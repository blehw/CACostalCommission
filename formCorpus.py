import csv
import sys
import nltk # $ pip install nltk
from nltk.corpus import stopwords
from stemming.porter2 import stem
import string

csv.field_size_limit(sys.maxsize)
stopwords = stopwords.words('english')

inputFile = 'all_data_w_paragraphs_public_access.csv'

# since the file is so large, this indicates how many lines we want to read
lineNum = 1000
documentColNum = 0
startYear = 1996
endYear = 2016
yearColNum = 2

doneYears = [2001, 2011]

table = str.maketrans({key: None for key in string.punctuation})

with open(inputFile, encoding='ISO-8859-1') as csvFile:

	for n in range(startYear, endYear + 1, 2):

		if n not in doneYears:

			d = {}
			badWords = []

			print(n)

			csvFile.seek(0)
			reader = csv.reader(csvFile)

			for row in reader:
				# if (reader.line_num < lineNum):
				if row[yearColNum] == str(n):
					tokens = nltk.word_tokenize(row[documentColNum])
					tagged = nltk.pos_tag(tokens)
					for tag in tagged:
						stemWord = stem(tag[0]).lower().translate(table)
						# if we find a pronoun, add it to the list of words that we don't want
						if (tag[1].startswith('NNP')):
							badWords.append(stemWord)
							# and erase all previous entries in our dictionary of that word
							if (stemWord in d):
								d[stemWord] = 0
						# add word to our dictionary
						elif (tag[1].startswith('V') or tag[1] == 'NN' or tag[1] == 'NNS') and (stemWord != '') and (stemWord not in badWords):
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