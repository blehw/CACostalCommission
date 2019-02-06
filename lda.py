import csv
import numpy as np
from sklearn.decomposition import LatentDirichletAllocation

inputFile = 'all_data_w_paragraphs_public_access.csv'
yearColNum = 2

n_topics = 20
lda_model = LatentDirichletAllocation(n_components=20,learning_method='online',random_state=0, verbose=0)

matrixFile = 'lsa_matrix_2016.txt'
matrixNums = []
f = open(matrixFile)
for line in f:
	matrixNums.append(line)

matrixNums = [float(i) for i in matrixNums]
matrixList = []

csvFile = open(inputFile, encoding='ISO-8859-1')
reader = csv.reader(csvFile)
numDocs = 0
for row in reader:
	if row[yearColNum] == '2016':
		numDocs += 1

for i in range(len(matrixNums)):
	row = []
	for j in range(0, numDocs):
		row.append(matrixNums[j])
	matrixList.append(row)

matrix = np.array(matrixList)
np.savetext('lsa_matrix_2016_condensed.txt')

lda_topic_matrix = lda_model.fit_transform(matrix)