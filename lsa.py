import csv
import sys
import numpy
import math
from scipy import linalg, dot

numpy.set_printoptions(threshold=numpy.nan)

lineNum = 1000 # total num of docs?
# this is the column that the text is in
documentColNum = 0

inputFile = 'all_data_w_paragraphs_public_access.csv'

# with open(inputFile, encoding='ISO-8859-1') as csvFile:
#     rowCount = sum(1 for row in csvFile)

with open(inputFile, encoding='ISO-8859-1') as csvFile:
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
		idf = math.log((lineNum / idfList[i])) # log of (total num docs / num docs with that term)?
		idfList[i] = idf
		# this is the weiging value for each term
		#print(popularWords[i] + " " + str(idf))

	csvFile.seek(0)
	reader = csv.reader(csvFile)

	matrixList = [] # matrix holding tf-idf values, rows->words and cols->docs

	for row in reader:
		if (reader.line_num < lineNum):
			tfidfList = [0 for i in range(len(popularWords))]
			tfList = [0 for i in range(len(popularWords))]
			# count number of times each word appears in each line
			for word in row[documentColNum].split():
				for popWord in popularWords:
					if word == popWord:
						tfList[popularWords.index(word)] += 1
			# multiply the term frequency by the appropriate weighing
			for i in range(len(tfList)):
				tfidfList[i] = tfList[i] * idfList[i]
			matrixList.append(tfidfList)
	
	matrix = numpy.array(matrixList)
	#print(matrix)

	# Singular Value Decomposition (SVD)

	u,sigma,vt = linalg.svd(matrix)

	# Reduce the dimensions of sigma

	dimensionsToReduce = linalg.norm(sigma)

	smallerSigma = TruncatedSVD(len(popularWords) - dimensionsToReduce)
	print(smallerSigma)

	transformedMatrix = dot(dot(u, linalg.diagsvd(smallerSigma, len(matrix), len(vt))) ,vt)

	# rotate the matrix so that it is words down and documents across
	rotatedMatrix = [*zip(*matrix)]
	# print(len(rotatedMatrix))
	# print(rotatedMatrix)

	# math stuff
	u,sigma,vt = linalg.svd(rotatedMatrix)

	dimensionsToReduce = linalg.norm(sigma)
	# print(dimensionsToReduce)

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

	transformedMatrix = transformedMatrix.tolist()

	### COSINE SIMILARITY:
	### similarity(w1, w2)
	### = cos(w1, w2)
	### = (w1 * w2) / (||w1|| * ||w2||)
	### = (w1 * w2) / (sqrt(sum of all doc counts of w1 squared) * sqrt(sum of all doc counts of w2 squarred))

	with open('lsaMatrix.txt','w') as f:
		for row in transformedMatrix:
			for column in row:
				f.write('%s\n' % str(column))

