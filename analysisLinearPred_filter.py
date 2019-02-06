import numpy as np
import sys
import csv
import matplotlib.pyplot as plt
import math

csv.field_size_limit(sys.maxsize)
input_file = 'all_data_v3.csv'
DOCUMENT_IND = 0
SECTIONS_START_IND = 8
OUTCOME_IND = 4

# feature is list of sections, 1 for mentioned, 0 for not mentioned
def feature_extractor(row):
    features = []
    #ind = [214,277,246,70,278,209,134,202,244,83,106,218,285,91,32,13,267,210,9,280,239,44,228,155,212,292,90,317,273,293]
    n = 0
    # creates a feature array using the sections + clustering info
    for i in row[SECTIONS_START_IND:]:
        #if n in ind or n > len(row[SECTIONS_START_IND:]) - 21:
        if i == '':
            features.append(0)
        else:
            features.append(float(i))
        n += 1
    #while len(features) != 20:
    #	features.append(0)
    return np.array(features)


def learn_predictor(train_examples, test_examples, num_iters, eta):
    weights = np.zeros(len(train_examples[0][0])-SECTIONS_START_IND).astype(float)
    
    def predictor(row):
        return 1 if np.dot(weights, feature_extractor(row)) > 0 else -1

    maxL = 0

    for i in range(int(num_iters)):
        print("Iteration #:", i)
        for row,value in train_examples:
            features = feature_extractor(row)
            # using hinge loss
            if np.dot(weights, features) * value < 1:
                # update weights
                gradient_loss = -1 * features * value
                weights -= (eta * gradient_loss)
                #print(np.sum(weights))
        print('Training Accuracy:', evaluate_predictor(train_examples, predictor))
        print('Testing Accuracy:', evaluate_predictor(test_examples, predictor))

    #np.savetxt("predictor_weights.txt", weights)
    print('Training Accuracy:', evaluate_predictor(train_examples, predictor))
    print('Testing Accuracy:', evaluate_predictor(test_examples, predictor))

    #ind = (-weights).argsort()[:30]
    #print(ind)

    return weights

def get_top_accept_sections(weights, num_sections):
    inds = (-weights).argsort()[:num_sections]
    with open(input_file, encoding='ISO-8859-1') as input:
        reader = csv.reader(input)
        row = next(reader)
    res = []
    for i in inds:
        res.append(row[i+8])
    return res

def get_top_reject_sections(weights, num_sections):
    inds = (weights).argsort()[:num_sections]
    with open(input_file, encoding='ISO-8859-1') as input:
        reader = csv.reader(input)
        row = next(reader)
    res = []
    for i in inds:
        res.append(row[i+8])
    return res


################################  HELPER FUNCTIONS  ####################################

matrix = np.loadtxt("clusters_data.txt")

# returns an array of (row,value) pairs, where value is +1 for APPROVED and -1 otherwise
def create_examples():
    examples = []
    with open(input_file, encoding='ISO-8859-1') as input:
        reader = csv.reader(input)
        next(reader)
        n = 0
        for row in reader:
            if matrix[n] == 0:
                value = 1 if 'APPROVED' in row[OUTCOME_IND] or 'CONCURRED' in row[OUTCOME_IND] else -1
                examples.append((row, value))
            n += 1
    return np.array(examples)

# Output error rates
def evaluate_predictor(examples, predictor):
    '''
    predictor: a function that takes an x and returns a predicted y.
    Given a list of examples (x, y), makes predictions based on |predict| and returns the fraction
    of misclassiied examples.
    '''
    error = 0
    for row, value in examples:
        if predictor(row) != value:
            error += 1
    return 1 - (1.0 * error / len(examples))

def row_count(filename):
    with open(filename, encoding='ISO-8859-1') as in_file:
        return sum(1 for _ in in_file)

#######################################################################################

def main(args):
    num_rows = row_count(input_file)
    examples = create_examples()
    #learn_predictor(train_examples, test_examples, feature_extractor, num_iters, eta)
    np.random.shuffle(examples)
    train_examples = examples[:9*num_rows//10]
    test_examples = examples[9*num_rows//10:]
    num_iters = 100
    eta = 0.001
    weights = learn_predictor(train_examples, test_examples, num_iters, eta)
    top_accept_sections = get_top_accept_sections(weights, 10) # gets sections with highest weights
    top_reject_sections = get_top_reject_sections(weights, 10)
    print('Most important sections for acceptances:', top_accept_sections)
    print('Most important sections for rejections:', top_reject_sections)


if __name__ == '__main__':
    args = sys.argv[1:]
    main(args)
