import csv
import numpy as np
import re
import math
from nltk.corpus import stopwords
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.manifold import TSNE
from bokeh.plotting import figure, output_file, show
from bokeh.models import Label
from bokeh.io import output_notebook

inputFile = 'all_data_v3.csv'
documentColNum = 2
startYear = 2016
endYear = 2016
yearColNum = 1
wordsToAnalyze = 1500

allPopularWords = {}
for n in range(startYear, endYear + 1):
    fileName ='lsa_words/lsa_popular_words_.txt'
    #fileName = 'lsa_words/lsa_popular_words_' + str(n) + '.txt'
    with open(fileName) as f:
        yearPopularWords = f.read().splitlines()
    # look at only the top 400 words
    yearPopularWords = yearPopularWords[:wordsToAnalyze]
    allPopularWords[n] = yearPopularWords

regex = re.compile('[^a-zA-Z]')
stopwords = stopwords.words('english')

n_topics = 500
lda_model = LatentDirichletAllocation(n_components=n_topics,learning_method='online',random_state=0, verbose=0)

def getMatrices():

    matrices = []
    with open(inputFile, encoding='ISO-8859-1') as csvFile:
        for n in range(startYear, endYear + 1):
            csvFile.seek(0)
            reader = csv.reader(csvFile)

            #print(len(popularWords[n]))

            print('Constructing tf-idf matrix')

            '''
            popularWords = allPopularWords[n]

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
                # this is the weiging value for each term
                #print(popularWords[i] + " " + str(idf))

            csvFile.seek(0)
            reader = csv.reader(csvFile)

            matrixList = []

            for tfList in tfs:
                tfidfList = [0 for i in range(len(popularWords))]
                for i in range(len(tfList)):
                    tfidfList[i] = tfList[i] * idfList[i]
                matrixList.append(tfidfList)
            
            matrix = np.array(matrixList)
            '''

            # our list containing inverse document frequency values
            popularWords = allPopularWords[n]
            #row_count = sum(1 for row in reader if row[yearColNum] == str(n))
            row_count = sum(1 for row in reader)

            idfList = np.zeros((len(popularWords)))
            matrix = np.zeros((row_count,len(popularWords)))
            numDocs = 0

            csvFile.seek(0)
            reader = csv.reader(csvFile)

            i = 0
            for row in reader:
                #if row[yearColNum] == str(n):
                usedWords = []
                for w in row[documentColNum].split():
                    word = regex.sub('', w.lower())
                    if (word not in stopwords) and (word != '') and (word in popularWords):
                        matrix[i][popularWords.index(word)] += 1
                        if word not in usedWords:
                            idfList[popularWords.index(word)] += 1
                            usedWords.append(word)
                numDocs += 1
                i += 1

            idfs = np.full((len(popularWords)),numDocs)
            idfs = np.log(np.divide(idfs, idfList))
            matrix = np.multiply(matrix,idfs)

            matrices.append(matrix)

            np.savetxt("all_data/tf-idf_all_years.txt", matrix)
    csvFile.close()
    return matrices

def getPopularWords(matrix, keys, n_topics, n_words, write_words, year):
    path = open('lda_words/lda_words.txt', 'w')
    #path = open('lda_words/lda_words_' + str(year) + '.txt', 'w')
    topWords = []
    centers = []
    popWords = np.zeros((n_topics, wordsToAnalyze))
    #print(matrix.shape)
    #print(popWords.shape)
    # popWords = np.zeros((n_topics, len(allPopularWords[year])))
    for i in range(matrix.shape[0]):
        #print(matrix.shape)
        popWords[keys[i]] += matrix[i]
    for word_keys in popWords:
        #print(word_keys)
        ind = (-word_keys).argsort()[:write_words]
        #print(word_keys)
        #print(ind)
        #ind = np.argpartition(word_keys, -write_words)[-write_words:]
        #print(ind)
        #print(secondInd)
        center = np.mean(word_keys)
        out = ''
        outStr = ''
        for i in range(write_words):
            out += allPopularWords[year][ind[i]] + ' '
        for i in range(n_words):
            outStr += allPopularWords[year][ind[i]] + ' '
        topWords.append(outStr)
        #print(out)
        path.write(out)
    return topWords

def getMeanTopicVectors(lda_keys, tsne_lda_vectors):
    means = [[0,0] for x in range(len(lda_keys))]
    counts = [0 for x in range(len(lda_keys))]
    for i in range(len(lda_keys)):
        means[lda_keys[i]][0] += tsne_lda_vectors[i][0]
        means[lda_keys[i]][1] += tsne_lda_vectors[i][1]
        counts[lda_keys[i]] += 1
    for i in range(len(means)):
        means[i][0] = means[i][0] / counts[0]
        means[i][1] = means[i][1] / counts[1]
    return means

matrices = getMatrices()
for num_matrix in range(len(matrices)):
    print("Doing stuff")
    lda_topic_matrix = lda_model.fit_transform(matrices[num_matrix])
    np.savetxt("clusters_scores.txt", lda_topic_matrix)
    print(lda_topic_matrix.shape)
    print("Max")
    lda_keys = np.argmax(lda_topic_matrix,axis=1)
    #np.savetxt("clusters_data.txt", lda_keys)
    top_n_words_lda = getPopularWords(matrices[num_matrix], lda_keys, n_topics, 6, wordsToAnalyze, num_matrix + startYear)
    tsne_lda_model = TSNE(n_components=2, perplexity=50, learning_rate=100, n_iter=2000, verbose=1, random_state=0, angle=0.75)
    tsne_lda_vectors = tsne_lda_model.fit_transform(lda_topic_matrix)
    lda_mean_topic_vectors = getMeanTopicVectors(lda_keys,tsne_lda_vectors)

    plot = figure(title="t-SNE Clustering of {} LDA Topics in {}".format(n_topics, str(startYear + num_matrix)), plot_width=700, plot_height=700)
    colormap = np.array([
        "#1f77b4", "#aec7e8", "#ff7f0e", "#ffbb78", "#2ca02c",
        "#98df8a", "#d62728", "#ff9896", "#9467bd", "#c5b0d5",
        "#8c564b", "#c49c94", "#e377c2", "#f7b6d2", "#7f7f7f",
        "#c7c7c7", "#bcbd22", "#dbdb8d", "#17becf", "#9edae5" ])
    colormap = colormap[:n_topics]
    plot.scatter(x=tsne_lda_vectors[:,0], y=tsne_lda_vectors[:,1], color=colormap[lda_keys])

    for t in range(n_topics):
        label = Label(x=lda_mean_topic_vectors[t][0], y=lda_mean_topic_vectors[t][1], 
                      text=top_n_words_lda[t], text_color=colormap[t])
        plot.add_layout(label)
    output_file("lda_all_years.html")
    show(plot)