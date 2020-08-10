import os
import subprocess
import threading
from json import load, dump
from time import sleep

# process names that gonna be tracked
constPythonTasksNames = {
	'PrinterServer': {
		'path': '/home/kerusey/PrinterServer/PrinterServer.py'
	}
}

constNodeTasksNames = {
	'DiscordCustomStatus': {
		'path': "/home/kerusey/discord-customstatus/DiscordCustomStatus.js"
	}
}
# process names that gonna be tracked
baseDir = os.path.dirname(os.path.abspath(__file__)) + "/"
config = load(open(baseDir + 'config.json'))

tasks = []
for item in config:
	if (item != 'token'):
		tasks.append(item)

def stopProcess(task):
	if (type(task) == dict):
		subprocess.run(['kill', str(task['pid'])])
	elif (type(task) == int):
		subprocess.run(['kill', str(task)])
	elif (type(task) == str):
		subprocess.run(['kill', task])

nodeHandler = [] # assiged to startNodeProcess def global list
def startNodeProcess(path):
	global nodeHandler
	nodeHandler.append(subprocess.Popen(['/usr/bin/node', path]).pid)

pyHandler = [] # assiged to startPyProcess def global list
def startPyProcess(path):
	global pyHandler
	pyHandler.append(subprocess.Popen(['python3', path]).pid)

def startProcess(task:dict):
	while (True):
		if (task['name'] in constPythonTasksNames):
			thread = threading.Thread(target = startPyProcess, 
									  args = (constPythonTasksNames[task['name']]['path'], ),
									  daemon = True)

		elif (task['name'] in constNodeTasksNames):
			thread = threading.Thread(target = startNodeProcess, 
									  args = (constNodeTasksNames[task['name']]['path'], ),
									  daemon = True)
		thread.run()
		
		sleep(1800)

		if (len(pyHandler)):
			stopProcess(pyHandler[0])
			pyHandler.clear()

		elif (len(nodeHandler)):
			stopProcess(nodeHandler[0])
			nodeHandler.clear()

def findNodeCommand(pids:list):
	response = []
	processes = subprocess.check_output(['ps', 'aux']).decode("utf-8").split('\n')
	for process in processes:
		for pid in pids:
			if (process.find(pid) != -1):			
				task = {
					'command': "/usr/bin/node" + process.split("node")[1],
					'pid': int(pid)
				}
				response.append(task)
	return response

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

def getLanguageProcesses(lang:str):
	try:
		pids = subprocess.check_output(['pidof', lang]).decode("utf-8")[:-1].split(' ')
	except Exception:
		return [] # Processes of this language are not running
	if (lang == 'python3'):
		pids.remove(str(os.getpid()))
	for id, pid in enumerate(pids):
		data = subprocess.check_output(['ps', '-p', pid]).decode("utf-8").split()[-1]
		if (data != lang):
			pids.pop(id)
	return findPythonCommand(pids) if lang == 'python3' else findNodeCommand(pids)

def editConfig(taskName:str, tasks:list):
	print(tasks)
	config[taskName]['status'] = False
	config[taskName]['pid'] = None
	for task in tasks:
		if (task['command'].find(taskName) != -1):
			config[taskName]['status'] = True
			config[taskName]['pid'] = task['pid']
	print(config)
	with open(baseDir + "config.json", 'w') as configFile:
		dump(config, configFile, indent=4)

def checkTask(taskName:str): # updates config.json
	if (taskName in constPythonTasksNames): # checks python pids
		editConfig(taskName, getLanguageProcesses("python3"))
	elif (taskName in constNodeTasksNames):
		editConfig(taskName, getLanguageProcesses("node"))
