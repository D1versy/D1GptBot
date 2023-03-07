import telegram
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
)
import openai
import os

# Set up your OpenAI API credentials
GPT_BOT_TOKEN = os.getenv("GPT_BOT_TOKEN")
openai.api_key = os.getenv("OPENAI_KEY")

def start_handler(update, context):
    update.message.reply_text("Hello! I'm a bot that can answer questions. Just send me a question and I'll do my best to answer it.\nMore details: /help")


def about_handler(update, context):
    update.message.reply_text("I am a software engineer. I develop software applications using a variety of programming languages, databases and frameworks. I develop applications for the web, desktop, mobile devices and other platforms. I also write code to integrate software applications with other systems and databases. Additionally, I troubleshoot software issues, optimize applications for performance and security, and provide technical support.")


def help_handler(update, context):
    update.message.reply_text('BOT Commands : /start , /about\n"Available D1 bots:\nhttps://t.me/D1VideoBot\nhttps://t.me/D1GptBot\nhttps://t.me/D1TikTokBot')


def answer_question(message, update, context):
    # Get the user's question from the message
    message = update.message
    status_msg = message.reply_text(message, "🚀 Processing ... \n it might take some time :)")

    question = message.text.strip()

    # Call the OpenAI API to get an answer
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Q: {question}\nA:",
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.7,
    )

    # Send the answer back to the user
    answer = response.choices[0].text.strip()
    status_msg.edit_text(message, answer)

def incoming_message_action(update, context):
    message = update.message
    context.dispatcher.run_async(answer_question, str(message.text), update, context)



def main() -> None:
    """Run the bot."""
    updater = Updater(GPT_BOT_TOKEN)
    dispatcher = updater.dispatcher

    # Commands Listning
    dispatcher.add_handler(CommandHandler('start', start_handler, run_async=True))
    dispatcher.add_handler(CommandHandler('about', about_handler, run_async=True))
    dispatcher.add_handler(CommandHandler('help', help_handler, run_async=True))

    # Message Incoming Action
    dispatcher.add_handler(MessageHandler(incoming_message_action,run_async=True))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()