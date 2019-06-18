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
    dataframe = []
    toReplace = ['`','"','.',',','!',':',"'"]  
    
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
        
        for pair in allEventsPairs:
            dictEventEvent = {}
            tenseAspectEvent1 = pair[0][3]+'-'+pair[0][4]
            tenseAspectEvent2 = pair[1][3]+'-'+pair[1][4]
            tenseEvent1 = pair[0][3]
            tenseEvent2 = pair[1][3]
            classEvent1 = pair[0][2]
            classEvent2 = pair[1][2]

            if classEvent1 == 'OCCURRENCE' and classEvent2 == 'OCCURRENCE':
                if tenseEvent1 == 'PAST' and tenseEvent2 == 'PAST':
                    if tenseAspectEvent1 == 'PAST-NONE' and tenseAspectEvent2 == 'PAST-PERFECTIVE' or tenseAspectEvent1 == 'PRESENT-PERFECTIVE' and tenseAspectEvent2 == 'PAST-PERFECTIVE' or tenseAspectEvent1 == 'PRESENT-PERFECTIVE' and tenseAspectEvent2 == 'PAST-NONE' :
                        relation = '<-'
                        dictEventEvent['relation'] = relation
                    else:
                        relation = '->'
                        dictEventEvent['relation'] = relation
                
                if tenseEvent1 == 'FUTURE' and tenseEvent2 == 'FUTURE':
                    if tenseAspectEvent1 == 'FUTURE-NONE' and tenseAspectEvent2 == 'FUTURE-PERFECTIVE' or tenseAspectEvent1 == 'FUTURE-PERFECTIVE' and tenseAspectEvent2 == 'FUTURE-NONE':
                        relation = '<-'
                        dictEventEvent['relation'] = relation
                    else:
                        relation = '->'
                        dictEventEvent['relation'] = relation
                        
                if tenseEvent1 == 'PRESENT' and tenseEvent2 == 'PRESENT' or tenseEvent1 == 'PRESENT' and tenseEvent2 == 'PAST' or tenseEvent1 == 'PAST' and tenseEvent2 == 'PRESENT' or tenseEvent1 == 'PRESPART' and tenseEvent2 == 'PRESPART' or tenseEvent1 == 'PRESPART' and tenseEvent2 == 'PAST' or tenseEvent1 == 'PAST' and tenseEvent2 == 'PRESPART':
                    if tenseAspectEvent1 == 'PRESENT-NONE' or tenseAspectEvent1 == 'PRESPART-NONE':
                        if tenseAspectEvent2 == 'PAST-PERFECTIVE' or tenseAspectEvent2 == 'PAST-NONE' or tenseAspectEvent2 == 'PRESENT-PERFECTIVE':
                            relation = '<-'
                            dictEventEvent['relation'] = relation
                    else:
                        relation = '->'
                        dictEventEvent['relation'] = relation
                
                if tenseEvent1 == 'FUTURE' and tenseEvent2 == 'PRESENT' or tenseEvent1 == 'PRESENT' and tenseEvent2 == 'FUTURE':
                    if tenseAspectEvent1 == 'FUTURE-PERFECTIVE' and tenseAspectEvent2 == 'PRESENT-NONE' or tenseAspectEvent1 == 'PRESENT-NONE' and tenseAspectEvent2 == 'FUTURE-NONE':
                        relation = '<-'
                        dictEventEvent['relation'] = relation
                    else:
                        relation = '->'
                        dictEventEvent['relation'] = relation
            else:
                relation = ''
                
            dictEventEvent['filename'] = fileName
            dictEventEvent['ev1'] = pair[0][0]
            dictEventEvent['idEv1'] = pair[0][1]
            dictEventEvent['classEv1'] = classEvent1
            dictEventEvent['tenseEv1'] = tenseEvent1
            dictEventEvent['aspectEv1'] = pair[0][4]
            dictEventEvent['ev2'] = pair[1][0]
            dictEventEvent['idEv2'] = pair[1][1]
            dictEventEvent['classEv2'] = classEvent2
            dictEventEvent['tenseEv2'] = tenseEvent2
        
            for punct in toReplace:
                dictEventEvent['aspectEv2'] = pair[1][4].replace(punct,'')
            
            dataframe.append(dictEventEvent)
            df = pd.DataFrame(dataframe)
        df.to_csv('CSV/regles_events_tense_class.csv', sep=';', columns=["filename","ev1","idEv1", "classEv1", "tenseEv1", "aspectEv1", "relation", "ev2", "idEv2", "classEv2", "tenseEv2", "aspectEv2"])
extractEventsPairs()