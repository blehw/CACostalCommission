import csv
import sys
import numpy
import math
from scipy import linalg, dot
import string
import nltk # $ pip install nltk
from nltk.corpus import stopwords

numpy.set_printoptions(threshold=numpy.nan)

lineNum = 1000
# this is the column that the text is in
documentColNum = 0
startYear = 1998
endYear = 2016
yearColNum = 2

doneYears = [2001, 2011]

inputFile = 'all_data_w_paragraphs_public_access.csv'

'''
with open(inputFile, encoding='ISO-8859-1') as csvFile:
     rowCount = sum(1 for row in csvFile)
'''

with open(inputFile, encoding='ISO-8859-1') as csvFile:

	for n in range(startYear, endYear + 1, 2):

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
			pop = popularWords.copy()

			for row in reader:
				if row[yearColNum] == str(n):
					usedWords = []
					tfList = [0 for i in range(len(popularWords))]
				# if an entry of text contains a certain word, increment that value in our list by 1
					#for i in range(len(popularWords)):
					tokens = nltk.word_tokenize(row[documentColNum])
					tagged = nltk.pos_tag(tokens)
					for tag in tagged:
						word = tag[0].lower()
						if word in popularWords:
							tfList[popularWords.index(word)] += 1
							if word not in usedWords:
								idfList[popularWords.index(word)] += 1
								usedWords.append(word)
							if word in pop:
								pop.remove(word)
						
						'''
						if popularWords[i] in row[documentColNum].lower():
							idfList[i] += 1
						'''
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

			'''
			for row in reader:
				if row[yearColNum] == str(n):
					tfidfList = [0 for i in range(len(popularWords))]
					tfList = [0 for i in range(len(popularWords))]
					# count number of times each word appears in each line
					for word in row[documentColNum].split():
						for popWord in popularWords:
							if word == popWord:
								tfList[popularWords.index(word)] += 1
					'''
					# multiply the term frequenc by the appropriate weighing
			for tfList in tfs:
				tfidfList = [0 for i in range(len(popularWords))]
				for i in range(len(tfList)):
					tfidfList[i] = tfList[i] * idfList[i]
				matrixList.append(tfidfList)
			
			matrix = numpy.array(matrixList)

			print('Performing matrix operations')

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
				print('Reducing dimensions')
				for index in range(rows - int(dimensionsToReduce), rows):
					sigma[index] = 0

			# reconstruct matrix
			print('Reconstructing matrix')
			transformedMatrix = dot(dot(u, linalg.diagsvd(sigma, len(rotatedMatrix), len(vt))) ,vt)
			print(transformedMatrix)
			#print(transformedMatrix)

			# this matrix has words down and documents across, showing weighted values for each
			# m_nonzero_rows = m[[i for i, x in enumerate(m) if x.any()]]
			# print(transformedMatrix)

			transformedMatrix = transformedMatrix.tolist()

			outFile = 'lsa_matrix_' + str(n) + '.txt'

			with open(outFile,'w') as o:
				for row in transformedMatrix:
					for column in row:
						o.write('%s\n' % str(column))