from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters

from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove

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
maxQuestions = 0

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
	global usersProgress

	username = update.effective_user.username
	if usersProgress.get(username) == None or usersProgress.get(username) == 0: 
		usersProgress[update.effective_user.username] = {}
		return 0
	else:
		return usersProgress[username]['currentStage']

def start(bot, update):
	global usersProgress

	currentStage = startInit(update)

	if currentStage == 0:
		usersProgress[update.effective_user.username]['currentStage'] = 0
		bot.send_message(chat_id=update.message.chat_id, text=jsonData['settings']['greeting'], reply_markup=ReplyKeyboardMarkup([['Yes']], resize_keyboard=True))

def progressRouter(bot, update):
	global usersProgress
	global maxQuestions

	currentUser = update.effective_user.username
	userMsg = update.message.text.lower().strip()

	if userMsg == "/start":
		return

	elif userMsg == "yes" and usersProgress[currentUser]['currentStage'] == 0: 

		bot.send_message(chat_id=update.message.chat_id, text=jsonData['settings']['begin'])

		usersProgress[currentUser]['currentStage'] = usersProgress[currentUser]['currentStage'] + 1

		custom_keyboard = [[i] for i in jsonData['questions']['question_' + str(usersProgress[currentUser]['currentStage'])]['answers'].values()]
		usersProgress[currentUser]['possibleAnswers'] = [i.lower().strip() for i in jsonData['questions']['question_' + str(usersProgress[currentUser]['currentStage'])]['answers'].values()]

		print(usersProgress)

		bot.send_message(
			chat_id=update.message.chat_id, 
			text=str(usersProgress[currentUser]['currentStage'])+ ') ' + jsonData['questions']['question_' + str(usersProgress[currentUser]['currentStage'])]['question']['full'], 
			reply_markup=ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=False)
		)

	elif usersProgress[currentUser]['currentStage'] == maxQuestions: 

		usersProgress[currentUser]['currentStage'] = usersProgress[currentUser]['currentStage'] + 1
		usersProgress[currentUser]['possibleAnswers'] = []
		bot.send_message(chat_id=update.message.chat_id, text=jsonData['settings']['thanks'], reply_markup=ReplyKeyboardRemove())
		bot.send_message(chat_id=update.message.chat_id, text=jsonData['settings']['farewell'])
		print(usersProgress)

	elif userMsg in usersProgress[currentUser]['possibleAnswers']:

		bot.send_message(chat_id=update.message.chat_id, text=jsonData['settings']['thanks'])

		usersProgress[currentUser]['currentStage'] = usersProgress[currentUser]['currentStage'] + 1

		custom_keyboard = [[i] for i in jsonData['questions']['question_' + str(usersProgress[currentUser]['currentStage'])]['answers'].values()]
		usersProgress[currentUser]['possibleAnswers'] = [i.lower().strip() for i in jsonData['questions']['question_' + str(usersProgress[currentUser]['currentStage'])]['answers'].values()]

		print(usersProgress)

		bot.send_message(
			chat_id=update.message.chat_id, 
			text=str(usersProgress[currentUser]['currentStage'])+ ') ' + jsonData['questions']['question_' + str(usersProgress[currentUser]['currentStage'])]['question']['full'], 
			reply_markup=ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=False)
		)

	elif usersProgress[currentUser]['currentStage'] == maxQuestions + 1: 
		bot.send_message(chat_id=update.message.chat_id, text=jsonData['settings']['stop'], reply_markup=ReplyKeyboardRemove())

	else:
		bot.send_message(chat_id=update.message.chat_id, text=jsonData['settings']['wrong'])


updater = Updater(token=config['DEFAULT']['API_KEY'])
def main():
	global jsonData
	global maxQuestions

	dispatcher = updater.dispatcher

	start_handler = CommandHandler('start', start)
	end_handler = CommandHandler('stop', stop, pass_args=True)
	progress_handler = MessageHandler(Filters.text, progressRouter)

	dispatcher.add_handler(start_handler)
	dispatcher.add_handler(end_handler)
	dispatcher.add_handler(progress_handler)

	with open("QA.json", "r") as read_file:
		jsonData = json.load(read_file)

	maxQuestions = len(jsonData['questions'])

	updater.start_polling()
	updater.idle()

if __name__ == '__main__':
	main()