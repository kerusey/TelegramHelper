import os
import subprocess
import json

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

config = json.load(open('config.json'))

tasks = []
for item in config:
	if (item != 'token'):
		tasks.append(item)

def startProcess(task:dict):
	if (task['name'] in constPythonTasksNames):
		subprocess.run(['python3', constPythonTasksNames[task['name']]['path']])
	if (task['name'] in constNodeTasksNames):
		subprocess.run(['/usr/bin/node', constNodeTasksNames[task['name']]['path']])

def stopProcess(task:dict):
	subprocess.run(['kill', str(task['pid'])])

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
	with open("config.json", 'w') as configFile:
		json.dump(config, configFile, indent=4)

def checkTask(taskName:str): # updates config.json
	if (taskName in constPythonTasksNames): # checks python pids
		editConfig(taskName, getLanguageProcesses("python3"))
	elif (taskName in constNodeTasksNames):
		editConfig(taskName, getLanguageProcesses("node"))
