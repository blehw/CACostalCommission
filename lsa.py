import csv
import sys
import numpy
import math
from scipy import linalg, dot
import string
from nltk.corpus import stopwords
from stemming.porter2 import stem
import re

numpy.set_printoptions(threshold=numpy.nan)

lineNum = 1000
# this is the column that the text is in
documentColNum = 0
startYear = 2016
endYear = 2016
yearColNum = 2

doneYears = []
regex = re.compile('[^a-zA-Z]')
stopwords = stopwords.words('english')

inputFile = "all_data_v3.csv"
#inputFile = 'all_data_w_paragraphs_public_access.csv'

'''
with open(inputFile, encoding='ISO-8859-1') as csvFile:
     rowCount = sum(1 for row in csvFile)
'''

with open(inputFile, encoding='ISO-8859-1') as csvFile:

	for n in range(startYear, endYear + 1):

		if n not in doneYears:

			print(n)

			csvFile.seek(0)
			reader = csv.reader(csvFile)

			fileName = 'lsa_popular_words_' + str(n) + '.txt'

			with open(fileName) as f:
				popularWords = f.read().splitlines()
			print(len(popularWords))

			print('Constructing tf-idf matrix')

			# our list containing inverse document frequency values
			idfList = [0 for i in range(len(popularWords))]
			tfs = []

			numDocs = 0

			for row in reader:
				if row[yearColNum] == str(n):
					usedWords = []
					tfList = [0 for i in range(len(popularWords))]
					# if an entry of text contains a certain word, increment that value in our list by 1
					#for i in range(len(popularWords)):
					for w in row[documentColNum].split():
						word = regex.sub('', w.lower())
						#word = regex.sub('', stem(w.lower()))
						if (word not in stopwords) and (word != ''):
							tfList[popularWords.index(word)] += 1
							if word not in usedWords:
								idfList[popularWords.index(word)] += 1
								usedWords.append(word)
					numDocs += 1
					tfs.append(tfList)

			for i in range(len(idfList)):
				# do math stuff
				idf = math.log((numDocs / idfList[i]))
				idfList[i] = idf
				# this is the weiging value for each term
				#print(popularWords[i] + " " + str(idf))

			csvFile.seek(0)
			reader = csv.reader(csvFile)

			matrixList = []

			for tfList in tfs:
				tfidfList = [0 for i in range(len(popularWords))]
				for i in range(len(tfList)):
					tfidfList[i] = tfList[i] * idfList[i]
				matrixList.append(tfidfList)
			
			matrix = numpy.array(matrixList)

			print('Performing matrix operations')

			# rotate the matrix so that it is words down and documents across
			rotatedMatrix = [*zip(*matrix)]
			print(rotatedMatrix[0])
			print(rotatedMatrix[1])
			# print(len(rotatedMatrix))

			# math stuff
			u,sigma,vt = linalg.svd(rotatedMatrix)

			dimensionsToReduce = linalg.norm(sigma)
			# print(dimensionsToReduce)

			rows = len(sigma)

			# eliminate unimportant dimensions
			if dimensionsToReduce < rows:
				print('Reducing dimensions')
				for index in range(rows - int(dimensionsToReduce), rows):
					sigma[index] = 0

			# reconstruct matrix
			print('Reconstructing matrix')
			transformedMatrix = dot(dot(u, linalg.diagsvd(sigma, len(rotatedMatrix), len(vt))) ,vt)
			#print(transformedMatrix)

			# this matrix has words down and documents across, showing weighted values for each
			# m_nonzero_rows = m[[i for i, x in enumerate(m) if x.any()]]
			# print(transformedMatrix)

			transformedMatrix = transformedMatrix.tolist()

			outFile = 'lsa_matrix2_' + str(n) + '.txt'

			with open(outFile,'w') as o:
				for row in transformedMatrix:
					for column in row:
						o.write('%s\n' % str(column))