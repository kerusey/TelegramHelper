import json
import telegram
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler

config = json.load(open('config.json'))
session = Updater(token = config['token'], use_context = True)

tasks = []
for item in config:
	if (item != 'token'):
		tasks.append(item)

def checkTask(taskName:str): # updates config.json
	return True 

def reloadConfig():
	config = json.load(open('config.json'))

def start(update, context):
	update.message.reply_text(text = "What task would you like to check?", reply_markup = telegram.ReplyKeyboardMarkup([[task] for task in tasks]))

def conversation(update, context):
	userReply = update.message.text
	if (userReply in config): # picking task
		checkTask(userReply)
		reloadConfig()
		plainText = None
		if (config[userReply]):
			plainText = userReply + " is already running!\nWould you like to restart this task?"
		else:
			plainText = userReply + " is not running!\nWould you like to start this task?"
		update.message.reply_text(text = plainText, reply_markup = telegram.ReplyKeyboardMarkup([["Yes"], ["No"]]))
	
	elif (userReply in ['Yes', 'No']):
		if (userReply == "No"):
			update.message.reply_text(text = "Have a wonderfoul day! =)", reply_markup = telegram.ReplyKeyboardRemove())
		else:
			## run task
			update.message.reply_text(text = "Yes", reply_markup = telegram.ReplyKeyboardRemove())

def help(update, context):
	update.message.reply_text("This is a telegram bot called CoffeeBreaker Web Server Helper.\nI am designed to help you to manage tasks that runs on your server.")

session.dispatcher.add_handler(CommandHandler('start', start))
session.dispatcher.add_handler(CommandHandler('help', help))
session.dispatcher.add_handler(MessageHandler(Filters.text, conversation))
session.start_polling()
session.idle()
exit()
