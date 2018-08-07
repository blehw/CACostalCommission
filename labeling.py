import csv
import sys
import random
import numpy
import nltk # $ pip install nltk
from nltk.corpus import stopwords
from copy import deepcopy

# nltk.download('stopwords')
# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')

csv.field_size_limit(sys.maxsize)
stopwords = stopwords.words('english')

inputFile = 'all_data_v3_w_text_1.csv'
badWords = []
# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')

numPopularWords = 500
d = {}
with open(inputFile, encoding='ISO-8859-1') as csvFile:
	reader = csv.reader(csvFile)
	
	'''
	for row in reader:
		tokens = nltk.word_tokenize(row[2])
		tagged = nltk.pos_tag(tokens)
		for tag in tagged:
			if (tag[1].startswith('NNP')):
				badWords.append(tag[0])
				if (tag[0] in d):
					d[tag[0]] = 0
			elif (tag[1].startswith('V') or tag[1] == 'NN' or tag[1] == 'NNS') and (tag[0] not in stopwords) and ('.' not in tag[0]) and (tag[0] != '[' and tag[0] != ']') and (tag[0] not in badWords):
				if tag[0] in d:
					d[tag[0]] += 1
				else:
					d[tag[0]] = 1

	popularWords = sorted(d, key=d.get, reverse=True)
	wordFile = open('popular_words.txt', 'w')
	for i in range(numPopularWords):
		wordFile.write('%s\n' % popularWords[i])
	'''

	with open('popular_words.txt') as f:
		popularWords = f.read().splitlines()
	print(popularWords)

	centers = []
	clusters = [[] for i in range(20)]
	for i in range(20):
		c = []
		for j in range(numPopularWords):
			c.append(random.uniform(0, 1))
		centers.append(numpy.array(c))

	#print(centers)

	unequal = True
	while unequal:
		print(centers)
		oldClusters = deepcopy(clusters)
		csvFile.seek(0)
		for row in reader:
			vector = []
			for word in popularWords:
				if word in row[2]:
					vector.append(1)
				else:
					vector.append(0)
			v = numpy.array(vector)
			#print(v)

			minDist = numpy.linalg.norm(v-centers[0])
			minIndex = 0
			for i in range(1, len(centers)):
				dist = numpy.linalg.norm(v-centers[i])
				if dist < minDist:
					minDist = dist
					minIndex = i
			#print(minDist)
			clusters[minIndex].append(reader.line_num)

		'''
		for cluster in	clusters:
			print(len(cluster))
		'''

		if clusters != oldClusters:
			for i in range(len(clusters)):
				if (len(clusters[i]) != 0):
					c = numpy.zeros(numPopularWords)
					for vector in clusters[i]:
						c += vector
					c = c / len(clusters[i])
					centers[i] = c
			for i in range(len(clusters)):
				if len(clusters[i]) != len(oldClusters[i]):
					print(len(clusters[i]) - len(oldClusters[i]))
			clusters = [[] for i in range(20)]
			print('****')
		else:
			unequal = False











