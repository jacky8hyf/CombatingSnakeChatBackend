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

    ### game loop
    def gameloop(self, roomId=None, *args, **kwargs):

        error = lambda message: InvalidInputError(message).json()

        # prepare the game
        if not roomId:
            self.logger.info('[GameLoop] No room id.')
            return
        room = self.restInterface.get_room(roomId)
        members = room.get('members')
        creator = room.get('creator')
        if not members or not creator:
            self.logger.info('[GameLoop] no members or creator key')
            return
        members.append(creator)
        membersDict = {}
        for member in members: membersDict[member['userId']] = member;
        memberIds = [member.get('userId') for member in members]
        if len(memberIds) > MAX_MEMBERS_IN_ROOM:
            self.roomManager.publish_to_room(roomId, error('Too many in the room, cannot start'))
            return
        board = self.roomManager.get(roomId).board = Board(BOARD_COLUMNS, BOARD_ROWS, memberIds)

        # notify everybody: game starts here!
        self.roomManager.publish_to_room(roomId, 'start')

        # infinite game loop
        while True:
            self.timeProvider.sleep(GAME_TICK_TIME)
            board.moveAllSnakes()
            self.roomManager.publish_to_room(roomId, 'g', board.getGameState())
            snakes = board.snakes
            if len(snakes) <= 1:
                winner = snakes[0] if len(snakes) == 1 else None
                winner = membersDict.get(winner) if winner else None
                self.roomManager.publish_to_room(roomId, 'end', {
                    'winner': winner
                    } if winner else None)
                break;