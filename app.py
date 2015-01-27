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
	config['PASSWORD'] = environ['PASSWORD']

app = flask.Flask(__name__) #Initialize our application
app.secret_key = config['SECRET_KEY']

def getLatestCountryStats():
	output = []
	with open('static/stats.txt', 'r') as statfile:
		output.append(statfile.readline().rstrip().split())
		output.append(statfile.read())
	with open('static/24hour.txt', 'r') as hourperiod:
		timeline = []
		dates = []
		for line in hourperiod.read().splitlines():
			lineData = eval(line)
			if not lineData[0] in dates:
				timeline.append(lineData)
				dates.append(lineData[0])
		if len(timeline) > 48:
			output.append(timeline[-48:])
		else:
			output.append(timeline)
	with open('static/words.txt', 'r') as statfile:
		output.append(statfile.read())

	with open('static/polwords.txt', 'r') as statfile:
		output.append([statfile.readline().rstrip(),statfile.read()])
	return output

def makeLineChart(data):
	# data - [['date', {'US':412, 'UK': 4124}], ['date', {'US':745, 'UK': 412}]]
	finalString = "[['Date', 'United States', 'United Kingdom', 'Australia', 'Germany', 'Canada'],\n"
	for hour in data:
		finalString += "['%s', %s, %s, %s, %s, %s]" % (hour[0], hour[1]['United States'], hour[1]['United Kingdom'], hour[1]['Australia'], hour[1]['Germany'], hour[1]['Canada'])
		finalString += ',\n'
	finalString += ']'
	return finalString

def updateStats():
	print 'Updating stats...'
	chanapi.updateStatsOnBoard('pol')
	print 'Update complete!'
	Timer(1800, updateStats, ()).start()
Timer(5, updateStats, ()).start()

@app.route('/')
def index():
	fetch = getLatestCountryStats()
	linechart = makeLineChart(fetch[2])
	return flask.render_template('index.html', countries=fetch[1], time=fetch[0], linechart=linechart, words=fetch[3], polwords=fetch[4])

@app.route('/admin', methods=['GET', 'POST'])
def admin():
	if flask.request.method == 'POST':
		userinput = flask.request.form['mainarea']
		userpassword = flask.request.form['pass']
		if userpassword == config['PASSWORD']:
			with open('static/24hour.txt', 'w') as placementFile:
				placementFile.write(userinput)
				return flask.redirect(flask.url_for('admin'))
	else:
		with open('static/24hour.txt', 'r') as placementFile:
			return flask.render_template('admin.html', textarea=placementFile.read())
if __name__ == '__main__':
	#app.debug = True #DONT FORGET
	app.run() #Run our app.