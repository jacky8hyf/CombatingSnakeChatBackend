import json
import traceback
class Message(object):
    commands = ['join', 'reconn', 'quit', 'start', 'u','l','d','r']

    def __init__(self, message_str):
        self.command = None
        self.data = None
        for command in Message.commands:
            if message_str.startswith(command):
                self.command = command
                try:
                    self.data = json.loads(message_str[len(command):].strip())
                except ValueError:
                    pass
                break

    @classmethod
    def from_str(cls, msgstr):
        if msgstr is None:
            return None
        return cls(msgstr)
