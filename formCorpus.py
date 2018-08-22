import csv
import sys
import nltk # $ pip install nltk
from nltk.corpus import stopwords

csv.field_size_limit(sys.maxsize)
stopwords = stopwords.words('english')

inputFile = 'all_data_w_paragraphs_public_access.csv'

# since the file is so large, this indicates how many lines we want to read
# lineNum = 10
d = {}
badWords = []
documentColNum = 0

with open(inputFile, encoding='ISO-8859-1') as csvFile:
	reader = csv.reader(csvFile)

	for row in reader:
		#if (reader.line_num < lineNum):
		tokens = nltk.word_tokenize(row[documentColNum])
		tagged = nltk.pos_tag(tokens)
		for tag in tagged:
			# if we find a pronoun, add it to the list of words that we don't want
			if (tag[1].startswith('NNP')):
				badWords.append(tag[0])
				# and erase all previous entries in our dictionary of that word
				if (tag[0] in d):
					d[tag[0]] = 0
			# add word to our dictionary
			elif (tag[1].startswith('V') or tag[1] == 'NN' or tag[1] == 'NNS') and (tag[0] not in stopwords) and ('.' not in tag[0]) and (tag[0] != '[' and tag[0] != ']') and (tag[0] not in badWords):
				if tag[0] in d:
					d[tag[0]] += 1
				else:
					d[tag[0]] = 1

	popularWords = sorted(d, key=d.get, reverse=True)
	wordFile = open('lsa_popular_words.txt', 'w')
	for i in range(len(popularWords)):
		wordFile.write('%s\n' % popularWords[i])
	#print(popularWords)
	#wordFrequencies = sorted(d.values(), reverse=True)
	#print(wordFrequencies)