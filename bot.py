"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import os
import logging
import urllib
import youtube_dl

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from config import TOKEN


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def video_id(value):
    query = urllib.parse.urlparse(value)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            p = urllib.parse.parse_qs(query.query)
            return p['v'][0]
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]
    # fail?
    return None

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Привіт! \n\nЯ бот для завантаження музики з YouTube! \n\nНадішли мені посилання на пісню, яку ти хочеш завантажити.')


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Аби завантажити пісню, надішли мені посилання на неї.')

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def download(update, context):
    """Download the audio from YouTube."""

    URL = update.message.text

    id = video_id(URL)

    if id == None:
        update.message.reply_text('На жаль, я не можу знайти твою пісню. \n\nБудь ласка, перевір посилання.')
    else:
        if not os.path.isfile("files/{filename}.mp3".format(filename=id)):
            update.message.reply_text("На жаль, твоєї пісні немає в базі даних. \n\nЗачекай, будь ласка, поки я її завантажу.")

            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': "files/{filename}.%(ext)s".format(filename=id),
                'ffmpeg_location': "ffmpeg/"
            }

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([URL])
        else:
            update.message.reply_text("Я знайшов твою пісню в базі даних. \n\nЗараз я її швиденько завантажу.")

        f = open("files/{filename}.mp3".format(filename=id), mode="rb")
        update.message.reply_audio(f)
        f.close()

def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, download))

     # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()