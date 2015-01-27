import urllib2
import time
import operator
from time import strftime
from flask import Markup
from copy import deepcopy

false = False #JSON Compatibility
true = True
hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
	'Accept-Encoding': 'none',
	'Accept-Language': 'en-US,en;q=0.8',
	'Connection': 'keep-alive'}

def saveStats(stats):
	sortedStats = sorted(stats[0].items(), key=operator.itemgetter(1))
	sortedStats.reverse()
	currentDate = strftime("%d/%m/%Y %H:%M")
	with open('static/stats.txt', 'w') as statfile:
		statfile.write(currentDate + '\n')
		for n in sortedStats:
			country = "".join(str(n[0]).split("'"))
			times = str(n[1])
			statfile.write( '[\"%s\", %s],\n' % (country, times) )
	with open('static/24hour.txt', 'a') as hourperiod:
		listOut = []
		listOut.append(currentDate)
		listOut.append({
						"United States":stats[0]['United States'],
						"United Kingdom":stats[0]['United Kingdom'],
						"Canada":stats[0]['Canada'],
						"Australia":stats[0]['Australia'],
						"Germany":stats[0]['Germany'],
						})
		hourperiod.write(str(listOut) + '\n')

	with open('static/words.txt', 'w') as wordlist:
		for pair in stats[1]:
			country = "".join(str(pair).split("'"))
			wordlist.write( "[\'%s\', \'%s\' ],\n" % (country, stats[1][pair]) )

	with open('static/polwords.txt', 'w') as wordlist:
		wordlist.write(str(stats[2][0]) + '\n')
		for n, pair in enumerate(stats[2][1]):
			wordlist.write("data.setValue(%i, 0, '%s');\n" % (n, pair))
			wordlist.write("data.setValue(%i, 1, '%s');\n" % (n, stats[2][1][pair]))

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
	uniquePersonalities = [] #IDs
	uniqueCountries = {}

	shitposts = {} # {"Country":['ops a fag', 'lyl']}
	fullShitpostList = []
	for thread in threads:
		url = 'http://a.4cdn.org/%s/thread/%s.json' % (board, str(thread))
		req = urllib2.Request(url, headers=hdr)
		u = urllib2.urlopen(req)

		mainJSON = eval(u.read())
		#Returns a dictionary with key 'posts'. Inside, a list with dictionaries of posts
		#Inside each post, post stats.
		for post in mainJSON['posts']:
			try:
				shitp = Markup(post['com']).striptags()
				shitp = "".join(shitp.split("\'"))
				fullShitpostList.append(shitp)
				if post['country_name'] in shitposts:
					shitposts[post['country_name']].append(shitp)
				else:
					shitposts[post['country_name']] = [shitp]
			except KeyError: #Empty post
				pass
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
	return [uniqueCountries, shitposts, fullShitpostList]

def generateWordCloud(data):
	size = len(data)
	wordList = {}
	for post in data:
			post = post.split()
			for word in post:
				boringWords = ['about', 'people', 'their', 'still', 'would', 'there', 'because', 'never', 'believe', 'never', 'least']
				if len(word) >= 5 and not word in boringWords: #boring words
					if word in wordList:
						wordList[word] += 1
					else:
						wordList[word] = 1
	cloneDict = deepcopy(wordList)
	for word in cloneDict:
		if cloneDict[word] <= 40:
			wordList.pop(word, None)
	cloneDict = None
	return [size,wordList]

def getMostUsedWord(shitposts):
	mostUsed = {}
	for country in shitposts:
		wordList = {}
		for post in shitposts[country]:
			post = post.split()
			for word in post:
				boringWords = ['about', 'people', 'their', 'still', 'would', 'there', 'because', 'never', 'believe', 'never', 'least']
				if len(word) >= 5 and not word in boringWords: #boring words
					if word in wordList:
						wordList[word] += 1
					else:
						wordList[word] = 1
		mostUsed[country] = max(wordList.iteritems(), key=operator.itemgetter(1))[0]
	return mostUsed

def updateStatsOnBoard(board):
	getData = countUniqueBoardCountries(board)
	fileInput = [getData[0]]
	fileInput.append(getMostUsedWord(getData[1]))
	fileInput.append(generateWordCloud(getData[2]))
	saveStats(fileInput)