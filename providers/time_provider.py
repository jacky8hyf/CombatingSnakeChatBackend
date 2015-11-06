import time as os_time

class TimeProvider(object):

    @classmethod
    def create(cls, *args, **kwargs):
        '''
        Create a TimeProvider object. (Could be a mock)
        '''
        return cls(*args, **kwargs)

    def time(self):
        return os_time.time()

    def sleep(self, secs):
        os_time.sleep(secs)