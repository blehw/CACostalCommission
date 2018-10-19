import csv
import sys
import numpy
import math
from scipy import linalg, dot
import string
from nltk.corpus import stopwords
from stemming.porter2 import stem
import re
import random
import collections

numpy.set_printoptions(threshold=numpy.nan)

# this is the column that the text is in
documentColNum = 0
startYear = 1996
endYear = 1996
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
                        if (word not in stopwords) and (word != ''):
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

            print('Performing matrix operations')

            # rotate the matrix so that it is words down and documents across
            rotatedMatrix = [*zip(*matrix)]
            matrices.append(rotatedMatrix)
        return matrices

def convertMatricesToExamples(matrices):
    examples = []
    for matrix in matrices:
        for row in matrix:
            d = {}
            for i in range(len(row)):
                d[i] = row[i]
            examples.append(d)
    return examples

matrices = getMatrices()
examples = convertMatricesToExamples(matrices)