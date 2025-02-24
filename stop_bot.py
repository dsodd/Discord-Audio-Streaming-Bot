import psutil
import os
from logger_config import logger
from datetime import datetime
import time

BOT_SCRIPT_NAME = "bot.py"
LOGS_DIR = "logs"
LATEST_LOG_FILE = os.path.join(LOGS_DIR, "latest_log.log")

def stop_bot():
    bot_found = False
    self_pid = os.getpid()  # Get our own PID so we don’t kill ourselves

    for process in psutil.process_iter(attrs=['pid', 'name', 'cmdline']):
        try:
            pid = process.info['pid']
            cmdline = process.info['cmdline']
            process_name = process.info['name']

            if pid == self_pid:
                continue  # Skip ourselves

            if cmdline:
                logger.info(f"Checking process PID {pid}: {' '.join(cmdline)}")

                # Detect bot.py running as "python bot.py" or a direct script execution
                if any(BOT_SCRIPT_NAME in arg for arg in cmdline):
                    bot_found = True
                    logger.info(f"Stopping bot process (PID: {pid})...")

                    process.terminate()
                    try:
                        process.wait(timeout=5)
                        logger.info(f"Process {pid} terminated successfully.")
                    except psutil.TimeoutExpired:
                        logger.warning(f"Process {pid} did not terminate, forcing kill...")
                        process.kill()
                        logger.info(f"Process {pid} killed.")

                    return True  # Exit after stopping one instance

        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logger.error(f"Error accessing process {pid}: {e}")

    if not bot_found:
        logger.error(f"No process found running {BOT_SCRIPT_NAME}.")
    return False

if stop_bot():
    time.sleep(1)

    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    new_log_filename = os.path.join(LOGS_DIR, f"log_{current_time}.log")

    logger.info(f"Renaming log file to: {new_log_filename}")

    

    time.sleep(1)

    if os.path.exists(LATEST_LOG_FILE):
        try:
            logger.info(f"Log file renamed to: {new_log_filename}")
            for handler in logger.handlers:
                handler.flush()
                handler.close()
            os.rename(LATEST_LOG_FILE, new_log_filename)

            print(f"Log file renamed to: {new_log_filename}")
        except Exception as e:
            logger.error(f"Error renaming log file: {e}")
            print(f"Error renaming log file: {e}")
    else:
        logger.warning(f"{LATEST_LOG_FILE} does not exist.")
        print(f"{LATEST_LOG_FILE} does not exist.")
else:
    logger.error("Bot process could not be stopped.")
    print("Bot process could not be stopped.")

exit()
