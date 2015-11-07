import json
from combating_snake_settings import MAX_MEMBERS_IN_ROOM, GAME_TICK_TIME, BOARD_COLUMNS, BOARD_ROWS
from models.snake_game_models import Board
from models.invalid_input_error import InvalidInputError

class SnakeGameExecution(object):

    @classmethod
    def create(cls, *args, **kwargs):
        '''
        Create a RestInterface object. (Could be a mock)
        '''
        return cls(*args, **kwargs)

    def __init__(self, restInterface, roomManager, timeProvider, logger, *args, **kwargs):
        self.restInterface = restInterface
        self.roomManager = roomManager
        self.timeProvider = timeProvider
        self.logger = logger


    def error(self, message):
        return InvalidInputError(message).json()

    def prepare(self, roomId):
        # prepare the game
        if not roomId:
            self.logger.info('[GameLoop] No room id.')
            return None, None
        room = self.restInterface.get_room(roomId)
        members = room.get('members')
        creator = room.get('creator')
        if members is None or creator is None:
            self.logger.info('[GameLoop] no members or creator key')
            return None, None
        members.append(creator)
        membersDict = {}
        for member in members: membersDict[member['userId']] = member;
        memberIds = [member.get('userId') for member in members]
        if len(memberIds) > MAX_MEMBERS_IN_ROOM:
            self.roomManager.publish_to_room(roomId, self.error('Too many in the room, cannot start'))
            return None, None
        board = self.roomManager.get(roomId).board = Board(BOARD_COLUMNS, BOARD_ROWS, memberIds)
        board.initializeBoard()

        return board, membersDict

    def tickOnce(self, roomId, board, membersDict):
        '''
        Return True if the loop should be broken, False if the loop should continue
        '''
        board.moveAllSnakes()
        self.roomManager.publish_to_room(roomId, 'g', board.getGameState())
        snakes = board.snakes
        if len(snakes) <= 1:
            return snakes
        return None

    def start(self, roomId=None, *args, **kwargs):
        '''
        Prepare the game, notify everybody that the game starts, and
        Run the game loop until end.
        '''
        self.logger.info('[GameLoop] starting...')
        board, membersDict = self.prepare(roomId)
        if not board or not membersDict:
            self.logger.info('[GameLoop] prepare failed!')
            return

        # notify everybody: game starts here!
        self.roomManager.publish_to_room(roomId, 'start')

        self.logger.info('[GameLoop] looping...')
        # infinite game loop
        while True:
            self.logger.info('[GameLoop] tick')
            self.timeProvider.sleep(GAME_TICK_TIME)
            snakes = self.tickOnce(roomId, board, membersDict)
            if snakes is not None: # could be an empty list
                winner = snakes[0] if len(snakes) == 1 else None
                winner = membersDict.get(winner) if winner else None
                self.roomManager.publish_to_room(roomId, 'end', {
                    'winner': winner
                    } if winner else None)
                self.restInterface.ends_game(roomId)
                return snakes
