import json as json_module
class InvalidInputError(Exception):
    def __init__(self, message):
        self.message = message
    def json(self):
        return json_module.dumps({"msg": self.message})