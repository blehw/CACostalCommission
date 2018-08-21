import csv
import sys
import random
import numpy
import nltk # $ pip install nltk
from nltk.corpus import stopwords
from copy import deepcopy
import math
from scipy import linalg, dot, spatial

numpy.set_printoptions(threshold=numpy.nan)

csv.field_size_limit(sys.maxsize)
stopwords = stopwords.words('english')

inputFile = 'all_data_w_paragraphs_public_access.csv'

# since the file is so large, this indicates how many lines we want to read
lineNum = 100
d = {}
badWords = []
# this is the column that the text is in
documentColNum = 0

with open(inputFile, encoding='ISO-8859-1') as csvFile:
	reader = csv.reader(csvFile)

	'''
	for row in reader:
		if (reader.line_num < lineNum):
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
	'''

	csvFile.seek(0)
	reader = csv.reader(csvFile)

	with open('lsa_popular_words.txt') as f:
		popularWords = f.read().splitlines()
	#print(len(popularWords))

	# our list containing inverse document frequency values
	idfList = [0 for i in range(len(popularWords))]

	for row in reader:
		if reader.line_num < lineNum:
			# if an entry of text contains a certain word, increment that value in our list by 1
			for i in range(len(popularWords)):
				if popularWords[i] in row[documentColNum]:
					idfList[i] += 1
	for i in range(len(idfList)):
		# do math stuff
		idf = math.log((lineNum / idfList[i]))
		idfList[i] = idf
		# this is the weiging value for each term
		#print(popularWords[i] + " " + str(idf))

	csvFile.seek(0)
	reader = csv.reader(csvFile)

	matrixList = []

	for row in reader:
		if (reader.line_num < lineNum):
			tfidfList = [0 for i in range(len(popularWords))]
			tfList = [0 for i in range(len(popularWords))]
			# count number of times each word appears in each line
			for word in row[documentColNum].split():
				for popWord in popularWords:
					if word == popWord:
						tfList[popularWords.index(word)] += 1
			# multiply the term frequenc by the appropriate weighing
			for i in range(len(tfList)):
				tfidfList[i] = tfList[i] * idfList[i]
			matrixList.append(tfidfList)
	
	matrix = numpy.array(matrixList)
	#print(matrix)

	# rotate the matrix so that it is words down and documents across
	rotatedMatrix = [*zip(*matrix)]
	# print(len(rotatedMatrix))
	print(rotatedMatrix)

	# math stuff
	u,sigma,vt = linalg.svd(rotatedMatrix)

	dimensionsToReduce = linalg.norm(sigma)
	print(dimensionsToReduce)

	rows = len(sigma)

	# eliminate unimportant dimensions
	if dimensionsToReduce < rows:
		for index in range(rows - int(dimensionsToReduce), rows):
			sigma[index] = 0

	# reconstruct matrix
	transformedMatrix = dot(dot(u, linalg.diagsvd(sigma, len(rotatedMatrix), len(vt))) ,vt)
	#print(transformedMatrix)

	# this matrix has words down and documents across, showing weighted values for each
	# m_nonzero_rows = m[[i for i, x in enumerate(m) if x.any()]]
	# print(transformedMatrix)

	string = 'ice'
	dists = []
	for row in transformedMatrix:
		dists.append(spatial.distance.cosine(transformedMatrix[popularWords.index(string)], row))
	'''
	print(dists)
	print(len(transformedMatrix))
	print(len(popularWords))
	print(len(dists))
	'''
	print('Words most related to ' + string + ':')
	for n in sorted(dists)[:10]:
		print(popularWords[dists.index(n)])

