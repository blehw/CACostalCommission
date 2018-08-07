import sys
import csv
#pip install matplotlib
import matplotlib.pyplot as plt
import math
from statistics import mode

csv.field_size_limit(sys.maxsize)
inputFile = 'all_data_v3.csv'
rows = 0

def rowCount(filename):
	with open(filename, encoding='ISO-8859-1') as in_file:
		return sum(1 for _ in in_file)

def isLaw(s):
	try:
		float(s)
		return True
	except ValueError:
		return False

def getYearlyCounts():
	with open(inputFile, encoding='ISO-8859-1') as input:
		reader = csv.reader(input)
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
			if (row[1] != year) or (reader.line_num == rows):
				yearlyCounts.append(counts[:])
				year = row[1]
				for i in range(0, len(counts)):
					counts[i] = 0
			for value in columns:
				if (row[value] != '0'):
					counts[value - columns[0]] += int(row[value])
		return columns, laws, yearlyCounts

# POPULARITY

#sortedLaws prints out a list of the most popular laws, in descending order
def getPopularity(laws, yearlyCounts):
	totalCounts = [0] * len(yearlyCounts[0])
	for year in yearlyCounts:
		for i in range(0, len(year)):
			totalCounts[i] += year[i]

	countsDictionary = {}
	for i in range(0, len(laws)):
		countsDictionary[laws[i]] = totalCounts[i]
	sortedCounts = sorted(totalCounts, reverse = True)
	sortedLaws = sorted(countsDictionary, key=countsDictionary.get, reverse=True)

	print('Sorted Laws by Popularity: ')
	# top 30
	print(sortedCounts[:60])
	print(sortedLaws[:60])
	return sortedCounts[:60], sortedLaws[:60]


# STANDARD DEVIATION

def getStandardDevs(laws, yearlyCounts):
	standardDevs = []
	sdAsPercentage = []
	for i in range(len(laws)):
	# calculate mean for this ith law
		countSum = 0
		for year in yearlyCounts:
			countSum += year[i]
		mean = countSum / len(yearlyCounts)
		squaredDiffSum = 0
		for year in yearlyCounts:
			squaredDiffSum += (year[i] - mean)**2
		variance = squaredDiffSum / len(yearlyCounts)
		standardDevs.append(math.sqrt(variance))
		if (mean != 0):
			sdAsPercentage.append(math.sqrt(variance) / mean)
		else:
			sdAsPercentage.append(0)

	sdDictionary = {}
	for i in range(0, len(laws)):
		sdDictionary[laws[i]] = sdAsPercentage[i]
	sortedSD = sorted(sdAsPercentage, reverse = True)
	sortedSDLaws = sorted(sdDictionary, key=sdDictionary.get, reverse=True)

	print("Sorted Laws by Standard Deviation as a Percentage:")
	print(sortedSD[:60])
	print(sortedSDLaws[:60])
	return sortedSD[:60], sortedSDLaws[:60]

def graph(laws, counts):
	plt.rcParams.update({'font.size': 8})
	plt.figure(figsize=(18,7))
	plt.bar(laws,counts, color='blue')
	plt.xticks(rotation=90)
	plt.show()

def nbcTrain(columns, laws, file):
	subDescriptions = []
	subDtypes = []
	with open('Handcode.csv', encoding='ISO-8859-1') as input:
		reader = csv.reader(input)
		next(reader)
		for row in reader:
			if row[11] != 'NA':
				subDescriptions.append(row[11])
				handCode = []
				for i in range(2, 5):
					handCode.append(row[i])
				if len(set(handCode)) == len(handCode):
					subDtypes.append(int(handCode[0]))
				else:
					subDtypes.append(int(mode(handCode)))

	with open(inputFile, encoding='ISO-8859-1') as input:
		# magic numbers
		types = 13
		handCodeTypes = 12
		typeColumn = 6
		outcomeColumn = 4
		trainNum = 800
		totalInstances = rows - trainNum

		reader = csv.reader(input)
		# number of values in each training instance
		inputs = len(laws) + types + handCodeTypes
		next(reader)

		# counts of true/false for column based on accepted/other
		counts = [[0,0,0,0] for i in range(inputs)]

		for case in reader:
			if reader.line_num > trainNum:
				# outcome variable is 0 if rejected, 1 if approved
				outcomeStr = case[outcomeColumn]
				outcome = 0
				if 'APPROVED' in outcomeStr:
					outcome = 1

				# get the type
				typeNum = int(case[typeColumn])
				# assign type column to true based on outcome
				if outcome == 0:
					for i in range(types):
						if i != typeNum - 1:
							counts[i][0] += 1
						else:
							counts[i][1] += 1
				else:
					for i in range(types):
						if i != typeNum - 1:
							counts[i][2] += 1
						else:
							counts[i][3] += 1

				# get the description
				description = case[2]
				for i in range(len(subDescriptions)):
					if subDescriptions[i] in description:
						#print(subDtypes[i])
						#subDescriptions.remove(subDescriptions[i])
						handCodeTypeNum = subDtypes[i]
						if outcome == 0:
							for j in range(handCodeTypes):
								if j != handCodeTypeNum - 1:
									counts[types + j][0] += 1
								else:
									counts[types + j][1] += 1
						else:
							for j in range(handCodeTypes):
								if j != handCodeTypeNum - 1:
									counts[types + j][2] += 1
								else:
									counts[types + j][3] += 1

				# loop through bylaws, increment values based on outcome
				num = types + handCodeTypes
				for i in columns:
					if outcome == 0:
						if case[i] == '0':
							counts[num][0] += 1
						else:
							counts[num][1] += 1
					else:
						if case[i] == '0':
							counts[num][2] += 1
						else:
							counts[num][3] += 1
					num += 1

		# divide by total rows to get percentages, with laplace estimators
		# if a value is 0, add 1 to it (so its not 'impossible')
		mles = [[0,0,0,0] for i in range(inputs)]
		for i in range(inputs):
			table = counts[i]

			if (table[0] != 0):
				mles[i][0] = table[0] / (totalInstances - 1)
			else:
				mles[i][0] = (table[0] + 1) / (totalInstances+ 1)

			if (table[1] != 0):
				mles[i][1] = table[1] / (totalInstances - 1)
			else:
				mles[i][1] = (table[1] + 1) / (totalInstances + 1)

			if (table[2] != 0):
				mles[i][2] = table[2] / (totalInstances - 1)
			else:
				mles[i][2] = (table[2] + 1) / (totalInstances + 1)

			if (table[3] != 0):
				mles[i][3] = table[3] / (totalInstances - 1)
			else:
				mles[i][3] = (table[3] + 1) / (totalInstances + 1)

		return mles

