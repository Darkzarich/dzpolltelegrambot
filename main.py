from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram import ReplyKeyboardMarkup
from telegram import KeyboardButton

import configparser
import logging
import threading

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

config = configparser.ConfigParser()
config.read('config.ini')

def shutdown():
	updater.stop()
	updater.is_idle = False

def stop(bot, update, args):
	if "".join(args) == config['DEFAULT']['SHUTDOWN_KEY']:
		bot.send_message(chat_id=update.message.chat_id, text="right code")
		threading.Thread(target=shutdown).start()
	else:
		bot.send_message(chat_id=update.message.chat_id, text="wrong code")

def start(bot, update):
	b1 = KeyboardButton("yes")
	b2 = KeyboardButton("no")
	bot.send_message(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!", reply_markup=ReplyKeyboardMarkup([[b1, b2]], resize_keyboard=False))

updater = Updater(token=config['DEFAULT']['API_KEY'])
def main():
	dispatcher = updater.dispatcher

	start_handler = CommandHandler('start', start)
	end_handler = CommandHandler('stop', stop, pass_args=True)

	dispatcher.add_handler(start_handler)
	dispatcher.add_handler(end_handler)

	updater.start_polling()
	updater.idle()

if __name__ == '__main__':
	main()