import os
REDIS_URL = os.environ.get('REDISCLOUD_URL')
if not REDIS_URL:
    REDIS_URL = "redis://localhost"
REDIS_CHAN = 'chat'
DEBUG = 'DEBUG' in os.environ
MASTER_KEY = os.environ.get('MASTER_KEY')
if not MASTER_KEY:
    MASTER_KEY = "fake_master_key"
REST_HOST = os.environ.get('REST_HOST')
if not REST_HOST:
    REST_HOST = "http://localhost:8080"