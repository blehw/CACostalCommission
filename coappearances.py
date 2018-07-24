import sys
import csv
import math

inputFile = 'all_data_v3.csv'

with open(inputFile, encoding='ISO-8859-1') as csvFile:
  reader = csv.reader(csvFile)
  headers = next(reader)


  pubAccInd = [85, 86, 87, 88, 89, 90] # indices of Public Access sections 30210, 30211, 30212, 30212.5, 30213, and 30214
  
  # set up 6 by (# sections) matrix
  matrix = []
  for i in range(len(pubAccInd)):
    comparisons = [0] * len(headers[8:])
    matrix.append(comparisons)

  for row in reader:
    pubAccMentioned = [] # 0-5 indices of Public Access sections mentioned in this permit
    for i in range(len(pubAccInd)):
      if row[pubAccInd[i]] == '1':
        pubAccMentioned.append(i)

    # find co-appearances
    if pubAccMentioned != None:
      for i in range(len(row[8:])):
        if row[8+i] == '1':
          for j in range(len(pubAccMentioned)):
            if (8+i != pubAccMentioned[j]+85):
              matrix[pubAccMentioned[j]][i] += 1

  # write into csv

  sections = ['30210', '30211', '30212', '30212.5', '30213', '30214']

  output = open('public_access_co_appearances.csv', 'w')
  writer = csv.writer(output, delimiter = ',')
  indices = []
  minMentioned = 50 # change this num to remove any law that is not mentioned at least this many times in relation with a public access law
  for i in range(len(headers[8:])):
    writeable = False
    for j in range(len(pubAccInd)):
      if matrix[j][i] > minMentioned:
        writeable = True
    if writeable:
      output.write(',' + headers[8+i])
      indices.append(i)
  output.write('\n')

  for i in range(len(sections)):
    print('hello')
    output.write(sections[i])
    for j in indices:
      output.write(',' + str(matrix[i][j]))
    output.write('\n')

  output.close()