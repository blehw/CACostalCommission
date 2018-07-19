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
            if 8+i != j+85:
              matrix[pubAccMentioned[j]][i] += 1
  print(matrix)

  # write into csv