# utils/logger_config.py

import logging
from logging.handlers import RotatingFileHandler
import os

# --- Centralized Logger Configuration ---

# 1. Create a logger instance
log = logging.getLogger('tool_logger')
log.setLevel(logging.INFO)

# 2. Define the log format
formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - [%(module)s:%(lineno)d] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# 3. Create a file handler that rotates logs
log_file = 'tool.log'
handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=5)
handler.setFormatter(formatter)

# 4. Add the handler to the logger
if not log.handlers:
    log.addHandler(handler)