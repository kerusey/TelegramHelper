import os
import subprocess
import json
import telegram
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler

config = json.load(open('config.json'))
session = Updater(token = config['token'], use_context = True)

constPythonTasksNames = ['PrinterServer']
tasks = []
for item in config:
	if (item != 'token'):
		tasks.append(item)

def findNodeCommand(pids:list):
	pass

def findPythonCommand(pids:list):
	response = []
	processes = subprocess.check_output(['ps', 'aux']).decode("utf-8").split('\n')
	for process in processes:
		for pid in pids:
			if (process.find(pid) != -1):
				try:
					task = {
						'command': 'python3' + process.split('python3')[1],
						'pid': int(pid)
					}
				except Exception:
					continue
				if (task['command'] != 'python3 /usr/bin/networkd-dispatcher --run-startup-triggers'):
					response.append(task)
	return response

def getLanguagePids(lang:str):
	pids = subprocess.check_output(['pidof', lang]).decode("utf-8")[:-1].split(' ')
	pids.remove(str(os.getpid()))
	for id, pid in enumerate(pids):
		data = subprocess.check_output(['ps', '-p', pid]).decode("utf-8").split()[-1]
		if (data != lang):
			pids.pop(id)
	return findPythonCommand(pids) if lang == 'python3' else findNodeCommand(pids)

def checkTask(taskName:str): # updates config.json
	if (taskName in constPythonTasksNames): # checks python pids
		pythonTasks = getLanguagePids("python3")
		config[taskName] = False
		for task in pythonTasks:
			if (task['command'].find(taskName) != -1):
				config[taskName] = True
		print(config)
		with open("config.json", 'w') as configFile:
			json.dump(config, configFile, indent=4)
	elif (taskName in constNodeTasksNames):
		pass
	
print(checkTask("PrinterServer"))