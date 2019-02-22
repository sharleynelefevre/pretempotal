# -*- coding: utf-8 -*-
'''
Created on Wed Feb  6 13:22:40 2019

@author: Sharleyne-Lefevre
'''

from __future__ import print_function
import os
import csv
import codecs
from bs4 import BeautifulSoup
from nltk.stem import WordNetLemmatizer
from nltk.stem.porter import *
from nltk.stem import *
from nltk import tokenize
import nltk


def extractFeaturesFromTml():    
    documents = []
    
    # ouverture de chaque fichier du repertoire 
    path = "dev/TBAQ-cleaned/"
    for foldername in os.listdir(path):
        if os.path.isdir(path+foldername):
            for filename in os.listdir(path+foldername):
                if '.tml' in filename:
                    file = codecs.open(path+foldername+'/'+filename, 'r', 'utf8') 
                    # parser le xml
                    soup = BeautifulSoup(file.read(), 'xml') 
                    file.close()

                docId = soup.find('DOCID').text
                
                document = {}
                document['docId'] = docId
                
                # ----------------------------------------------
                #                     EVENTS
                # ----------------------------------------------
                # pour recuperer le stem de chaque event
                stemmer = PorterStemmer()
                # pour recuperer le lemme de chaque event
                lemmatizer = WordNetLemmatizer()   
                
                events = {}
                # recuperation des events
                for eventTag in soup.find_all('EVENT'):
                    event = eventTag.text
                    verb = {}    
                    dictEvent = {}
                    
                    # recuperation des attributs des events + ajout dans dictEvent 
                    dictEvent['eid'] = eventTag.get('eid') 
                    dictEvent['class'] = eventTag.get('class')
                    dictEvent['stem'] = eventTag.get('stem')
                    dictEvent['stemNLTK'] = stemmer.stem(event)

                    # ajout de event dans le dictionnaire verbe
                    verb['libelle'] = event
                    
                    # ajout du dictEvent dans le dictionnaire verbe
                    verb['event'] = dictEvent
                    
                    # ajout du dictionnaire verbe dans le dictionnaire events
                    events[eventTag.get('eid')] = verb

                # on met chaque event dans document, la cle de events est 'verbes'
                document['verbes'] = events
                
                # ----------------------------------------------
                #                  INSTANCES
                # ----------------------------------------------
                for makeinstance in soup.find_all('MAKEINSTANCE'):
                    instance = {}
                    
                    # recuperation des attributs des makeinstances et ajout dans le dictionnaire instance
                    instance['eventid'] = makeinstance.get('eventid')
                    instance['eiid'] = makeinstance.get('eiid')
                    instance['aspect'] = makeinstance.get('aspect')
                    instance['tense'] = makeinstance.get('tense')
                    instance['pos'] = makeinstance.get('pos')
                    instance['polarity'] = makeinstance.get('polarity')
                    instance['modality'] = makeinstance.get('modality') 
                    instance['cardinality'] = makeinstance.get('cardinality')                             
        
                    # on met le dictionnaire instance dans le chemin : document > eid > instance > dictionaire instance
                    # instance a pour cle 'instance'
                    document['verbes'][makeinstance.get('eventID')]['instance'] = instance
                
                for verb in document['verbes']:
                    verb = document['verbes'][verb]
                    event = verb['libelle']
                    
                    # on n'a pas toujours d'instance pour un event
                    # si on en a un
                    if 'instance' in verb.keys():  
                        # on recupere le pos
                        pos = verb['instance']['pos'][0].lower()
                    else :
