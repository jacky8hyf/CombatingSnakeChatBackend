import json
import traceback
class Message(object):
    commands = ['join', 'reconn', 'quit', 'start', 'u','l','d','r']

    def __init__(self, command = None, data = None):
        self.command = command
        self.data = data

    @classmethod
    def from_str(cls, message_str):
        if message_str is None:
            return None
        msg = cls()
        for command in Message.commands:
            if message_str.startswith(command):
                msg.command = command
                try:
                    msg.data = json.loads(message_str[len(command):].strip())
                except ValueError:
                    pass
                break
        return msg

    @classmethod
    def create(cls, command = None, data = None):
        return cls(command, data)
