#!/usr/bin/env python
# coding: utf-8

from flask import Flask
import requests
import json
import time
from collections import Counter

app = Flask(__name__)

counters = {}

def process_emails(flow_id):
  post_obj = {'flow_id': flow_id}
  response = requests.post('http://cluster5-2.utdallas.edu:8080/api/queryEmailFlow', data = post_obj)

  json_array = json.loads(response.text)
  email_list = []

  return_string = f"Flow: {flow_id}\n"

  for item in json_array:
    email_details = {"id": None, "flow_id": None, "sender": None, "subject": None, "content": None, "is_spam": None}
    email_details['id'] = item['id']
    email_details['flow_id'] = item['flow_id']
    email_details['sender'] = item['sender']
    email_details['subject'] = item['subject']
    email_details['content'] = item['content']
    email_details['is_spam'] = item['is_spam']
    email_list.append(email_details)

  spamCounter = 0
  hamCounter = 0
  spamWordCounter = 0
  hamWordCounter = 0

  if not email_list:
      return "Database is empty\n"

  for item in email_list:
    if item['is_spam'] == False:
      hamCounter = hamCounter +1;
      hamWordCounter += len(item['content'].strip().split(" "))
    else:
      spamCounter = spamCounter +1;
      spamWordCounter += len(item['content'].strip().split(" "))

  totalEmails = spamCounter + hamCounter
  return_string += f"Total of {str(totalEmails)} emails, {str(spamCounter)} are spams\n"
  return_string += f"Average word count of normal emails is: {str(hamWordCounter/hamCounter)}, average word count of spam emails is: {str(spamWordCounter/spamCounter)}\n\n"

  #######################################################################################
  stopwords = ["a", "about", "above", "above", "across", "after", "afterwards", "again", "against", "all", "almost", "alone", "along", "already", "also","although","always","am","among", "amongst", "amoungst", "amount",  "an", "and", "another", "any","anyhow","anyone","anything","anyway", "anywhere", "are", "around", "as",  "at", "back","be","became", "because","become","becomes", "becoming", "been", "before", "beforehand", "behind", "being", "below", "beside", "besides", "between", "beyond", "bill", "both", "bottom","but", "by", "call", "can", "cannot", "cant", "co", "con", "could", "couldnt", "cry", "de", "describe", "detail", "do", "done", "down", "due", "during", "each", "eg", "eight", "either", "eleven","else", "elsewhere", "empty", "enough", "etc", "even", "ever", "every", "everyone", "everything", "everywhere", "except", "few", "fifteen", "fify", "fill", "find", "fire", "first", "five", "for", "former", "formerly", "forty", "found", "four", "from", "front", "full", "further", "get", "give", "go", "had", "has", "hasnt", "have", "he", "hence", "her", "here", "hereafter", "hereby", "herein", "hereupon", "hers", "herself", "him", "himself", "his", "how", "however", "hundred", "ie", "if", "in", "inc", "indeed", "interest", "into", "is", "it", "its", "itself", "keep", "last", "latter", "latterly", "least", "less", "ltd", "made", "many", "may", "me", "meanwhile", "might", "mill", "mine", "more", "moreover", "most", "mostly", "move", "much", "must", "my", "myself", "name", "namely", "neither", "never", "nevertheless", "next", "nine", "no", "nobody", "none", "noone", "nor", "not", "nothing", "now", "nowhere", "of", "off", "often", "on", "once", "one", "only", "onto", "or", "other", "others", "otherwise", "our", "ours", "ourselves", "out", "over", "own","part", "per", "perhaps", "please", "put", "rather", "re", "same", "see", "seem", "seemed", "seeming", "seems", "serious", "several", "she", "should", "show", "side", "since", "sincere", "six", "sixty", "so", "some", "somehow", "someone", "something", "sometime", "sometimes", "somewhere", "still", "such", "system", "take", "ten", "than", "that", "the", "their", "them", "themselves", "then", "thence", "there", "thereafter", "thereby", "therefore", "therein", "thereupon", "these", "they", "thick", "thin", "third", "this", "those", "though", "three", "through", "throughout", "thru", "thus", "to", "together", "too", "top", "toward", "towards", "twelve", "twenty", "two", "un", "under", "until", "up", "upon", "us", "very", "via", "was", "we", "well", "were", "what", "whatever", "when", "whence", "whenever", "where", "whereafter", "whereas", "whereby", "wherein", "whereupon", "wherever", "whether", "which", "while", "whither", "who", "whoever", "whole", "whom", "whose", "why", "will", "with", "within", "without", "would", "yet", "you", "your", "yours", "yourself", "yourselves", "the", "Subject:", "subject"]

  spam_list = []
  ham_list = []

  spamWords = {}
  hamWords = {}

  for item in email_list:
    if item['is_spam'] == False:
      ham_list.append(item)
    else:
      spam_list.append(item)

  for item in spam_list:
    wordcount = Counter(item['content'].split())
    for word in wordcount:
      if word in spamWords and len(word) > 1 and word not in stopwords and word.isdigit() == False:
        spamWords[word] = spamWords[word] + wordcount[word]
      else:
        spamWords[word] = wordcount[word]

  sort_orders = sorted(spamWords.items(), key=lambda x: x[1], reverse=True)
  return_string += "the top 10 most common words in spam emails after removing stopwords, and numbers\n"
  for item in sort_orders[:10]:
    return_string += f"{item}\n"

  return_string += "\n"

  #####
  for item in ham_list:
    wordcount = Counter(item['content'].split())
    for word in wordcount:
      if word in hamWords and len(word) > 1 and word not in stopwords and word.isdigit() == False:
        hamWords[word] = hamWords[word] + wordcount[word]
      else:
        hamWords[word] = wordcount[word]

  sort_orders = sorted(hamWords.items(), key=lambda x: x[1], reverse=True)
  return_string += "the top 10 most common words in normal emails after removing stopwords, and numbers\n"
  for item in sort_orders[:10]:
    return_string += f"{item}\n"

  #send analytics to webpage
  return return_string


# @app.route('/')
# def get_stats():
#     return process_emails()

@app.route('/', methods = ['POST'])
def get_data():
  data = requests.json
  flow = data["flow_id"]
  if flow in counters:
    counters[flow] += 1
    if (counters[flow] % 10 == 0):
      return process_emails(flow)
  else:
    counters[flow] = 1



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6001)
