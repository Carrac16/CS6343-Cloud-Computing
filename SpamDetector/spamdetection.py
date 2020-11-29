import math
import pickle
import socketserver
import requests
import time
import json
from flask import Flask, request

app = Flask(__name__)


TRAINED_DATA_FILE = 'trained_data.pkl'

with open(TRAINED_DATA_FILE, 'rb') as pickle_file:
    ham_cond_probability, spam_cond_probability, spam_prior, ham_prior, ham_size, spam_size, vocabulary_size, stopwords_list = pickle.load(pickle_file)


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
        return False
    else:
        return True


def get_next_components(workflow_id):
    x = requests.post('http://cluster5-1.utdallas.edu:6000/next', data=f'{{"workflow_id": "{workflow_id}", "service_name": "spamdetection"}}')
    response = json.loads(x.text.replace('\'', '"'))
    print(f'response: {response}')
    return response


next_components = {}


@app.route('/', methods=['POST'])
def recieve_email():
    if request.method == 'POST':
        data = request.get_json(force=True)  # always try to parse data as JSON
        data = json.loads(str(data))

        # calculate spam
        spam = isSpam(data['content'])

        # get workflow id
        workflow_id = data['flow_id']

        # form database entry
        data = {'id': str(time.time()), 'flow_id': workflow_id, 'sender': '' if 'sender' not in data else data['sender'], 'subject': '' if 'subject' not in data else data['subject'],
                'content': '' if 'content' not in data else data['content'],
                'is_spam': spam}

        if workflow_id not in next_components:
            next_components[workflow_id] = get_next_components(workflow_id)

        # for component in next_components[workflow_id]:
        for component in next_components[workflow_id]:
            if component['requestType'] == 'POST':
                # get address components
                address = component['address']
                port = component['port']
                endpoint = component['endpoint'] if 'endpoint' in component else '/'

                # send post request
                x = requests.post(f'{address}:{port}{endpoint}', json=data)
                print(f'Sent 1 {"spam" if spam else "ham"} to {address}:{port}{endpoint} on workflow {workflow_id}')


    return ""


if __name__ == '__main__':
    app.run(host=SERVER_HOST, port=SERVER_PORT)

'''class serverHandler(socketserver.BaseRequestHandler):
    def handle(self):
        self.data = ''

        num_spam, num_ham = 0, 0
        next_components = {}

        #while True:
            # read message size
        message_size = self.request.recv(7).decode()
        if len(message_size) > 1:
            if "END" in message_size:
                num_spam, num_ham = 0, 0
                #continue
            # read message
            dataRead = self.request.recv(int(message_size)).decode()
            self.data = dataRead

            # get json from message
            data = json.loads(self.data)

            # calculate spam
            spam = isSpam(data['email'])

            # get workflow id
            workflow_id = data['flow_id']

            # form database entry
            data = {'id': str(time.time()), 'flow_id': workflow_id, 'sender': '', 'subject': data['subject'], 'content': data['email'],
                    'is_spam': spam}

            if workflow_id not in next_components:
                next_components[workflow_id] = get_next_components(workflow_id)

            # for component in next_components[workflow_id]:


            # send to database
            x = requests.post(f'http://cluster5-2.utdallas.edu:8080/api/addEmail', json=data)  # use json=data to automatically convert and include json header
            if json.loads(x.text)['success']:
                print(f'Sent 1 {"spam" if spam else "ham"} to database')
                if spam:
                    num_spam += 1
                else:
                    num_ham += 1



server = socketserver.TCPServer((SERVER_HOST, SERVER_PORT), serverHandler)
print('[+] Starting spam detection server')
server.serve_forever()
'''