import csv
import numpy as np
from scipy import linalg, dot, spatial
import matplotlib.pyplot as plt
#from stemming.porter2 import stem
import re

inputFile = 'all_data_w_paragraphs_public_access.csv'

startYear = 1996
endYear = 2016
yearColNum = 2

regex = re.compile('[^a-zA-Z]')

index = 0
allPopularWords = []

for n in range(startYear, endYear + 1):
	wordsFile = 'lsa_words/lsa_popular_words_' + str(n) + '.txt'
	with open(wordsFile) as f:
		popularWords = f.read().splitlines()
	allPopularWords.append(popularWords)

volatilities = []

for n in range(startYear, endYear + 1):

	print(n)

	with open(inputFile, encoding='ISO-8859-1') as csvFile:
		reader = csv.reader(csvFile)
		numDocs = 0
		for row in reader:
			if row[yearColNum] == str(n):
				numDocs += 1

	matrixFile = 'lsa_matrix_' + str(n) + '.txt'

	'''
	matrixNums = []
	with open(matrixFile) as f:
		for line in f:
			matrixNums.append(line)
		#matrixNums = f.read().splitlines()
	'''
	
	popularWords = allPopularWords[index]

	w = 'beach'

	if w not in popularWords:
		volatilities.append(0)
	else:
		'''
		matrixNums = [float(i) for i in matrixNums]
		matrixList = []

		for i in range(len(popularWords)):
			row = []
			for j in range(i * numDocs, (i * numDocs) + numDocs):
				row.append(matrixNums[j])
			matrixList.append(row)

		matrix = np.array(matrixList)
		'''

		matrix = np.loadtxt(matrixFile)

		dists = []
		for row in matrix:
			not_zeros = row.any()
			if not_zeros:
				dists.append(spatial.distance.cosine(matrix[popularWords.index(w)], row))
			else:
				dists.append(1)

		relatedWords = []
		relatedDists = []

		for x in sorted(dists):
			if popularWords[dists.index(x)] not in relatedWords:
				relatedWords.append(popularWords[dists.index(x)])
				relatedDists.append(x)

		if w in relatedWords:
			relatedWords.remove(w)
			relatedDists.remove(0)
		print('Words most related to ' + w + ' in ' + str(n) + ':')
		for i in range(10):
			print(str(relatedWords[i]) + ' ' + str(relatedDists[i]))

		sigOccurences = []

		for x in range(len(relatedWords)):
			if relatedDists[x] < 0.5:
				sigOccurences.append(relatedWords[x])

		coVariations = []
		for word in sigOccurences:
			ranks = []
			for year in allPopularWords:
				if word not in year:
					ranks.append(len(year))
				else:
					ranks.append(year.index(word) + 1)
			# check if negative
			coVariations.append(np.std(ranks) / np.mean(ranks))

		volatilities.append(np.mean(coVariations))

	index += 1

f = plt.figure()
plt.plot(range(startYear, endYear + 1), volatilities)
plt.yticks(np.arange(min(volatilities), max(volatilities)+0.1, 0.1))
plt.show()

pdfName = w + '.pdf'
f.savefig(pdfName, bbox_inches='tight')