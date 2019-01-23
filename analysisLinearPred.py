import numpy as np
import sys
import csv
import matplotlib.pyplot as plt
import math

csv.field_size_limit(sys.maxsize)
input_file = 'all_data_v3.csv'
SECTIONS_START_IND = 8
OUTCOME_IND = 4

# feature is list of sections, 1 for mentioned, 0 for not mentioned
def feature_extractor(row):
    features = []
    for i in row[SECTIONS_START_IND:]:
        if i == '':
            features.append(0)
        else:
            features.append(float(i))
    return np.array(features)


def learn_predictor(train_examples, test_examples, num_iters, eta):
    weights = np.zeros(len(train_examples[0][0])-SECTIONS_START_IND).astype(float)
    
    def predictor(row):
        return 1 if np.dot(weights, feature_extractor(row)) > 0 else -1

    for i in range(int(num_iters)):
        for row,value in train_examples:
            features = feature_extractor(row)
            # using hinge loss
            if np.dot(weights, features) * value < 1:
                # update weights
                gradient_loss = -1 * features * value
                weights -= (eta * gradient_loss)
        print('Iteration', i)
        print('Training Error:', evaluate_predictor(train_examples, predictor))
        print('Testing Error:', evaluate_predictor(test_examples, predictor))
        # print(i, weights)

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

# returns an array of (row,value) pairs, where value is +1 for APPROVED and -1 otherwise
def create_examples():
    examples = []
    with open(input_file, encoding='ISO-8859-1') as input:
        reader = csv.reader(input)
        next(reader)
        for row in reader:
            value = 1 if 'APPROVED' in row[OUTCOME_IND] or 'CONCURRED' in row[OUTCOME_IND] else -1
            examples.append((row, value))     
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
    return 1.0 * error / len(examples)

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
    num_iters = 20
    eta = 0.001
    weights = learn_predictor(train_examples, test_examples, num_iters, eta)
    top_accept_sections = get_top_accept_sections(weights, 10) # gets sections with highest weights
    top_reject_sections = get_top_reject_sections(weights, 10)
    print('Most important sections for acceptances:', top_accept_sections)
    print('Most important sections for rejections:', top_reject_sections)
    

if __name__ == '__main__':
    args = sys.argv[1:]
    main(args)
