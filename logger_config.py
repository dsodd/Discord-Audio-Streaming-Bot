import logging
import os

# Ensure the 'logs' directory exists
log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)

# Use a fixed log filename for logging within the 'logs' directory
log_filename = os.path.join(log_dir, 'logs\latest_log.log')

# Use a fixed log filename for logging
log_filename = 'logs\latest_log.log'

# Create the logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create a file handler to log to the 'latest_log.log'
file_handler = logging.FileHandler(log_filename)
file_handler.setLevel(logging.INFO)

# Create a console handler to log to the console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Define the log format
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')

# Set the formatter for both handlers
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add both handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)
