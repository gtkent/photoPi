import logging

LOG_FILE_PATH = '/var/log/paperPi.log'

logger = logging.getLogger('main')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
)

file_handler = logging.FileHandler(LOG_FILE_PATH)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)