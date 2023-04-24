import logging
import os
import time
from datetime import datetime, timedelta

import openai
import telegram
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters
)

# Set up your OpenAI API credentials
GPT_BOT_TOKEN = os.getenv("GPT_BOT_TOKEN")
openai.api_key = os.getenv("OPENAI_KEY")

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


class UserHistory:
    def __init__(self, user_id):
        self.user_id = user_id
        self.history = []
        self.last_interaction = datetime.now()

    def add_message(self, sender, message):
        self.history.append({"sender": sender, "message": message})
        self.last_interaction = datetime.now()

    def get_conversation(self):
        return [message["message"] for message in self.history]

    def is_expired(self, expiration_time=10):
        return datetime.now() - self.last_interaction > timedelta(minutes=expiration_time)


user_histories = {}


def start_handler(update, context):
    update.message.reply_text(
        "Hello! I'm a bot that can answer questions. Just send me a question and I'll do my best to answer it.\nMore details: /help")


def about_handler(update, context):
    update.message.reply_text(
        "I am a software engineer. I develop software applications using a variety of programming languages, databases and frameworks. I develop applications for the web, desktop, mobile devices and other platforms. I also write code to integrate software applications with other systems and databases. Additionally, I troubleshoot software issues, optimize applications for performance and security, and provide technical support.")


def help_handler(update, context):
    update.message.reply_text(
        'BOT Commands : /start , /about\nAvailable D1 bots:\nhttps://t.me/D1VideoBot\nhttps://t.me/D1GptBot\nhttps://t.me/D1TikTokBot')


def chat_gpt_request(prompt, max_tokens=1024):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=max_tokens,
        n=1,
        stop=None,
        temperature=0.7,
    )
    return response.choices[0].text.strip()


def handle_user_message(user_id, message, user_histories):
    if user_id not in user_histories or user_histories[user_id].is_expired():
        user_histories[user_id] = UserHistory(user_id)

    user_history = user_histories[user_id]

    user_history.add_message("user", message)

    conversation = "\n".join(user_history.get_conversation())
    prompt = f"{conversation}\nbot:"

    response = chat_gpt_request(prompt)
    user_history.add_message("bot", response)
    return response

def log_unique_user_id(user_id, log_file='Users.log'):
    unique_user_ids = set()

    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            for line in f.readlines():
                line = line.strip()
                if line:
                    unique_user_ids.add(int(line))

    if user_id not in unique_user_ids:
        unique_user_ids.add(user_id)
        with open(log_file, 'a') as f:
            f.write(f"{user_id}\n")


def answer_question(update, context):
    message = update.message
    user_id = message.from_user.id
    username = message.from_user.username
    user_message = message.text.strip()
    log_unique_user_id(user_id)

    # Use username if available, otherwise use user_id as a filename
    filename = f'{username, user_id or user_id}.txt'
    filepath = os.path.join('./logs', filename)

    # Create 'logs' directory if it doesn't exist
    os.makedirs('./logs', exist_ok=True)

    with open(filepath, "a+", encoding='utf-8') as file:
        file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {username or user_id} => {message.text}")
        file.write("\n")

    context.bot.send_chat_action(chat_id=update.effective_chat.id, action=telegram.ChatAction.TYPING)

    try:
        response = handle_user_message(user_id, user_message, user_histories)
        update.message.reply_text(response)

        # Save the bot's response to the file
        with open(filepath, "a+", encoding='utf-8') as file:
            file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - BOT => {response}")
            file.write("\n")

    except Exception as ex:
        print(ex)
        update.message.reply_text(
            "Due to a high volume of requests, I'm currently experiencing a heavy load, which may cause delays in my responses. I apologize for any inconvenience this may cause.\nPlease try again later.")


def main() -> None:
    """Run the bot."""

    updater = Updater(GPT_BOT_TOKEN)
    dispatcher = updater.dispatcher

    # Commands Listening
    dispatcher.add_handler(CommandHandler('start', start_handler, run_async=True))
    dispatcher.add_handler(CommandHandler('about', about_handler, run_async=True))
    dispatcher.add_handler(CommandHandler('help', help_handler, run_async=True))

    # Message Incoming Action
    dispatcher.add_handler(MessageHandler(Filters.text, answer_question))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()