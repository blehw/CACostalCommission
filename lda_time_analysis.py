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

def getWordVolatility(w):

	index = 0
	allPopularWords = []

	for n in range(startYear, endYear + 1,2):
		wordsFile = 'lsa_words/lsa_popular_words_' + str(n) + '.txt'
		with open(wordsFile) as f:
			popularWords = f.read().splitlines()
		allPopularWords.append(popularWords)

	volatilities = []

	for n in range(startYear, endYear + 1,2):

		print(n)

		with open(inputFile, encoding='ISO-8859-1') as csvFile:
			reader = csv.reader(csvFile)
			numDocs = 0
			for row in reader:
				if row[yearColNum] == str(n):
					numDocs += 1

		matrixFile = 'lsa_matrix/lsa_matrix_' + str(n) + '.txt'

		'''
		matrixNums = []
		with open(matrixFile) as f:
			for line in f:
				matrixNums.append(line)
			#matrixNums = f.read().splitlines()
		'''
		
		popularWords = allPopularWords[index]

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

	return volatilities

top_words = 100
wordsToAnalyze = 1500

cluster_dict = {}

for n in range(1996,2017,1):
	f = open("lda_words/lda_words_" + str(n) + ".txt")
	words = f.read().split(" ")[:-1]
	f.close()
	cluster_dict[n] = [words[i:i + wordsToAnalyze][:top_words] for i in range(0, len(words), wordsToAnalyze)]

year = 1996
c = 4

cluster_words = cluster_dict[year][c]

for key in cluster_dict.keys():
	if key != year and key % 4 == 0:
		max_cluster = []
		for cluster in cluster_dict[key]:
			set_2 = frozenset(cluster)
			new_cluster = [x for x in cluster_words if x in set_2]
			if len(new_cluster) > len(max_cluster):
				max_cluster = new_cluster
		cluster_words = max_cluster

#cluster_words = cluster_words[:10]
print(cluster_words)

cluster_str = ""
for w in cluster_words:
	cluster_str += w + " "
print(cluster_words)

print('Analyzing')
volatilities = np.zeros(((endYear - startYear)//2 + 1))
for word in cluster_words:
	v= np.array(getWordVolatility(word))
	volatilities += v

volatilities = np.divide(volatilities, len(cluster_words))
volatilities = volatilities.tolist()
print(volatilities)

f = plt.figure()
plt.plot(range((endYear - startYear)//2 + 1), volatilities)
f.suptitle(cluster_str, fontsize=5)
plt.yticks(np.arange(min(volatilities), max(volatilities), 0.01))
plt.show()

pdfName =  'cluster3.pdf'
f.savefig(pdfName, bbox_inches='tight')