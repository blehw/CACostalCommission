import csv
import sys
import numpy
import math
from scipy import linalg, dot

numpy.set_printoptions(threshold=numpy.nan)

lineNum = 1000
# this is the column that the text is in
documentColNum = 0
startYear = 1996
endYear = 2016
currYear = 2016
yearColNum = 2

inputFile = 'all_data_w_paragraphs_public_access.csv'

'''
with open(inputFile, encoding='ISO-8859-1') as csvFile:
     rowCount = sum(1 for row in csvFile)
'''

with open(inputFile, encoding='ISO-8859-1') as csvFile:

	for n in range(endYear, endYear + 1, 5):

		reader = csv.reader(csvFile)

		print(n)

		fileName = 'lsa_popular_words_' + str(n) + '.txt'

		with open(fileName) as f:
			popularWords = f.read().splitlines()
		#print(len(popularWords))

		# our list containing inverse document frequency values
		idfList = [0 for i in range(len(popularWords))]

		numDocs = 0

		for row in reader:
			if row[yearColNum] == str(n):
			# if an entry of text contains a certain word, increment that value in our list by 1
				for i in range(len(popularWords)):
					if popularWords[i] in row[documentColNum]:
						idfList[i] += 1
				numDocs += 1
				print(numDocs)

		for i in range(len(idfList)):
			# do math stuff
			idf = math.log((numDocs / idfList[i]))
			idfList[i] = idf
			# this is the weiging value for each term
			#print(popularWords[i] + " " + str(idf))

		csvFile.seek(0)
		reader = csv.reader(csvFile)

		matrixList = []

		for row in reader:
			if row[yearColNum] == str(n):
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

		outFile = 'lsa_matrix_' + str(n) + '.txt'

		'''
		with open(outFile,'w') as o:
			for row in transformedMatrix:
				for column in row:
					o.write('%s\n' % str(column))
		'''