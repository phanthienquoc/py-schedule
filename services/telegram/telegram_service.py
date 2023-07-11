import os
import schedule
import threading
import time
from datetime import datetime
from dotenv import load_dotenv
import telegram
from telegram.ext import CommandHandler, MessageHandler, Filters, Updater
from croniter import croniter
load_dotenv()

# Define a class for the Telegram bot
class TelegramBot:

    def __init__(self):
        self.bot_token = os.getenv('BOT_TOKEN')
        self.bot = telegram.Bot(token=self.bot_token)
        self.updater = Updater(self.bot_token, use_context=True)
        self.dispatcher = self.updater.dispatcher
        
        # Add the /start handler to the bot
        start_handler = CommandHandler('start', self.handle_start)
        self.dispatcher.add_handler(start_handler)
        
        # Add the message handler to the bot
        message_handler = MessageHandler(Filters.text & ~Filters.command, self.handle_message)
        self.dispatcher.add_handler(message_handler)

    def start(self):
        # Start the bot
        self.updater.start_polling()
    
    def stop(self):
        # Stop the bot
        self.updater.stop()

    def send_message(self, chat_id, message):
        try:
            self.bot.send_message(chat_id=chat_id, text=message)
        except Exception as e:
            print("Error sending message:", e)
    
    def handle_start(self, update, context):
        user = update.message.from_user
        message = f"Hi {user.first_name}! Welcome to the bot."
        self.send_message(update.effective_chat.id, message)
    
    def handle_message(self, update, context):
        user = update.message.from_user
        message_text = update.message.text
        reply_message = f"Hi {user.first_name}, you said: {message_text}"
        self.send_message(update.effective_chat.id, reply_message)