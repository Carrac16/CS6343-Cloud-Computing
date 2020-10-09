import math
import os
import timeit
from collections import Counter
import pickle
import socketserver
import sys

TRAINED_DATA_FILE = 'trained_data.pkl'

if len(sys.argv) != 3:
    print('Error! Expected arguments python emailServer.py <spam_detection_host> <spam_detection_port>', file=sys.stderr)
    exit(0)

with open(TRAINED_DATA_FILE, 'rb') as pickle_file:
    ham_cond_probability, spam_cond_probability, spam_prior, ham_prior, ham_size, spam_size, vocabulary_size, stopwords_list = pickle.load(pickle_file)


forward_host = sys.argv[1]
forward_port = int(sys.argv[2])


SERVER_HOST = "0.0.0.0"
SERVER_PORT = 5002

BUFFER_SIZE = 4096
SEPARATOR = " "


'''def trainNB(filter_stopwords=False):
    stopwords_list = []

    if filter_stopwords:
        with open('stopwords.txt', 'r') as f:
            stopwords_list.extend(f.read().split())

    ham_vocabulary = Counter()
    spam_vocabulary = Counter()
    ham_prior = 0
    spam_prior = 0

    # get words and counts for spam and ham

    for filename in os.listdir('./train/ham'):
        ham_prior += 1
        with open('./train/ham/' + filename, 'r', errors='ignore') as f:
            ham_vocabulary.update(filter(lambda x: x not in stopwords_list, f.read().split()))

    for filename in os.listdir('./train/spam'):
        spam_prior += 1
        with open('./train/spam/' + filename, 'r', errors='ignore') as f:
            spam_vocabulary.update(filter(lambda x: x not in stopwords_list, f.read().split()))

    total_examples = ham_prior + spam_prior
    ham_prior = math.log10(float(ham_prior)/total_examples)
    spam_prior = math.log10(float(spam_prior)/total_examples)

    ham_size = sum(ham_vocabulary.values())
    spam_size = sum(spam_vocabulary.values())
    vocabulary_size = len(ham_vocabulary) + len(spam_vocabulary)

    # create conditional probability dictionaries
    ham_cond_probability = {}
    spam_cond_probability = {}

    for word in ham_vocabulary:
        ham_cond_probability[word] = math.log10((ham_vocabulary[word] + 1) / (ham_size + vocabulary_size))
    for word in spam_vocabulary:
        spam_cond_probability[word] = math.log10((spam_vocabulary[word] + 1) / (spam_size + vocabulary_size))

    # save trained probabilities
    with open(TRAINED_DATA_FILE, 'wb') as pickle_file:
        pickle.dump((ham_cond_probability, spam_cond_probability, spam_prior, ham_prior, ham_size, spam_size, vocabulary_size, stopwords_list), pickle_file)


def testNB(filename):

    with open(filename, 'rb') as pickle_file:
        ham_cond_probability, spam_cond_probability, spam_prior, ham_prior, ham_size, spam_size, vocabulary_size, stopwords_list = pickle.load(pickle_file)

    # report accuracy using testing set

    # ham testing
    num_ham = 0
    num_spam = 0

    for filename in os.listdir('./test/ham'):
        with open('./test/ham/' + filename, 'r', errors='ignore') as f:
            ham_probability = ham_prior
            spam_probability = spam_prior
            for word in filter(lambda x: x not in stopwords_list, f.read().split()):
                ham_probability += ham_cond_probability[word] if word in ham_cond_probability else math.log10(1.0 / (ham_size + vocabulary_size))
                spam_probability += spam_cond_probability[word] if word in spam_cond_probability else math.log10(1.0 / (spam_size + vocabulary_size))
            if ham_probability > spam_probability:
                num_ham += 1
            else:
                num_spam += 1

    correct = num_ham
    incorrect = num_spam
    print(f'Ham detection accuracy: {num_ham/(num_spam+num_ham)*100:.3f}%')

    # spam testing
    num_ham = 0
    num_spam = 0

    for filename in os.listdir('./test/spam'):
        with open('./test/spam/' + filename, 'r', errors='ignore') as f:
            ham_probability = ham_prior
            spam_probability = spam_prior
            for word in filter(lambda x: x not in stopwords_list, f.read().split()):
                ham_probability += ham_cond_probability[word] if word in ham_cond_probability else math.log10(1.0 / (ham_size + vocabulary_size))
                spam_probability += spam_cond_probability[word] if word in spam_cond_probability else math.log10(1.0 / (spam_size + vocabulary_size))
            if ham_probability > spam_probability:
                num_ham += 1
            else:
                num_spam += 1

    correct += num_spam
    incorrect += num_ham
    print(f'Spam detection accuracy: {num_spam/(num_spam+num_ham)*100:.3f}%')

    print(f'Total detection accuracy: {correct/(correct+incorrect)*100:.3f}%')
    print(f'Total: {correct+incorrect}, Correct: {correct}, Incorrect: {incorrect}')
'''


def isSpam(text):
    ham_probability = ham_prior
    spam_probability = spam_prior
    for word in filter(lambda x: x not in stopwords_list, text.split()):
        ham_probability += ham_cond_probability[word] if word in ham_cond_probability else math.log10(
            1.0 / (ham_size + vocabulary_size))
        spam_probability += spam_cond_probability[word] if word in spam_cond_probability else math.log10(
            1.0 / (spam_size + vocabulary_size))
    if ham_probability > spam_probability:
        print(f'Ham')
        return False
    else:
        print(f'Spam')
        return True


class serverHandler(socketserver.BaseRequestHandler):
    def handle(self):
        dataRead = True
        self.data = ''
        while dataRead:
            dataRead = self.request.recv(BUFFER_SIZE).decode()
            self.data += dataRead
        # print(f'{self.client_address[0]}:{self.client_address[1]} sent a message.')
        # self.data contains processed email
        spam = isSpam(self.data)
        # send self.data + spam to database


server = socketserver.TCPServer((SERVER_HOST, SERVER_PORT), serverHandler)
print('[+] Starting email receiver server')
server.serve_forever()
