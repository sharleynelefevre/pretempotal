# -*- coding: utf-8 -*-
"""
Created on Thu Jun  6 17:53:09 2019

@author: Sharleyne-Lefevre
"""

import os
import codecs
import nltk
import re
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
    modals = ["would", "could", "might", "should"]
    
    # pour remplir le dataframe concordancier
#    dfConcordancier = {}
#    dfConcordancier["SentEv1"] = []
#    dfConcordancier["event1"] = []
#    dfConcordancier["Tense-AspectEv1"] = []
#    dfConcordancier["event2"] = []
#    dfConcordancier["Tense-AspectEv2"] = []   
    
    for fileName, fileContent in files.items():
        sents = nltk.sent_tokenize(fileContent)
        allEventsPairs = []
        for sentence in sents:
            sent = re.findall(r"[\w'#]+|[.,!?;':\"`]", sentence)
            events = []
            for w in range(len(sent)):
                if "#e" in sent[w]:
                    dictEvent = {}
                    eventSplit = sent[w].split('#')
                                     
                    dictEvent['sentence'] = sentence   
                    dictEvent['event-1'] = sent[w-1]
                    dictEvent['event-2'] = sent[w-2]
                    dictEvent['event-3'] = sent[w-3]
                    dictEvent['event-4'] = sent[w-4]
                    dictEvent['fenetre-4'] = [sent[w-1],sent[w-2],sent[w-3],sent[w-4]]
                    dictEvent['event'] = eventSplit[0]
                    dictEvent['event+1'] = sent[w+1]
                    dictEvent['eid'] = eventSplit[1]
                    dictEvent['class'] = eventSplit[2]
                    dictEvent['tense'] = eventSplit[3]
                    dictEvent['aspect'] = eventSplit[4]
                    dictEvent['eiid'] = eventSplit[5]
                    dictEvent['rel'] = eventSplit[6]
                    dictEvent['eventInstanceID'] = eventSplit[7]
                    dictEvent['relatedToEventInstance'] = eventSplit[8]
                
                    events.append(dictEvent)


            for i in range(len(events)-1):
                eventsPairs = []
                eventsPairs.append(events[i])
                eventsPairs.append(events[i+1])
                allEventsPairs.append(eventsPairs)
           

         
        for pair in allEventsPairs:
            dictEventEvent = {}
            
#            sentEv1 = pair[0]['sentence']

            
            event1 = pair[0]['event']
            event2 = pair[1]['event']
            
            eidEvent1 = pair[0]['eid']
            eidEvent2 = pair[1]['eid']
            
            tenseAspectEvent1 = pair[0]['tense']+'-'+pair[0]['aspect']
            tenseAspectEvent2 = pair[1]['tense']+'-'+pair[1]['aspect']
            
            tenseEvent1 = pair[0]['tense']
            tenseEvent2 = pair[1]['tense']
            
            aspectEvent1 = pair[0]['aspect']
            aspectEvent2 = pair[1]['aspect']
            
            classEvent1 = pair[0]['class']
            classEvent2 = pair[1]['class']
            
            wordsBeforeEvent1 = pair[0]['event-4']
            wordsBeforeEvent2 = pair[1]['event-4']
            wordAfterEvent1 = pair[0]['event+1']
            
#            wordEv1Moins1 = pair[0]['event-1']
#            wordEv1Moins2 = pair[0]['event-2']
#            wordEv1Moins3 = pair[0]['event-3']
#            wordEv1Moins4 = pair[0]['event-4']
#            
#            wordEv2Moins1 = pair[1]['event-1']
#            wordEv2Moins2 = pair[1]['event-2']
#            wordEv2Moins3 = pair[1]['event-3']
#            wordEv2Moins4 = pair[1]['event-4']
            
