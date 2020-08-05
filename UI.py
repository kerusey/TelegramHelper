import ProcessHandler as Handler
import threading
import json
import telegram
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler

config = json.load(open('config.json'))
session = Updater(token = config['token'], use_context = True)

tasks = []
for item in config:
	if (item != 'token'):
		tasks.append(item)

def reloadConfig():
	global config
	config = json.load(open('config.json'))

def start(update, context):
	update.message.reply_text(text = "What task would you like to check?", reply_markup = telegram.ReplyKeyboardMarkup([[task] for task in tasks]))

task = { # global variable assigned to conversation func, related to the specific task required from user
	'name': None, # task name 
	'action': None, # what to do (start/restart)
	'pid': None # required to stop process fastly in restart method
}

def conversation(update, context):
	userReply = update.message.text
	global task
	if (userReply in config): # picking task
		Handler.checkTask(userReply) # updates config file with new info 'bout processes
		reloadConfig()
		plainText = None
		if (config[userReply]['status']):
			plainText = userReply + " is already running!\nWould you like to restart this task?"
			task['action'] = 'restart'
			task['pid'] = config[userReply]['pid']
		else:
			plainText = userReply + " is not running!\nWould you like to start this task?"
			task['action'] = 'start'
		task['name'] = userReply
		update.message.reply_text(text = plainText, reply_markup = telegram.ReplyKeyboardMarkup([["Yes"], ["No"]]))
	
	elif (userReply in ['Yes', 'No']):
		if (userReply == "No"):
			update.message.reply_text(text = "Have a wonderfoul day! =)", reply_markup = telegram.ReplyKeyboardRemove())
		else:
			if (task['action'] == 'restart'):
				Handler.stopProcess(task)
			processThread = threading.Thread(target = Handler.startProcess, args = (task,))
			processThread.start()
			update.message.reply_text(text = "Task has been successfully " + task['action'] + "ed", reply_markup = telegram.ReplyKeyboardRemove())

def help(update, context):
	update.message.reply_text("This is a telegram bot called CoffeeBreaker Web Server Helper.\nI am designed to help you to manage tasks that runs on your server.")

session.dispatcher.add_handler(CommandHandler('start', start))
session.dispatcher.add_handler(CommandHandler('help', help))
session.dispatcher.add_handler(MessageHandler(Filters.text, conversation))
session.start_polling()
session.idle()
exit()