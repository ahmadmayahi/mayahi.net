import logging
import os
from logging.handlers import TimedRotatingFileHandler

log_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'var', 'logs', 'app.log'))

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler = TimedRotatingFileHandler(log_path, when="midnight", interval=1)
handler.setFormatter(formatter)
logging.basicConfig(level=logging.DEBUG, filename=log_path)
logger = logging.getLogger()
logger.addHandler(handler)
