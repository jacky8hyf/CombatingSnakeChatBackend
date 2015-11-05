class RestInterface(object):
    ### FIXME RestInterface
    @staticmethod
    def authenticate_user(userId, ts, auth):
        '''
        Return true if the user should be authenticated, false otherwise.
        '''
        return True

    @staticmethod
    def join_and_get_room(roomId, userId):
        '''
        Put user in the room and return the new room data (a dictionary)
        '''
        return {}

    @staticmethod
    def exit_and_get_room(roomId, userId):
        '''
        Kick user out of the room and return the new room data (a dictionary)
        '''
        return {}

    @staticmethod
    def start_room_if_created_by(roomId, userId):
        '''
        Start the game in the room and return true iff room exists and is
        created by user. Return false otherwise.
        '''
        return True