#            if not wordEv1Moins1 in modals and \
#               not wordEv1Moins2 in modals and \
#               not wordEv1Moins3 in modals and \
#               not wordEv1Moins4 in modals and \
#               wordEv2Moins1 in modals or \
#               wordEv2Moins2 in modals or \
#               wordEv2Moins3 in modals or \
#               wordEv2Moins4 in modals :
#                
#               dfConcordancier["SentEv1"].append(sentEv1)
#               dfConcordancier["event1"].append(event1)
#               dfConcordancier["Tense-AspectEv1"].append(tenseAspectEvent1)
#               dfConcordancier["event2"].append(event2)
#               dfConcordancier["Tense-AspectEv2"].append(tenseAspectEvent2)
#
#                        
#            res = pd.DataFrame(dict([(k,pd.Series(v)) for k,v in dfConcordancier.items()]))
#            res.to_csv('CSV/concordancier_tense-aspect_no-modal-Ev1_and_modal-Ev2.csv', sep=';', encoding='utf-8') 
                        
                        
            ### OCCURRENCE ###
            if classEvent1 == 'OCCURRENCE' and classEvent2 == 'OCCURRENCE':
                if tenseEvent1 == 'PAST' and tenseEvent2 == 'PAST':
                    if tenseAspectEvent1 == 'PAST-NONE' and tenseAspectEvent2 == 'PAST-PERFECTIVE' or \
                       tenseAspectEvent1 == 'PRESENT-PERFECTIVE' and tenseAspectEvent2 == 'PAST-PERFECTIVE' or \
                       tenseAspectEvent1 == 'PRESENT-PERFECTIVE' and tenseAspectEvent2 == 'PAST-NONE' or \
                       tenseAspectEvent1 == 'PAST-NONE' and tenseAspectEvent2 == 'PAST-NONE' :
                           
                       relation = '<-'
                       dictEventEvent['relation'] = relation
                    else:
                       relation = '->'
                       dictEventEvent['relation'] = relation
                
                if tenseEvent1 == 'FUTURE' and tenseEvent2 == 'FUTURE':
                    if tenseAspectEvent1 == 'FUTURE-NONE' and tenseAspectEvent2 == 'FUTURE-PERFECTIVE' or \
                       tenseAspectEvent1 == 'FUTURE-PERFECTIVE' and tenseAspectEvent2 == 'FUTURE-NONE':
                       
                       relation = '<-'
                       dictEventEvent['relation'] = relation
                    else:
                       relation = '->'
                       dictEventEvent['relation'] = relation
                        
                if tenseEvent1 == 'PRESENT' and tenseEvent2 == 'PRESENT' or \
                   tenseEvent1 == 'PRESENT' and tenseEvent2 == 'PAST' or \
                   tenseEvent1 == 'PAST' and tenseEvent2 == 'PRESENT' or \
                   tenseEvent1 == 'PRESPART' and tenseEvent2 == 'PRESPART' or \
                   tenseEvent1 == 'PRESPART' and tenseEvent2 == 'PAST' or \
                   tenseEvent1 == 'PAST' and tenseEvent2 == 'PRESPART':
                  
                   if tenseAspectEvent1 == 'PRESENT-NONE' or tenseAspectEvent1 == 'PRESPART-NONE':
                       if tenseAspectEvent2 == 'PAST-PERFECTIVE' or \
                          tenseAspectEvent2 == 'PAST-NONE' or \
                          tenseAspectEvent2 == 'PRESENT-PERFECTIVE':
                              
                          relation = '<-'
                          dictEventEvent['relation'] = relation
                   else:
                       relation = '->'
                       dictEventEvent['relation'] = relation
                
                if tenseEvent1 == 'FUTURE' and tenseEvent2 == 'PRESENT' or tenseEvent1 == 'PRESENT' and tenseEvent2 == 'FUTURE':
                    if tenseAspectEvent1 == 'FUTURE-PERFECTIVE' and tenseAspectEvent2 == 'PRESENT-NONE' or \
                       tenseAspectEvent1 == 'PRESENT-NONE' and tenseAspectEvent2 == 'FUTURE-NONE':
                       
                       relation = '<-'
                       dictEventEvent['relation'] = relation
                    else:
                       relation = '->'
                       dictEventEvent['relation'] = relation

                
            ### REPORTING ###  
            elif classEvent1 == "REPORTING":
                if tenseEvent1 == 'PAST' and tenseEvent2 == 'PAST':
                    if tenseAspectEvent1 == 'PAST-NONE' and tenseAspectEvent2 == 'PAST-NONE':
                        for word in wordsBeforeEvent2:
                            if word in ["would", "could", "might", "should", "and"]:
                                relation = '->'
                                dictEventEvent['relation'] = relation
                            else:
                                relation = '<-'
                                dictEventEvent['relation'] = relation
                else:
                    relation = '<-'
                    dictEventEvent['relation'] = relation
                    
                            
            ### I_ACTION ###          
            elif classEvent1 == "I_ACTION":
                relation = '->'
                dictEventEvent['relation'] = relation
                
                
            ### I_STATE ###     
            elif  classEvent1 == "I_STATE":
                for word in wordsBeforeEvent1:
                    if wordsBeforeEvent1 in modals or \
                       wordsBeforeEvent2 in modals :
                       relation = '->'
                       dictEventEvent['relation'] = relation   
                    else:
                        relation = '<-'
                        dictEventEvent['relation'] = relation
                    
                    
            ### STATE ###        
            elif classEvent2 == "STATE":
                if wordAfterEvent1 == "that" or \
                   wordsBeforeEvent2 in modals :
                   relation = '->'
                   dictEventEvent['relation'] = relation
                else:
                    relation = '<-'
                    dictEventEvent['relation'] = relation
                            
            else:
                relation = '' 
                
            dictEventEvent['filename'] = fileName
            dictEventEvent['ev1'] = event1
            dictEventEvent['idEv1'] = eidEvent1
            dictEventEvent['classEv1'] = classEvent1
            dictEventEvent['tenseEv1'] = tenseEvent1
            dictEventEvent['aspectEv1'] = aspectEvent1
            dictEventEvent['ev2'] = event2
            dictEventEvent['idEv2'] = eidEvent2
            dictEventEvent['classEv2'] = classEvent2
            dictEventEvent['tenseEv2'] = tenseEvent2
        
            for punct in toReplace:
                dictEventEvent['aspectEv2'] = aspectEvent2.replace(punct,'')
            
            dataframe.append(dictEventEvent)
            df = pd.DataFrame(dataframe)
        df.to_csv('CSV/regles_events_tense_class.csv', sep=';', columns=["filename","ev1","idEv1", "classEv1", "tenseEv1", "aspectEv1", "relation", "ev2", "idEv2", "classEv2", "tenseEv2", "aspectEv2"])

extractEventsPairs()