import json

class Files:
	def __init__(self,settingsFile,logFile):
		self.settingsFile = settingsFile
		self.logFile = logFile

	def get_settings(self):
		file = open(self.settingsFile, 'r')
		settings = json.loads(file.read())
		file.close()
		return settings