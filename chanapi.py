import urllib2
import time
import operator
from time import strftime

false = False #JSON Compatibility
true = True
hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
	'Accept-Encoding': 'none',
	'Accept-Language': 'en-US,en;q=0.8',
	'Connection': 'keep-alive'}

def saveStats(stats):
	sortedStats = sorted(stats.items(), key=operator.itemgetter(1))
	sortedStats.reverse()
	with open('static/stats.txt', 'w') as statfile:
		statfile.write(strftime("%Y-%m-%d-%H-%M-%S") + '\n')
		for n in sortedStats:
			statfile.write( "[\'" + str(n[0]) + "\', " + str(n[1]) + "],\n" )

def getBoardThreads(board):
	url = 'http://a.4cdn.org/%s/threads.json' % board
	req = urllib2.Request(url, headers=hdr)
	u = urllib2.urlopen(req)

	threads = []
	mainJSON = eval(u.read())
	#First is a list []
	#Inside the list there are dicts {}
	#In the dics are stored the page and a list
	#named threads
	#Inside that list there are multiple dicts with 
	#the thread information
	#[{[{}]}]

	for page in mainJSON:
		for thread in page['threads']:
			threads.append(thread['no'])
	return threads

def countUniqueBoardCountries(board):
	threads = getBoardThreads(board)
	uniquePersonalities = []
	uniqueCountries = {}
	for thread in threads:
		url = 'http://a.4cdn.org/%s/thread/%s.json' % (board, str(thread))
		req = urllib2.Request(url, headers=hdr)
		u = urllib2.urlopen(req)

		mainJSON = eval(u.read())
		#Returns a dictionary with key 'posts'. Inside, a list with dictionaries of posts
		#Inside each post, post stats.
		for post in mainJSON['posts']:
			try:
				if not post['id'] in uniquePersonalities:
					uniquePersonalities.append(post['id'])
					if post['country_name'] in uniqueCountries:
						uniqueCountries[post['country_name']] += 1
					else:
						uniqueCountries[post['country_name']] = 1
			except KeyError:
				pass
		time.sleep(0.1)
	return uniqueCountries

def updateStatsOnBoard(board):
	saveStats(countUniqueBoardCountries(board))

if __name__ == '__main__':
	updateStatsOnBoard('pol')