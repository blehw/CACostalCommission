import csv
import numpy
from scipy import linalg, dot, spatial
import matplotlib.pyplot as plt

inputFile = 'all_data_w_paragraphs_public_access.csv'

lineNum = 1000
startYear = 1996
endYear = 2016
yearColNum = 2

index = 0
allPopularWords = []

for n in range(startYear, endYear + 1, 5):
	wordsFile = 'lsa_popular_words_' + str(n) + '.txt'
	with open(wordsFile) as f:
		popularWords = f.read().splitlines()
	allPopularWords.append(popularWords)

doneYears = [1996, 2001, 2006, 2011, 2016]
volatilities = []

for n in range(startYear, endYear + 1, 5):

	#print(n)

	with open(inputFile, encoding='ISO-8859-1') as csvFile:
		reader = csv.reader(csvFile)
		numDocs = 0
		for row in reader:
			if row[yearColNum] == str(n):
				numDocs += 1

	matrixFile = 'lsa_matrix_' + str(n) + '.txt'

	with open(matrixFile) as f:
		matrixNums = f.read().splitlines()
	
	popularWords = allPopularWords[index]

	string = 'fire'

	if string not in popularWords:
		volatilities.append(1)
	else:
		matrixNums = [float(i) for i in matrixNums]
		matrixList = []

		for i in range(len(popularWords)):
			row = []
			for j in range(i * numDocs, (i * numDocs) + numDocs):
				row.append(matrixNums[j])
			matrixList.append(row)

		matrix = numpy.array(matrixList)

		dists = []
		for row in matrix:
			not_zeros = row.any()
			if not_zeros:
				dists.append(spatial.distance.cosine(matrix[popularWords.index(string)], row))
			else:
				dists.append(1)

		relatedWords = []
		relatedDists = []

		for x in sorted(dists):
			if popularWords[dists.index(x)] not in relatedWords:
				relatedWords.append(popularWords[dists.index(x)])
				relatedDists.append(x)

		if string in relatedWords:
			relatedWords.remove(string)
			relatedDists.remove(0)
		print('Words most related to ' + string + ' in ' + str(n) + ':')
		'''
		for word in relatedWords[:10]:
			print(word)
		'''

		sigOccurences = []

		for x in range(len(relatedWords)):
			if relatedDists[x] < 0.8:
				sigOccurences.append(relatedWords[x])

		coVariations = []
		for word in sigOccurences:
			ranks = []
			for year in allPopularWords:
				if word not in year:
					ranks.append(len(year))
				else:
					ranks.append(year.index(word) + 1)
			coVariations.append(numpy.std(ranks) / numpy.mean(ranks))

		volatilities.append(numpy.mean(coVariations))

		index += 1

plt.plot(doneYears, volatilities)
plt.show()