def nbcPred(columns, laws, file, mles):
	subDescriptions = []
	subDtypes = []
	with open('Handcode.csv', encoding='ISO-8859-1') as input:
		reader = csv.reader(input)
		next(reader)
		for row in reader:
			if row[11] != 'NA':
				subDescriptions.append(row[11])
				handCode = []
				for i in range(2, 5):
					handCode.append(row[i])
				if len(set(handCode)) == len(handCode):
					subDtypes.append(int(handCode[0]))
				else:
					subDtypes.append(int(mode(handCode)))

	with open(inputFile, encoding='ISO-8859-1') as input:
		# magic numbers
		types = 13
		handCodeTypes = 12
		typeColumn = 6
		outcomeColumn = 4
		trainNum = 800

		reader = csv.reader(input)
		# number of values in each training instance
		inputs = len(laws) + types + handCodeTypes
		next(reader)

		tested0 = 0
		tested1 = 0
		correct0 = 0
		correct1 = 0

		accepted = 0

		x = 0

		for case in reader:
			if reader.line_num <= trainNum:
				# outcome variable is 0 if rejected, 1 if approved
				outcomeStr = case[outcomeColumn]
				outcome = 0
				if 'APPROVED' in outcomeStr:
					outcome = 1

				num = types + handCodeTypes
				pred0 = 1
				pred1 = 1

				typeNum = int(case[typeColumn])

				# include this line to only test for type 1s
				# if (typeNum == 1):

				# probability for type
				p0 = mles[typeNum - 1][1] / (mles[typeNum - 1][0] + mles[typeNum - 1][1])
				p1 = mles[typeNum - 1][3] / (mles[typeNum - 1][2] + mles[typeNum - 1][3])

				pred0 = pred0 * p0
				pred1 = pred1 * p1

				description = case[2]
				for i in range(len(subDescriptions)):
					if subDescriptions[i] in description:
						print(description)
						x += 1
						handCodeTypeNum = subDtypes[i] + types
						p0 = (mles[handCodeTypeNum - 1][1] / (mles[handCodeTypeNum - 1][0] + mles[handCodeTypeNum - 1][1]))
						p1 = (mles[handCodeTypeNum - 1][3] / (mles[handCodeTypeNum - 1][2] + mles[handCodeTypeNum - 1][3]))
						pred0 = pred0 * p0
						pred1 = pred1 * p1

				# loop through rest of probabilities
				for i in columns:
					if case[i] == '0':
						p0 = mles[num][0] / (mles[num][0] + mles[num][1])
						p1 = mles[num][2] / (mles[num][2] + mles[num][3])
						pred0 = pred0 * p0
						pred1 = pred1 * p1
					else:
						p0 = mles[num][1] / (mles[num][0] + mles[num][1])
						p1 = mles[num][3] / (mles[num][2] + mles[num][3])
						pred0 = pred0 * p0
						pred1 = pred1 * p1
					num+=1

				# test if our prediction is correct
				if (pred0 > pred1):
					if (outcome == 0):
						correct0+=1
					tested0 +=1
				else:
					if (outcome == 1):
						correct1+=1

					# find the ones we expected to be approved but were denied (for type 1)
					# these are lines 3, 476, and 709 in the csv
					# single family residence construction, creation of huge 401 acre space, and saving a boardwalk, respectively
					
					# for not type 1, the ones we expect to be approved but were not are
					# 37, 193, and 245
					else:
						if 'DENIED' in outcomeStr:
							print(str(reader.line_num) + " " + outcomeStr)
					tested1 +=1

				if (outcome == 1):
					accepted += 1

		testedO = tested0 + tested1
		correctO = correct0 + correct1
		acc = correctO / testedO
		acceptedPerc = accepted / testedO
		print(x)
		string = "Class 0: predicted " + str(tested0) + ", correctly classified " + str(correct0) +"\n"
		string+= "Class 1: predicted " + str(tested1) + ", correctly classified " + str(correct1) +"\n"
		string+= "Overall: predicted " + str(testedO) + ", correctly classified " + str(correctO) +"\n"
		string+= "Accuracy = " + str(acc) +"\n"
		string+= "Percent accepted = " + str(acceptedPerc)
		return string

def main(args):
	global rows
	rows = rowCount('all_data_v3.csv')
	columns, laws, yearlyCounts = getYearlyCounts()
	#sortedCounts, sortedLaws = getPopularity(laws, yearlyCounts)
	#sortedSD, sortedSDLaws = getStandardDevs(laws, yearlyCounts)
	#graph(sortedLaws, sortedCounts)
	#graph(sortedSDLaws, sortedSD)
	print(nbcPred(columns, laws, inputFile, nbcTrain(columns, laws, inputFile)))

if __name__ == '__main__':
	args = sys.argv[1:]
	main(args)
