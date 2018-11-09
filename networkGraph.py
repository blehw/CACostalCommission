import plotly as py
import plotly.graph_objs as go

import networkx as nx

import csv
import numpy
from scipy import linalg, dot, spatial
import matplotlib.pyplot as plt
from stemming.porter2 import stem
import re
import plotly as py
import plotly.graph_objs as go

import networkx as nx

def createGraph(q, year):

	inputFile = 'all_data_w_paragraphs_public_access.csv'

	startYear = year
	endYear = year
	yearColNum = 2

	regex = re.compile('[^a-zA-Z]')

	allPopularWords = []

	for n in range(startYear, endYear + 1):
		wordsFile = 'lsa_popular_words_' + str(n) + '.txt'
		with open(wordsFile) as f:
			popularWords = f.read().splitlines()
		allPopularWords.append(popularWords)

	w = q
	volatilities = []
	topRelatedWords = []
	G=nx.Graph()

	def lsaAnalysis(query, level, maxLevel):
		for n in range(startYear, endYear + 1):
			relatedWords = []
			relatedDists = []

			index = 0

			print(query)

			with open(inputFile, encoding='ISO-8859-1') as csvFile:
				reader = csv.reader(csvFile)
				numDocs = 0
				for row in reader:
					if row[yearColNum] == str(n):
						numDocs += 1

			matrixFile = 'lsa_matrix_' + str(n) + '.txt'

			matrixNums = []
			with open(matrixFile) as f:
				for line in f:
					matrixNums.append(line)
				#matrixNums = f.read().splitlines()
			
			popularWords = allPopularWords[index]

			if query not in popularWords:
				volatilities.append(0)
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
						dists.append(spatial.distance.cosine(matrix[popularWords.index(query)], row))
					else:
						dists.append(1)

				for x in sorted(dists):
					if popularWords[dists.index(x)] not in relatedWords:
						relatedWords.append(popularWords[dists.index(x)])
						relatedDists.append(x)

				if query in relatedWords:
					relatedWords.remove(query)
					relatedDists.remove(0)
				print('Words most related to ' + str(query) + ' in ' + str(n) + ':')
				for i in range(10):
					print(str(relatedWords[i]) + ' ' + str(relatedDists[i]))

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
					# check if negative
					coVariations.append(numpy.std(ranks) / numpy.mean(ranks))

				volatilities.append(numpy.mean(coVariations))

			index += 1

			for i in range(10):
				G.add_edge(query, relatedWords[i], weight=relatedDists[i])

			if level < maxLevel:
				for i in range(10):
					lsaAnalysis(relatedWords[i], level+1,maxLevel)

	lsaAnalysis(w,0,1)

	pos=nx.get_node_attributes(G,'pos')

	dmin=1
	ncenter=0
	for n in pos:
	    x,y=pos[n]
	    d=(x-0.5)**2+(y-0.5)**2
	    if d<dmin:
	        ncenter=n
	        dmin=d

	#p=nx.single_source_shortest_path_length(G,ncenter)
	pos=nx.spring_layout(G)

	edge_trace = go.Scatter(
	    x=[],
	    y=[],
	    line=dict(width=0.5,color='#888'),
	    hoverinfo='none',
	    mode='lines')

	for edge in G.edges():
	    x0, y0 = pos[edge[0]]
	    x1, y1 = pos[edge[1]]
	    edge_trace['x'] += tuple([x0, x1, None])
	    edge_trace['y'] += tuple([y0, y1, None])

	node_trace = go.Scatter(
	    x=[],
	    y=[],
	    text=[],
	    mode='markers+text',
	    textposition='top center',
	    #hoverinfo='text',
	    marker=dict(
	        showscale=True,
	        # colorscale options
	        #'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
	        #'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
	        #'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
	        colorscale='YlGnBu',
	        reversescale=True,
	        color=[],
	        size=10,
	        colorbar=dict(
	            thickness=15,
	            title='Node Connections',
	            xanchor='left',
	            titleside='right'
	        ),
	        line=dict(width=2)))

	for node in G.nodes():
	    x, y = pos[node]
	    node_trace['x'] += tuple([x])
	    node_trace['y'] += tuple([y])
	    node_trace['text']+=tuple([node])

	for node, adjacencies in enumerate(G.adjacency()):
	    node_trace['marker']['color']+=tuple([len(adjacencies[1])])
	    node_info = '# of connections: '+str(len(adjacencies[1]))
	    #node_trace['text']+=tuple([node_info])

	fig = go.Figure(data=[edge_trace, node_trace],
	             layout=go.Layout(
	                title='<br>Network graph of "' + str(w) + '" in ' + str(startYear),
	                titlefont=dict(size=16),
	                showlegend=False,
	                hovermode='closest',
	                margin=dict(b=20,l=5,r=5,t=40),
	                annotations=[ dict(
	                    text="Python code: <a href='https://plot.ly/ipython-notebooks/network-graphs/'> https://plot.ly/ipython-notebooks/network-graphs/</a>",
	                    showarrow=False,
	                    xref="paper", yref="paper",
	                    x=0.005, y=-0.002 ) ],
	                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
	                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))

	f = w + str(startYear)
	py.offline.plot(fig, filename=f)

querys = ['parking']
for y in range(2008, 2017, 4):
	createGraph('parking', y)
createGraph('shoreline', 2016)
createGraph('protective', 2016)

'''
f = plt.figure()
plt.plot(range(startYear, endYear + 1), volatilities)
plt.yticks(numpy.arange(min(volatilities), max(volatilities)+0.1, 0.1))
plt.show()

pdfName = w + '.pdf'
f.savefig(pdfName, bbox_inches='tight')
'''