from telegram import Bot
from telegram.error import TelegramError
import os


# Replace with your own bot token
GPT_BOT_TOKEN = os.getenv("GPT_BOT_TOKEN")

# Message to send to all users
message_text = ""

def read_user_ids(file_path):
    with open(file_path, 'r') as file:
        user_ids = [int(line.strip()) for line in file.readlines()]
    return user_ids

def notify_all_users(bot, user_ids, message_text):
    for user_id in user_ids:
        try:
            bot.send_message(chat_id=user_id, text=message_text)
            print(f"Message sent successfully to user {user_id}!")
        except TelegramError as error:
            print(f"Error sending message to user {user_id}: {error.message}")

# Create a bot instance
bot = Bot(token=GPT_BOT_TOKEN)

# Read user IDs from Users.log
user_ids = read_user_ids("Users.log")

# Send message to all users
notify_all_users(bot, user_ids, message_text)
