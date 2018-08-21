import csv
import sys
import random
import numpy
import nltk # $ pip install nltk
from nltk.corpus import stopwords
from copy import deepcopy
import math
from scipy import linalg, dot
from sklearn.decomposition import TruncatedSVD

csv.field_size_limit(sys.maxsize)
stopwords = stopwords.words('english')

inputFile = 'all_data_w_paragraphs_public_access.csv'

numPopularWords = 500
lineNum = 100
d = {}
badWords = []
with open(inputFile, encoding='ISO-8859-1') as csvFile:
	reader = csv.reader(csvFile)

	# magic numbers
	documentRowNum = 0

	'''
	for row in reader:
		if (reader.line_num < lineNum):
			tokens = nltk.word_tokenize(row[documentRowNum])
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
	wordFile = open('lsa_popular_words.txt', 'w')
	for i in range(len(popularWords)):
		wordFile.write('%s\n' % popularWords[i])
	#print(popularWords)
	#wordFrequencies = sorted(d.values(), reverse=True)
	#print(wordFrequencies)
	'''

	csvFile.seek(0)
	reader = csv.reader(csvFile)

	with open('lsa_popular_words.txt') as f:
		popularWords = f.read().splitlines()
	#print(popularWords)

	idfList = [0 for i in range(len(popularWords))]

	for row in reader:
		if reader.line_num < lineNum:
			for i in range(len(popularWords)):
				if popularWords[i] in row[documentRowNum]:
					idfList[i] += 1

	for i in range(len(idfList)):
		idf = math.log((lineNum / idfList[i]))
		idfList[i] = idf
		print(popularWords[i] + " " + str(idf))

	csvFile.seek(0)
	reader = csv.reader(csvFile)

	matrixList = []

	for row in reader:
		if (reader.line_num < lineNum):
			tfidfList = [0 for i in range(len(popularWords))]
			tfList = [0 for i in range(len(popularWords))]
			for word in row[documentRowNum]:
				if word in popularWords:
					tfList[popularWords.index(word)] += 1
			for i in range(len(tfList)):
				tfidfList[i] = tfList[i] * idfList[i]
			matrixList.append(tfidfList)
	
	matrix = numpy.array(matrixList)
	#print(matrix)

	rotatedMatrix = [*zip(*matrix)]
	#print(rotatedMatrix)

	u,sigma,vt = linalg.svd(rotatedMatrix)

	dimensionsToReduce = linalg.norm(sigma)
	print(dimensionsToReduce)

	rows = len(sigma)

	for index in range(rows - int(dimensionsToReduce), rows):
		sigma[index] = 0

	transformedMatrix = dot(dot(u, linalg.diagsvd(sigma, len(rotatedMatrix), len(vt))) ,vt)

	print(transformedMatrix)

	#print(docFreqCounts)
	#print(len(popularWords))



