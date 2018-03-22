import logging
import sys

log_filepath = 'log.txt'
logger = logging.getLogger('netCrawler')
logger.setLevel(logging.INFO)
handler1 = logging.FileHandler(log_filepath)
handler2 = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - [%(filename)s:%(lineno)s-%(funcName)s()] - %(levelname)s - %(message)s')
handler1.setFormatter(formatter)
handler2.setFormatter(formatter)
logger.addHandler(handler1)
logger.addHandler(handler2)

def setup_logger():
	return logger
