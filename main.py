from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram import ReplyKeyboardMarkup
from telegram import KeyboardButton

import configparser
import logging
import threading
import json


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

config = configparser.ConfigParser()
config.read('config.ini')

usersProgress = {}
jsonData = {}

def shutdown():
	updater.stop()
	updater.is_idle = False

def stop(bot, update, args):
	if "".join(args) == config['DEFAULT']['SHUTDOWN_KEY']:
		bot.send_message(chat_id=update.message.chat_id, text="right code")
		threading.Thread(target=shutdown).start()
	else:
		bot.send_message(chat_id=update.message.chat_id, text="wrong code")

def startInit(update):
	username = update.effective_user.username
	if usersProgress.get(username) == None or usersProgress.get(username) == 0: 
		usersProgress[update.effective_user.username] = 0
		return 0
	else:
		return usersProgress.get(username)

def start(bot, update):

	currentStage = startInit(update)
	j = 1 # iterator for questions

	for key, value in jsonData['questions'].items():
		custom_keyboard = [[i] for i in jsonData['questions']['question_' + str(j)]['answers'].values()]
		bot.send_message(
				chat_id=update.message.chat_id, 
				text=str(j)+ ') ' + jsonData['questions']['question_' + str(j)]['question']['full'], 
				reply_markup=ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=False)
		)
		j += 1

	print(usersProgress)

updater = Updater(token=config['DEFAULT']['API_KEY'])
def main():
	global jsonData

	dispatcher = updater.dispatcher

	start_handler = CommandHandler('start', start)
	end_handler = CommandHandler('stop', stop, pass_args=True)

	dispatcher.add_handler(start_handler)
	dispatcher.add_handler(end_handler)

	with open("QA.json", "r") as read_file:
		jsonData = json.load(read_file)

	updater.start_polling()
	updater.idle()

if __name__ == '__main__':
	main()