from unittest import TestCase
from message import Message
class MessageTestCase(TestCase):
    def testCreate(self):
        m = Message.create("command", "data")
        self.assertEquals("command", m.command)
        self.assertEquals("data", m.data)

    def testFromStr(self):
        m = Message.from_str('join {"key":"value"}')
        self.assertEquals("join", m.command)
        self.assertEquals({"key":"value"}, m.data)