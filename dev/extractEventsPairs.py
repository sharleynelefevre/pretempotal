# -*- coding: utf-8 -*-
"""
Created on Thu Jun  6 17:53:09 2019

@author: Sharleyne-Lefevre
"""

import os
import codecs
import nltk
import pandas as pd

def openFilesTXT():
    path = 'ressources/TBAQ-txt-Tps-Aspect-Class/'
    texts = {}
    for foldername in os.listdir(path):
        if os.path.isdir(path+foldername):
            for filename in os.listdir(path+foldername):
                if '.txt' in filename:
                    file = codecs.open(path+foldername+'/'+filename, 'r', 'utf8').read()
                    texts[filename.replace(".txt","")] = file
    return texts 

def extractEventsPairs():
    files = openFilesTXT()
    toReplace = ['`','"','.',',','!',':',"'"]
    dataframe = []  
    
    for fileName, fileContent in files.items():
        sents = nltk.sent_tokenize(fileContent)
        allEventsPairs = []
        for sent in sents:
            events = []
            for word in sent.split():
                if "#e" in word:
                    for item in toReplace:
                        word = word.replace(item,'')
                    events.append(word)

            for i in range(len(events)-1):
                eventsPairs = []
                eventsPairs.append(events[i].split("#"))
                eventsPairs.append(events[i+1].split("#"))
                allEventsPairs.append(eventsPairs)

        for pairs in allEventsPairs:
            dictEventEvent = {}
            dictEventEvent['filename'] = fileName
            dictEventEvent['ev1'] = pairs[0][0]
            dictEventEvent['idEv1'] = pairs[0][1]
            dictEventEvent['classEv1'] = pairs[0][2]
            dictEventEvent['tenseEv1'] = pairs[0][3]
            dictEventEvent['aspectEv1'] = pairs[0][4]
            dictEventEvent['ev2'] = pairs[1][0]
            dictEventEvent['idEv2'] = pairs[1][1]
            dictEventEvent['classEv2'] = pairs[1][2]
            dictEventEvent['tenseEv2'] = pairs[1][3]
            
            for punct in toReplace:
                dictEventEvent['aspectEv2'] = pairs[1][4].replace(punct,'')
            
            dataframe.append(dictEventEvent)
            df = pd.DataFrame(dataframe)
        df.to_csv('CSV/regles_events_tense_class.csv', sep=';', columns=["filename","ev1","idEv1", "classEv1", "tenseEv1", "aspectEv1", "ev2", "idEv2", "classEv2", "tenseEv2", "aspectEv2"])
extractEventsPairs()