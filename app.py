import flask 
import chanapi
from time import strftime
from threading import Timer
from os import environ

#Load config file
config = {}
if not 'SECRET_KEY' in environ:
	with open('config.ini', 'r') as file:
		for line in file.read().splitlines():
			line = line.split('==')
			config[line[0]] = line[1]
else:
	config['SECRET_KEY'] = environ['SECRET_KEY']

app = flask.Flask(__name__) #Initialize our application
app.secret_key = config['SECRET_KEY']

def getLatestCountryStats():
	with open('static/stats.txt', 'r') as statfile:
		time = statfile.readline().rstrip().split('-')
		return [time, statfile.read()]

def updateStats():
	print 'Updating stats...'
	chanapi.updateStatsOnBoard('pol')
	print 'Update complete!'
	Timer(1800, updateStats, ()).start()
Timer(5, updateStats, ()).start()

@app.route('/')
def index():
	fetch = getLatestCountryStats()
	return flask.render_template('index.html', countries=fetch[1], time=fetch[0])

if __name__ == '__main__':
	#app.debug = True #DONT FORGET
	app.run() #Run our app.