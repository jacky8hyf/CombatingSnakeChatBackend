from unittest import TestCase
from .test_utils import *

class SnakeGameExecutionTest(BaseTestCase):
    def setUp(self):
        self.redis = MockRedis()
        self.timeProvider = MockTimeProvider()
        self.logger = MockLogger()