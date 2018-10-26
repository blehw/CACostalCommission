# big idea:
# calculate matrix (rows -> permits, cols -> top-500 words)
# turn each row into an example to use in kmeans algorithm
# permit's features are its top-500 words

# before running this script, do:
# pip install stemming

import csv
import sys
import numpy
import math
from scipy import linalg, dot
import string
from nltk.corpus import stopwords
import nltk
from stemming.porter2 import stem
import re
import random
import collections

numpy.set_printoptions(threshold=numpy.nan)

# this is the column that the text is in
documentColNum = 0
startYear = 2016
endYear = 2016
yearColNum = 2

regex = re.compile('[^a-zA-Z]')
stopwords = stopwords.words('english')

inputFile = 'all_data_w_paragraphs_public_access.csv'

def getMatrices():

    matrices = []
    with open(inputFile, encoding='ISO-8859-1') as csvFile:
        for n in range(startYear, endYear + 1):
            csvFile.seek(0)
            reader = csv.reader(csvFile)

            fileName = 'lsa_popular_words_' + str(n) + '.txt'

            with open(fileName) as f:
                popularWords = f.read().splitlines()

            # look at only the top 100 words
            popularWords = popularWords[:1000]
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
                        if (word not in stopwords) and (word != '') and (word in popularWords):
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

            csvFile.seek(0)
            reader = csv.reader(csvFile)

            matrixList = []

            for tfList in tfs:
                tfidfList = [0 for i in range(len(popularWords))]
                for i in range(len(tfList)):
                    tfidfList[i] = tfList[i] * idfList[i]
                matrixList.append(tfidfList)
            
            matrix = numpy.array(matrixList)

            #print('Performing matrix operations')

            # rotate the matrix so that it is words down and documents across
            #rotatedMatrix = [*zip(*matrix)]
            matrices.append(matrix)
    csvFile.close()
    return matrices

# turn each row into an example
def convertMatricesToExamples(matrices):
    fileName = 'lsa_popular_words_1996.txt'
    with open(fileName) as f:
        popularWords = f.read().splitlines()
    f.close()
    examples = []
    for matrix in matrices:
        for row in matrix:
            d = {}
            for i in range(len(row)):
                d[popularWords[i]] = row[i]
            examples.append(d)
    return examples

# helper for kmeans function
def dotProduct(d1, d2):
    if len(d1) < len(d2):
        return dotProduct(d2, d1)
    else:
        return sum(d1.get(f, 0) * v for f, v in d2.items())

# helper for kmeans function
def increment(d1, scale, d2):
    for f, v in d2.items():
        d1[f] = d1.get(f, 0) + v * scale

def kmeans(examples, K, maxIters):
    # initialize k cluster centroids u_0,...,u_k-1 to random elements of examples
    centroids = random.sample(examples, K)
    assignments = [-1 for i in range(len(examples))] # contains z_0,...,z_n-1 and tells us which cluster 0,...,K-1 each example is assigned to
    # examplesClustered = [[] for i in range(K)] # list of lists of examples at each cluster (index represents the cluster number)
    cache = collections.defaultdict(int) # key = distance between feature and centroid vectors, value = squared distance
    exampleDotCache = collections.defaultdict(int)
    for i in range(len(examples)): # precompute and map the index of an example to (example dot example)
        exampleDotCache[i] = dotProduct(examples[i], examples[i])

    print('Starting k-means clustering')
    # NOTE: clusters are 0-indexed
    for iteration in range(maxIters):
        print('Iteration ' + str(iteration+1))
        prevAssignments = assignments[:]
        centroidDotCache = collections.defaultdict(int)
        for i in range(len(centroids)): # precompute and map the index of a centroid to (centroid dot centroid)
            centroidDotCache[i] = dotProduct(centroids[i], centroids[i])
        sumOfExamplesAtCluster = [collections.defaultdict(int) for i in range(K)] # maintains sum of examples at a particular cluster (index)
        numExamplesAtCluster = [0 for i in range(K)] # maintains how many examples are at a particular cluster (index)

        ### STEP 1: Assign each example to best cluster
        for e in range(len(examples)): # calculate the cluster each example will be assigned to
            squaredDistances = [] # list of distances of examples from centroids (cluster numbers are the indices of this list) 
            for c in range(K):
                squaredDist = exampleDotCache[e] - 2*dotProduct(examples[e], centroids[c]) + centroidDotCache[c]
                squaredDistances.append(squaredDist)
            minSquaredDist = min(squaredDistances)
            assignments[e] = squaredDistances.index(minSquaredDist) # keep track of assignments of each example to a cluster
            increment(sumOfExamplesAtCluster[assignments[e]], 1.0, examples[e]) 
            numExamplesAtCluster[assignments[e]] += 1

        if assignments == prevAssignments: # convergence has been reached
            break

        ### STEP 2: Find best centroid for each cluster    
        for c in range(K): # iterate thru clusters and update centroid for each one
            ### Calculate average sparse vector of this cluster
            average = collections.defaultdict(int)
            increment(average, 1.0/numExamplesAtCluster[c], sumOfExamplesAtCluster[c])
            centroids[c] = average

    # calculate loss
    loss = 0.0
    for e in range(len(examples)):
        squaredDistance = exampleDotCache[e] - 2*dotProduct(examples[e], centroids[assignments[e]]) + centroidDotCache[assignments[e]]
        loss += squaredDistance
    #print('Centroids:', centroids)
    #print('Assignments:', assignments)
    print('Loss:', loss)
    outFile = 'kmeans.txt'
    with open(outFile,'w') as o:
        o.write('%s\n' % str(centroids))
        o.write('%s\n' % str(assignments))
        o.write('%s\n' % str(loss))
    o.close()

    return centroids, assignments, loss

def outputClusters(path, examples, centers, assignments):
    '''
    Output the clusters to the given path.
    '''
    print('Outputting clusters to %s' % path)
    out = open(path, 'w')
    for j in range(len(centers)):
        out.write('====== Cluster %s\n' % j)
        out.write('--- Centers:\n')
        sortedCenters = sorted(centers[j].items(), key=lambda kv: kv[1], reverse=True)
        for t in sortedCenters[:10]:
            k = t[0]
            v = t[1]
            if v != 0:
                out.write('%s\t%s\n' % (k, v))
        '''
        out.write('--- Assigned points:')
        for i, z in enumerate(assignments):
            if z == j:
                out.write(' '.join(examples[i].keys()))
        '''
    out.close()

###########################################################################

matrices = getMatrices()
examples = convertMatricesToExamples(matrices)
centroids, assignments, loss = kmeans(examples, 6, 100)
outputClusters('kmeans_clusters_' + str(startYear) + '.txt', examples, centroids, assignments)
for i in range(6):
    print('Cluster ' + str(i+1) + ': ' + str(assignments.count(i)))