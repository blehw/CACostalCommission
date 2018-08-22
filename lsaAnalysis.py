import numpy
from scipy import linalg, dot, spatial

inputFile = 'all_data_w_paragraphs_public_access.csv'

with open(inputFile, encoding='ISO-8859-1') as csvFile:
     rowCount = sum(1 for row in csvFile)

lineNum = 1000
startYear = 1996
endYear = 2016
currYear = 2016

for n in range(startYear, endYear + 1, 5):

	matrixFile = 'lsa_matrix_' + str(n) + '.txt'

	with open(matrixFile) as f:
		matrixNums = f.read().splitlines()

	wordsFile = 'lsa_popular_words_' + str(n) + '.txt'

	with open(wordsFile) as f:
			popularWords = f.read().splitlines()

	matrixNums = [float(i) for i in matrixNums]
	matrixList = []

	print(len(popularWords))

	for i in range(len(popularWords)):
		row = []
		for j in range(i * (rowCount - 1), (i * (rowCount - 1)) + rowCount - 1):
			row.append(matrixNums[j])
		matrixList.append(row)

	matrix = numpy.array(matrixList)

	string = 'wall'
	dists = []
	for row in matrix:
		dists.append(spatial.distance.cosine(matrix[popularWords.index(string)], row))

	print('Words most related to ' + string + ' in ' + str(n) + ':')
	for n in sorted(dists).remove(string)[:10]:
		print(popularWords[dists.index(n)])


