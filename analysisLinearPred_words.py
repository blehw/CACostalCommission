import numpy as np
import sys
import csv
import matplotlib.pyplot as plt
import math
import re
from nltk.corpus import stopwords

csv.field_size_limit(sys.maxsize)
input_file = 'all_data_v3.csv'
DOCUMENT_IND = 2
OUTCOME_IND = 4
f = open("lsa_words/lsa_popular_words_all.txt", "r")
vocab = {}
vocab_ind2word = {}
index = 0
for line in f:
    vocab[line.strip()] = index
    vocab_ind2word[index] = line.strip()
    index += 1
regex = re.compile('[^a-zA-Z]')
stopwords = stopwords.words('english')

# feature is list of sections, 1 for mentioned, 0 for not mentioned
def feature_extractor(row):
    features = np.zeros((len(vocab)))
    # creates a feature array using the sections + clustering info
    for word in row[DOCUMENT_IND].split():
        word = regex.sub('', word.lower())
        if (word not in stopwords) and (word != '') and (word in vocab):
            features[vocab[word]] += 1
    return features


def learn_predictor(train_examples, test_examples, num_iters, eta):
    weights = np.zeros(len(vocab)).astype(float)

    #weights = np.loadtxt("predictor_weights.txt")
    
    def predictor(row):
        return 1 if np.dot(weights, feature_extractor(row)) > 0 else -1

    maxL = 0

    for i in range(int(num_iters)):
        print("Iteration #:", i)
        x = 0
        for row,value in train_examples:
            x += 1
            features = feature_extractor(row)
            # using hinge loss
            if np.dot(weights, features) * value < 1:
                # update weights
                gradient_loss = -1 * features * value
                weights -= (eta * gradient_loss)
        eta = 0.98 * eta
        print(np.sum(weights))
        print('Training Accuracy:', evaluate_predictor(train_examples, predictor))
        print('Testing Accuracy:', evaluate_predictor(test_examples, predictor))

    np.savetxt("words_predictor_weights.txt", weights)
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
        # res.append(row[i+8])
        res.append(vocab_ind2word[i])
    return res

def get_top_reject_sections(weights, num_sections):
    inds = (weights).argsort()[:num_sections]
    with open(input_file, encoding='ISO-8859-1') as input:
        reader = csv.reader(input)
        row = next(reader)
    res = []
    for i in inds:
        # res.append(row[i+8])
        res.append(vocab_ind2word[i])
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
            #if matrix[n] == 0:
            value = -1
            if "APPROVED" in row[OUTCOME_IND] or "CONCURRED" in row[OUTCOME_IND]:
                value = 1
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
    np.random.shuffle(examples)
    # train_examples = examples[:7*num_rows//10]
    # test_examples = examples[7*num_rows//10:]
    train_examples = examples[:9*len(examples)//10]
    test_examples = examples[9*len(examples)//10:]
    num_iters = 100
    eta = 0.001
    weights = learn_predictor(train_examples, test_examples, num_iters, eta)
    top_accept_sections = get_top_accept_sections(weights, 100) # gets sections with highest weights
    top_reject_sections = get_top_reject_sections(weights, 100)
    with open('top_accept_words.txt', 'w') as a:
    	for item in top_accept_sections:
        	a.write("%s\n" % item)
    with open('top_reject_words.txt', 'w') as r:
    	for item in top_reject_sections:
        	r.write("%s\n" % item)
    print('Most important words for acceptances:', top_accept_sections)
    print('Most important words for rejections:', top_reject_sections)
    

if __name__ == '__main__':
    args = sys.argv[1:]
    main(args)