#                        print(docId + " " + event) # /!\ Events sans instance 
                        # sinon on assigne none au pos des events n'ayant pas d'instance
                        pos = None
                    
                    eid = verb['event']['eid']
                    if not pos in ['u', 'p', 'o', None]:  # NLTK ne prend pas en compte les p et les o (OTHER) et les u (UNKNOWN)
                        document['verbes'][eid]['event']['lemmeNltk'] = lemmatizer.lemmatize(event, pos)
                    else:
                        document['verbes'][eid]['event']['lemmeNltk'] = 'unknown'
                
                # ----------------------------------------------
                #                     TIMEXS
                # ----------------------------------------------        
                timexs = {}
                for timexTag in soup.find_all('TIMEX3'):
                    timex = timexTag.text
                    
                    word = {}
                    dictTimex = {}
                    
                    dictTimex['tid'] = timexTag.get('tid')
                    dictTimex['type'] = timexTag.get('type')
                    dictTimex['value'] = timexTag.get('value') 
                    dictTimex['mod'] = timexTag.get('mod') 
                    dictTimex['temporalFunction'] = timexTag.get('temporalFunction') 
                    dictTimex['functionInDocument'] = timexTag.get('functionInDocument') 
                    dictTimex['beginPoint'] = timexTag.get('beginPoint') 
                    dictTimex['endPoint'] = timexTag.get('endPoint') 
                    dictTimex['quant'] = timexTag.get('quant') 
                    dictTimex['freq'] = timexTag.get('freq') 
                    dictTimex['anchorTimeID'] = timexTag.get('anchorTimeID') 
                    
                    word['libelle'] = timex
                    word['timex'] = dictTimex
                    timexs[timexTag.get('tid')] = word
                
                document['timexs'] = timexs
                
                # ----------------------------------------------
                #                     SIGNAUX
                # ----------------------------------------------        
                signaux = {}
                for signalTag in soup.find_all('SIGNAL'):
                    signal = signalTag.text
                    
                    strSignal = {}
                    dictSignal = {}
                    
                    dictSignal['sid'] = signalTag.get('sid')
                    
                    strSignal['libelle'] = signal
                    strSignal['signal'] = dictTimex
                    signaux[signalTag.get('sid')] = strSignal
                
                document['signaux'] = signaux
                # ajout du document contenant les informations des events qu'il contient
                documents.append(document)

    return documents


def writeCsvEvent(documents):    
    # ouverture du csv en ecriture
    with open('Dev/csv_features_events.csv', 'w', newline='') as f:
        # en-tete des colonnes
        fieldnames = ['Libelle', 'docID', 'eid', 'eiid', 'Class', 'Stem', 'StemNltk', 'LemmeNltk', 'Aspect', 'Tense', 'POS', 'Polarity', 'Modality', 'Cardinality']
        # le writer est au format dictionnaire
        writer = csv.DictWriter(f, fieldnames = fieldnames, delimiter = ';')

        writer.writeheader()
        
        for document in documents:
            for verb in document['verbes']:
                
                verb = document['verbes'][verb]
                if 'instance' in verb.keys():
                    # remplissage des colonnes avec les elements provenant de event et instance + docId
                    writer.writerow({'docID' : document['docId'], 
                                     'Libelle' : verb['libelle'],
                                     'eid' : verb['event']['eid'],
                                     'Class' : verb['event']['class'],
                                     'Stem' : verb['event']['stem'],
                                     'StemNltk' : verb['event']['stemNLTK'],
                                     'LemmeNltk' : verb['event']['lemmeNltk'], 
                                     'eiid' : verb['instance']['eiid'],
                                     'Aspect' : verb['instance']['aspect'],
                                     'Tense' : verb['instance']['tense'],
                                     'POS' : verb['instance']['pos'],
                                     'Polarity' : verb['instance']['polarity'],
                                     'Modality' : verb['instance']['modality'],
                                     'Cardinality' : verb['instance']['cardinality']})

    f.close()


def writeCsvTimex(documents):    
    with open('Dev/csv_features_timex.csv', 'w', newline='') as f:
        fieldnames = ['Libelle', 'docID', 'tid', 'Type', 'Value', 'Mod', 'temporalFunction', 'functionInDocument', 'beginPoint', 'endPoint', 'quant', 'freq', 'anchorTimeID']
        writer = csv.DictWriter(f, fieldnames = fieldnames, delimiter = ';')

        writer.writeheader()
        
        for document in documents:
            for word in document['timexs']:
                word = document['timexs'][word]
                writer.writerow({'docID' : document['docId'], 
                                 'Libelle' : word['libelle'],
                                 'tid' : word['timex']['tid'],
                                 'Type' : word['timex']['type'],
                                 'Value' : word['timex']['value'],
                                 'Mod' : word['timex']['mod'],
                                 'temporalFunction' : word['timex']['temporalFunction'],
                                 'functionInDocument' : word['timex']['functionInDocument'],
                                 'beginPoint' : word['timex']['beginPoint'],
                                 'endPoint' : word['timex']['endPoint'],
                                 'quant' : word['timex']['quant'],
                                 'freq' : word['timex']['freq'],
                                 'anchorTimeID' : word['timex']['anchorTimeID']})

    f.close()

# En cours : csv signaux / ajout context     
    
documents = extractFeaturesFromTml()
writeCsvEvent(documents)
writeCsvTimex(documents)
