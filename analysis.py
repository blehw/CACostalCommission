import sys
import csv
#pip install matplotlib
import matplotlib.pyplot as plt
import math

csv.field_size_limit(sys.maxsize)

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
  inputFile = 'all_data_v3_w_text_1.csv'
  with open(inputFile, encoding='ISO-8859-1') as input:
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
  return laws, yearlyCounts


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
  sortedCounts = sorted(totalCounts)
  sortedLaws = sorted(countsDictionary, key=countsDictionary.get, reverse=True)
  print('Sorted Laws: ')
  print(sortedLaws)
  return sortedCounts, sortedLaws


# STANDARD DEVIATION

def getStandardDevs(laws, yearlyCounts):
  standardDevs = []
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
  print("Standard Deviations by year:")
  print(standardDevs)

#print(sortedLaws)

def graph(laws, counts):
  plt.bar(laws,counts, color='blue')
  plt.show()


def main(args):
  laws, yearlyCounts = getYearlyCounts()
  sortedCounts, sortedLaws = getPopularity(laws, yearlyCounts)
  getStandardDevs(laws, yearlyCounts)
  graph(sortedLaws, sortedCounts)

if __name__ == '__main__':
    args = sys.argv[1:]
    main(args)
