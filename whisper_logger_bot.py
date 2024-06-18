import os
import json
from telegram import Update, ParseMode
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, CallbackContext
from typing import Dict, List

# Define admin_id here with your specific Telegram chat ID
admin_id = 1336330730  # Telegram chat ID of the bot admin

# Global dictionary to store registered users
registered_users: Dict[int, List[int]] = {}  # {group_id: [user_id1, user_id2, ...]}
DATA_FILE = os.path.join(os.path.dirname(__file__), "registered_users.json")

# Load registered users from file if it exists
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as file:
        registered_users = json.load(file)

# Function to save registered users to file
def save_registered_users():
    with open(DATA_FILE, "w") as file:
        json.dump(registered_users, file)

# Function to log Whisper messages and forward them to registered users
def log_message(update: Update, context: CallbackContext) -> None:
    message = update.message.text
    user = update.message.from_user
    chat = update.message.chat
    
    if chat.type == 'private':
        # User registration
        if user.id == admin_id:
            group_id = int(message)
            if group_id not in registered_users:
                registered_users[group_id] = []
            context.bot.send_message(user.id, f"You are now registered to receive whispers from group {group_id}.")
            save_registered_users()
        else:
            context.bot.send_message(user.id, "You are not authorized to register groups.")

    elif chat.type in ['group', 'supergroup']:
        if is_whisper_message(message):  # Check if the message is a Whisper message
            for user_id in registered_users.get(chat.id, []):
                context.bot.send_message(user_id, f"Whisper in group {chat.id}:\n{message}", parse_mode=ParseMode.MARKDOWN)
            with open("message_log.txt", "a") as log_file:
                log_file.write(f"User: {user.username or user.id}, Whisper Message: {message}\n")

# Function to check if a message is a Whisper message (adjust this based on Whisper Bot's format)
def is_whisper_message(message: str) -> bool:
    return message.startswith("Whisper:")  # Adjust this condition based on Whisper Bot's message format

# Command to register for whispers
def register(update: Update, context: CallbackContext) -> None:
    if update.message.from_user.id == admin_id:
        update.message.reply_text("Send me the group ID you want to register (as a private message).")
    else:
        update.message.reply_text("You are not authorized to register groups.")

# Command to set the admin ID
def set_admin(update: Update, context: CallbackContext) -> None:
    global admin_id
    if admin_id is None:
        admin_id = update.message.from_user.id
        update.message.reply_text(f"Admin ID set to {admin_id}.")
    else:
        update.message.reply_text("Admin ID is already set.")

# Command to provide basic information about the bot
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Hi! I am Whisper Logger Bot. Use /register to register groups for whisper message forwarding.")

# Command to provide help information
def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Available commands:\n"
                              "/start - Start the bot\n"
                              "/help - Display this help message\n"
                              "/register - Register groups for whisper message forwarding (admin only)\n"
                              "/setadmin - Set admin ID for the bot (admin only)")

def main() -> None:
    # Replace 'YOUR_BOT_TOKEN' with your bot's token
    token = os.getenv("7480847710:AAGHZRkVHhbqGPxvHdPCtzLZxZKFZ7COd0Q")
    updater = Updater(token)

    dispatcher = updater.dispatcher

    # Handler to log Whisper messages
    dispatcher.add_handler(MessageHandler(Filters.text & Filters.group, log_message))

    # Command handlers
    dispatcher.add_handler(CommandHandler("register", register))
    dispatcher.add_handler(CommandHandler("setadmin", set_admin))
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT
    updater.idle()

    # Save registered users to file before exiting
    save_registered_users()

if __name__ == '__main__':
    main()
