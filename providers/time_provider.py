import time as os_time

class TimeProvider(object):
    def time(self):
        return os_time.time()

    def sleep(self, secs):
        os_time.sleep(secs)