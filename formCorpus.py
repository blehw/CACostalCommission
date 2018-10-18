import csv
import sys
from nltk.corpus import stopwords
from stemming.porter2 import stem
import re

csv.field_size_limit(sys.maxsize)
stopwords = stopwords.words('english')

inputFile = 'all_data_w_paragraphs_public_access.csv'

# since the file is so large, this indicates how many lines we want to read
lineNum = 1000
documentColNum = 0
startYear = 1996
endYear = 2016
yearColNum = 2

doneYears = []
#years = [1998, 2000, 2002, 2004, 2011, 2016]
regex = re.compile('[^a-zA-Z]')

with open(inputFile, encoding='ISO-8859-1') as csvFile:

	#for n in range(startYear, endYear + 1, 10):
	for n in range(startYear, endYear + 1):

		if n not in doneYears:

			d = {}
			badWords = []

			print(n)

			csvFile.seek(0)
			reader = csv.reader(csvFile)

			for row in reader:
				# if (reader.line_num < lineNum):
				if row[yearColNum] == str(n):
					for string in row[documentColNum].split(' '):
						stemWord = regex.sub('', string.lower())
						#stemWord = regex.sub('', stem(string.lower()))
						# add word to our dictionary
						if (stemWord not in stopwords) and (stemWord != ''):
							if stemWord in d:
								d[stemWord] += 1
							else:
								d[stemWord] = 1

			popularWords = sorted(d, key=d.get, reverse=True)
			fileName = 'lsa_popular_words_' + str(n) + '.txt'
			wordFile = open(fileName, 'w')
			for i in range(len(popularWords)):
				wordFile.write('%s\n' % popularWords[i])

			print(len(popularWords))