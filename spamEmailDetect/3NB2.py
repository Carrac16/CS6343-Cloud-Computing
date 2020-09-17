#!/usr/bin/env python
# coding: utf-8

# In[11]:


import numpy as np
import math
import os

# create an array to store V
wordcount = {}

spamCount = 0
hamCount = 0

# make sure concatHam.txt and concatSpam.txt is empty
open('concatSpam.txt', 'w').close()
open('concatHam.txt', 'w').close()

# CONCATENATE TEXT OF ALL DOCS IN CLASS
with open('concatHam.txt', 'w') as outfile:
    for fname in  os.listdir("train/ham"):
        hamCount += 1
        with open("train/ham/"+fname,errors='ignore') as infile:
            for line in infile:
                outfile.write(line)
        outfile.write('\n')
        #infile.close()
outfile.close()
print("concat ham done!")

with open('concatSpam.txt', 'w') as outfile:
    for fname in  os.listdir("train/spam"):
        spamCount += 1
        with open("train/spam/"+fname,errors='ignore') as infile:
            for line in infile:
                outfile.write(line)
        outfile.write('\n')
        #infile.close()
outfile.close()
print("concat spam done!")

# find the prior
hamPrior = hamCount/(hamCount+spamCount)
spamPrior = spamCount/(hamCount+spamCount)


# count token of term
from collections import Counter

with open("concatHam.txt") as f:
    wordcountHam = Counter(f.read().split())
    

with open("concatSpam.txt") as f:
    wordcountSpam = Counter(f.read().split())
    
# combine the two wordCount Counter to V
V = []
for key in wordcountHam:
    V.append(key)
for key in wordcountSpam:
    if key not in V:
        V.append(key)
        
        
# cond prob of ham and spam
condprob = {}
condprob["spam"] = []
condprob["ham"] = []
Tct_ham = 0
Tct_spam = 0

# sum of Tct ham and Tct spam
for t in wordcountHam:
    Tct_ham += wordcountHam[t]

for t in wordcountSpam:
    Tct_spam += wordcountSpam[t]


# cond prob of ham
for t in V:
    tempvalue = 0
    if t in wordcountHam:
        tempvalue = (wordcountHam[t]+1)/(Tct_ham-(wordcountHam[t]+1)+len(V))
        condprob["ham"].append(tempvalue)
    else:
        tempvalue = 1/(Tct_ham-(wordcountHam[t]+1)+len(V))
        condprob["ham"].append(tempvalue)

# cond prob of spam
for t in V:
    tempvalue = 0
    if t in wordcountSpam:
        tempvalue = (wordcountSpam[t]+1)/(Tct_spam-(wordcountSpam[t]+1)+len(V))
        condprob["spam"].append(tempvalue)
    else:
        tempvalue = 1/(Tct_spam-(wordcountSpam[t]+1)+len(V))
        condprob["spam"].append(tempvalue) 

print("conditional probablity done!")

    
# output is V, hamPrior, spamPrior, condprob["ham"], condprob["spam"]


# In[12]:


# debugging codes
#print (len(V))
#print (hamPrior)
#print (spamPrior)
#print(len(condprob["ham"]))
#print(len(condprob["spam"]))


# In[13]:


# testing
# this function will test if mail is spam or ham using NB, input path to file, return boolean.
def NBtest(str):
    # create W
    W=[]
    file = open(str,errors='ignore')
    for line in file:
        for word in line.split():
            if word not in W:
                W.append(word)
    # initialize score
    hamScore = math.log(hamPrior)
    spamScore = math.log(spamPrior)
    
    # add to score for ham and spam
    for word in W:
        if word in V:
            location = V.index(word)
            hamScore += math.log(condprob["ham"][location])
            spamScore += math.log(condprob["spam"][location])   
    
    file.close()
    
    # compare score, then return true or false, true is ham, false is spam
    if (hamScore > spamScore):
        return True
    else:
        return False

# ask for a filename that is in the train test folder and make prediction
directory = input("What folder in test is it from? \n") 
filename = input("Please enter the filename:\n")

if (NBtest("test/"+directory+"/"+filename)):
    print("This is most likely a normal email \n")
else:
    print("This is most likely a spam \n")



