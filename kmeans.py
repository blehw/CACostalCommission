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
from sklearn.manifold import TSNE
from bokeh.plotting import figure, output_file, show
from bokeh.models import Label
from bokeh.io import output_notebook
#output_notebook()

numpy.set_printoptions(threshold=numpy.nan)

# this is the column that the text is in
documentColNum = 0
startYear = 2008
endYear = 2008
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
            popularWords = popularWords[:400]
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
    fileName = 'lsa_popular_words_' + startYear + '.txt'
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
    centroids = random.sample(examples, K)
    assignments = [0 for i in range(len(examples))]
    cache = {}
    for i in range(maxIters):
        tempAssignments = [0 for i in range(len(examples))]
        for e in range(len(examples)):
            minCentroid = 0
            scalarMinDist = float('inf')
            for j in range(len(centroids)):
                ex = examples[e].copy()
                distance = 0
                for val in ex.keys():
                    num = 0 
                    if val in centroids[j]:
                        num = centroids[j][val]
                    if ex[val] != 0:
                        num -= ex[val]
                    if num in cache:
                        distance += cache[num]
                    else:
                        squared = num * num
                        distance += squared
                        cache[num] = squared
                if distance < scalarMinDist:
                    minCentroid = j
                    scalarMinDist = distance
            tempAssignments[e] = minCentroid
        if sorted(tempAssignments) == sorted(assignments):
            break
        newCentroids = [{} for i in range(K)]
        counts = [0 for i in range(K)]
        for k in range(len(tempAssignments)):
            asssignedCentroid = tempAssignments[k]
            example = examples[k].copy()
            counts[asssignedCentroid] += 1
            increment(newCentroids[asssignedCentroid], 1, example)
        for c in range(len(newCentroids)):
            centroid = newCentroids[c]
            for key in centroid:
                centroid[key] = centroid[key] / float(counts[c])
        assignments = tempAssignments
        centroids = newCentroids
    totalLoss = 0
    for m in range(len(assignments)):
        lossEx = examples[m].copy()
        loss = 0
        for val in lossEx.keys(): 
            num = 0
            if val in centroids[assignments[m]]:
                num = centroids[assignments[m]][val]
            if lossEx[val] != 0:
                num -= lossEx[val]
            if num in cache:
                loss += cache[num]
            else:
                squared = num * num
                loss += squared
                cache[num] = squared
        totalLoss += loss
    print('Loss: ' + str(totalLoss))
    return centroids, assignments, totalLoss

def outputClusters(path, examples, centers, assignments):
    '''
    Output the clusters to the given path.
    '''
    print('Outputting clusters to %s' % path)
    out = open(path, 'w')
    topThreeWords = ['' for i in range(len(centers))]
    for j in range(len(centers)):
        out.write('====== Cluster %s\n' % j)
        out.write('--- Centers:\n')
        sortedCenters = sorted(centers[j].items(), key=lambda kv: kv[1], reverse=True)
        truncatedSortedCenters = sortedCenters[:20]
        for t in range(len(truncatedSortedCenters)):
            if t < 3:
                topThreeWords[j] += truncatedSortedCenters[t][0] + ' '
            k = truncatedSortedCenters[t][0]
            v = truncatedSortedCenters[t][1]
            if v != 0:
                out.write('%s\t%s\n' % (k, v))
        '''
        out.write('--- Assigned points:')
        for i, z in enumerate(assignments):
            if z == j:
                out.write(' '.join(examples[i].keys()))
        '''
    out.close()
    return topThreeWords

def outputGraph(matrix, numClusters, assignments, topThreeWords):
    tsne_lsa_model = TSNE(n_components=2, perplexity=50, learning_rate=100, 
                        n_iter=2000, verbose=1, random_state=0, angle=0.75)
    tsne_lsa_vectors = tsne_lsa_model.fit_transform(matrix)
    centroidCounts = [0 for i in range(numClusters)]
    centroids = [(0,0) for i in range(numClusters)]
    for i in range(len(assignments)):
        centroids[assignments[i]] = (centroids[assignments[i]][0] + tsne_lsa_vectors[i][0], centroids[assignments[i]][1] + tsne_lsa_vectors[i][1])
        centroidCounts[assignments[i]] += 1
    for i in range(len(centroids)):
        centroids[i] = tuple(t/centroidCounts[i] for t in centroids[i])
    colormap = numpy.array([
    "#1f77b4", "#aec7e8", "#ff7f0e", "#ffbb78", "#2ca02c",
    "#98df8a", "#d62728", "#ff9896", "#9467bd", "#c5b0d5",
    "#8c564b", "#c49c94", "#e377c2", "#f7b6d2", "#7f7f7f",
    "#c7c7c7", "#bcbd22", "#dbdb8d", "#17becf", "#9edae5" ])
    colormap = colormap[:numClusters]
    plot = figure(title="t-SNE Clustering of {} LSA Topics".format(numClusters), plot_width=700, plot_height=700)
    for t in range(numClusters):
        label = Label(x=centroids[t][0], y=centroids[t][1], 
                  text=topThreeWords[t], text_color=colormap[t])
        plot.add_layout(label)
    plot.scatter(x=tsne_lsa_vectors[:,0], y=tsne_lsa_vectors[:,1], color=colormap[assignments])
    show(plot)

###########################################################################

matrices = getMatrices()
examples = convertMatricesToExamples(matrices)
numClusters = 8
centroids, assignments, loss = kmeans(examples, numClusters, 100)
topThreeWords = outputClusters('kmeans_clusters_' + str(startYear) + '.txt', examples, centroids, assignments)
for i in range(numClusters):
    print('Cluster ' + str(i) + ': ' + str(assignments.count(i)))
outputGraph(numpy.array(matrices[0]),numClusters,assignments,topThreeWords)