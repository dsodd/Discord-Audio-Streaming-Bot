import psutil

# Define a keyword to search for in the process (change "bot.py" if your script has a different name)
BOT_PROCESS_NAME = "bot.py"

# Iterate through all running processes
for process in psutil.process_iter(attrs=['pid', 'name', 'cmdline']):
    try:
        cmdline = process.info['cmdline']
        if cmdline and any(BOT_PROCESS_NAME in arg for arg in cmdline):
            print(f"Stopping bot process (PID: {process.info['pid']})...")
            process.terminate()  # Sends SIGTERM (graceful shutdown)
            print("Bot stopped successfully.")
            process.wait()  # Wait for it to fully terminate
            break
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        continue
