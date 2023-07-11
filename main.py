import os
import time
import signal
import schedule
import threading
from datetime import datetime
from dotenv import load_dotenv
from services.telegram.telegram_service import TelegramBot

# Create an instance of the TelegramBot class
telegram_bot = TelegramBot()

# Define a global exit flag to signal the threads to exit
global_exit_flag = threading.Event()

# Start the Telegram bot in a separate thread
telegram_thread = threading.Thread(target=telegram_bot.start)
telegram_thread.start()

# Define a function to stop the threads
def stop_threads():
    global_exit_flag.set()
    telegram_bot.stop()
    telegram_thread.join()

# Register the stop_threads function to be called on SIGINT or SIGTERM
signal.signal(signal.SIGINT, lambda signum, frame: stop_threads())
signal.signal(signal.SIGTERM, lambda signum, frame: stop_threads())

# Wait for the threads to finish
telegram_thread.join()