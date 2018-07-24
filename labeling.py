import csv
import sys
import nltk

# $ pip install nltk

csv.field_size_limit(sys.maxsize)

inputFile = 'all_data_v3_w_text_1.csv'
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

d = {}
with open(inputFile, encoding='ISO-8859-1') as csvFile:
	reader = csv.reader(csvFile)
	for row in reader:
		tokens = nltk.word_tokenize(row[2])
		tagged = nltk.pos_tag(tokens)
		for tag in tagged:
			if tag[1].startswith('V') or tag[1].startswith('N'):
				if tag[0] in d:
					d[tag[0]] += 1
				else:
					d[tag[0]] = 1

popularWords = sorted(d, key=d.get, reverse=True)
for i in range(100):
	print(popularWords[i])
