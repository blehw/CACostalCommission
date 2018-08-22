import csv
import numpy
from scipy import linalg, dot, spatial

inputFile = 'all_data_w_paragraphs_public_access.csv'

lineNum = 1000
startYear = 1996
endYear = 2011
yearColNum = 2

for n in range(startYear, endYear + 1, 5):

	with open(inputFile, encoding='ISO-8859-1') as csvFile:
		reader = csv.reader(csvFile)
		numDocs = 0
		for row in reader:
			if row[yearColNum] == str(n):
				numDocs += 1

	print(n)

	matrixFile = 'lsa_matrix_' + str(n) + '.txt'

	with open(matrixFile) as f:
		matrixNums = f.read().splitlines()

	wordsFile = 'lsa_popular_words_' + str(n) + '.txt'

	with open(wordsFile) as f:
			popularWords = f.read().splitlines()

	matrixNums = [float(i) for i in matrixNums]
	matrixList = []

	for i in range(len(popularWords)):
		row = []
		for j in range(i * numDocs, (i * numDocs) + numDocs):
			row.append(matrixNums[j])
		matrixList.append(row)

	matrix = numpy.array(matrixList)

	string = 'winter'
	dists = []
	for row in matrix:
		not_zeros = row.any()
		if not_zeros:
			dists.append(spatial.distance.cosine(matrix[popularWords.index(string)], row))
		else:
			dists.append(1)

	relatedWords = []

	for x in sorted(dists):
		relatedWords.append(popularWords[dists.index(x)])

	relatedWords.remove(string)
	print('Words most related to ' + string + ' in ' + str(n) + ':')
	for word in relatedWords[:20]:
		print(word)