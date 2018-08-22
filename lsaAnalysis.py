import numpy
from scipy import linalg, dot, spatial

inputFile = 'all_data_w_paragraphs_public_access.csv'

# with open(inputFile, encoding='ISO-8859-1') as csvFile:
#     rowCount = sum(1 for row in csvFile)

lineNum = 1000

with open('lsaMatrix.txt') as f:
	matrixNums = f.read().splitlines()

with open('lsa_popular_words.txt') as f:
		popularWords = f.read().splitlines()

matrixNums = [float(i) for i in matrixNums]
matrixList = []

print(len(popularWords))

for i in range(len(popularWords)):
	row = []
	for j in range(i * (lineNum - 1), (i * (lineNum - 1)) + lineNum - 1):
		row.append(matrixNums[j])
	matrixList.append(row)

matrix = numpy.array(matrixList)

string = 'flooding'
dists = []
for row in matrix:
	dists.append(spatial.distance.cosine(matrix[popularWords.index(string)], row))

print('Words most related to ' + string + ':')
for n in sorted(dists)[:10]:
	print(popularWords[dists.index(n)])


