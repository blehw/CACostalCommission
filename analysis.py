import sys
import csv

csv.field_size_limit(sys.maxsize)

def rowCount(filename):
    with open(filename) as in_file:
        return sum(1 for _ in in_file)

def isLaw(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

inputFile = 'all_data_v3_w_text_1.csv'
with open(inputFile, 'rb') as input :
  	reader = csv.reader(input)
  	lastLineNum = rowCount(inputFile)
   	headers = next(reader)
   	laws = []
   	counts = []
   	columns = []
   	counter = 0
   	for s in headers:
   		if (isLaw(s)):
   			laws.append(s)
   			counts.append(0)
   			columns.append(counter)
   		counter += 1
   	year = '2016'
   	yearlyCounts = []
   	for row in reader:
   		if (row[1] != year) or (reader.line_num == lastLineNum):
   			yearlyCounts.append(counts[:])
   			year = row[1]
   			for i in range(0, len(counts)):
   				counts[i] = 0
	   	for value in columns:
	   		if (row[value] != '0'):
	   			counts[value - columns[0]] += int(row[value])

	#sortedLaws prints out a list of the most popular laws, in descending order
	totalCounts = [0] * len(yearlyCounts[0])
	for year in yearlyCounts:
		for i in range(0, len(year)):
			totalCounts[i] += year[i]
	
	countsDictionary = {}
	for i in range(0, len(laws)):
		countsDictionary[laws[i]] = totalCounts[i]
	sortedLaws = sorted(countsDictionary, key=countsDictionary.get, reverse=True)
	print(sortedLaws)
