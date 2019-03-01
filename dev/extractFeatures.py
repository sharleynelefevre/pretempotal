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
from nltk.tokenize import TweetTokenizer


def openFilesTML():
    # ouverture de chaque fichier du repertoire 
    path = "dev/TBAQ-cleaned/"
    soup = []
    for foldername in os.listdir(path):
        if os.path.isdir(path+foldername):
            for filename in os.listdir(path+foldername):
                if '.tml' in filename:
                    file = codecs.open(path+foldername+'/'+filename, 'r', 'utf8') 
                    # parser le xml
                    soup.append(BeautifulSoup(file.read(), 'xml')) 
                    file.close()
    return soup


def openFilesTXT():
    path = "dev/TBAQ-txt/"
    texts = []
    for foldername in os.listdir(path):
        if os.path.isdir(path+foldername):
            for filename in os.listdir(path+foldername):
                if '.txt' in filename:
                    file = codecs.open(path+foldername+'/'+filename, 'r', 'utf8')         
                    texts.append(file.read())
        
    return texts        
        

def extractInstances(file):
    # recuperation des attributs des makeinstances et ajout dans le dictionnaire instance
    attributes = ['eventID','eiid','aspect','tense','pos','polarity','modality','cardinality']
    
    instances = {}
    
    for makeinstance in file.find_all('MAKEINSTANCE'):
        instance = {}
        
        for attribute in attributes :
            instance[attribute] = makeinstance.get(attribute)
        instances[makeinstance.get('eventID')] = instance
        
    return instances
        
        
def extractEvents(file, document):
    stemmer = PorterStemmer()
    
    instances = extractInstances(file)
    
    events = {}
    # recuperation des events
    for eventTag in file.find_all('EVENT'):
        dictEvent = {}
        event = eventTag.text
        # recuperation des attributs des events + ajout dans le dictionnaire des events 
        dictEvent['eid'] = eventTag.get('eid') 
        dictEvent['class'] = eventTag.get('class')
        dictEvent['stem'] = eventTag.get('stem')
        dictEvent['stemNLTK'] = stemmer.stem(event)

        # creation d'un dictionnaire pour stocker l'event
        verb = {}    
        
        # ajout de event dans le dictionnaire verbe
        verb['libelle'] = eventTag.text
        
        # ajout du dictEvent dans le dictionnaire verbe
        verb['event'] = dictEvent
        
        # creation de l'instance de l'event
        verb['instance'] = instances.get(eventTag.get('eid'))
        
        # creation du lemme de l'event
        verb['lemmeNltk'] = lemmatizeEvent(verb)
        
        # ajout du dictionnaire verbe dans le dictionnaire events
        events[eventTag.get('eid')] = verb
        
    document['verbes'] = events
    

def extractTimex(file, document):
    timexs = {}
    for timexTag in file.find_all('TIMEX3'):
        dictTimex = {}
        
        attributes = ['tid','type','value','mod','temporalFunction','functionInDocument','beginPoint','endPoint','quant','freq','anchorTimeID']
        
        for attribute in attributes :
            dictTimex[attribute] = timexTag.get(attribute)
        
        word = {}
        word['libelle'] = timexTag.text
        word['timex'] = dictTimex
        
        timexs[timexTag.get('tid')] = word
    document['timexs'] = timexs
    
    
def extractSignaux(file, document):
    signaux = {}
    for signalTag in file.find_all('SIGNAL'):
        strSignal = {}
        strSignal['libelle'] = signalTag.text
        strSignal['signal'] = {'sid':signalTag.get('sid')}
        signaux[signalTag.get('sid')] = strSignal
    document['signaux'] = signaux
  
    
def creationDocument(file):
    # recuperation du docId unique au fichier passe en parametre
    docId = file.find('DOCID').text
    # creation d'un dictionnaire document
    document = {}
    document['docId'] = docId
    print(docId)
    
    # Events
    extractEvents(file, document)       
    # Timex     
    extractTimex(file, document)
    # Signaux        
    extractSignaux(file, document)
    return document
    

def extractDocuments():
    # creation d'une liste de documents vide
    documents = []
    # recuperation des fichiers
    files = openFilesTML()
    # parcours des fichiers
    for file in files:
        # creation du document
        document = creationDocument(file)
        # ajout du document dans la liste de documents
        documents.append(document)
        break
#    print('Documents crées \n')
    return documents


def lemmatizeEvent(event):
    # pour recuperer le lemme de chaque event
    lemmatizer = WordNetLemmatizer()
    # on n'a pas toujours d'instance pour un event
    # si on en a un
    if 'instance' in event.keys():  
        # on recupere le temps
        tense = event['instance']['tense']
        # on recupere le pos
        pos = event['instance']['pos'][0].lower()
    else :
#        print(docId + " " + event) # /!\ Events sans instance 
        # sinon on assigne none au pos des events n'ayant pas d'instance
        pos = None
    
    if pos in ['u', 'p', 'o', None]:  # NLTK ne prend pas en compte les p et les o (OTHER), les u (UNKNOWN) et None pour les events sans instance
        if tense == 'NONE':
            pos = 'n'
        else:
            pos = 'v'
            
    return lemmatizer.lemmatize(event['libelle'], pos)


def writeCsvEvent(documents): 
    print('ecriture csv event')
    # ouverture du csv en ecriture
    with open('Dev/CSV/csv_features_events.csv', 'w', newline='') as f:
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
    print('ecriture csv event finie \n')
    f.close()


def writeCsvTimex(documents):
    print('ecriture csv timex')    
    with open('Dev/CSV/csv_features_timex.csv', 'w', newline='') as f:
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
    print('ecriture csv timex finie \n')
    f.close()
    
    
def writeCsvSignal(documents): 
    print('ecriture csv signaux')
    with open('Dev/CSV/csv_features_signal.csv', 'w', newline='') as f:
        fieldnames = ['Libelle', 'docID', 'sid']
        writer = csv.DictWriter(f, fieldnames = fieldnames, delimiter = ';')

        writer.writeheader()
        
        for document in documents:
            for sign in document['signaux']:
                sign = document['signaux'][sign]
                writer.writerow({'docID' : document['docId'], 
                                 'Libelle' : sign['libelle'],
                                 'sid' : sign['signal']['sid']})
    print('ecriture csv signaux finie \n')
    f.close()
     
            
def getContextEvent(): """A AMELIORER"""
    files = openFilesTXT()
    tokenizer = TweetTokenizer()
    
    nbContext = 4 
    testRecupContext = {}
    
    for file in files:
        sents = nltk.sent_tokenize(file)
        for sent in sents:
            tokens = tokenizer.tokenize(sent) 

            i_offset = 0
            for i, t in enumerate(tokens):
                i -= i_offset
                if '#' in t and i > 0:
                    left = tokens[:i-1]
                    joined = [tokens[i - 1] + t]
                    right = tokens[i + 1:]
                    tokens = left + joined + right
                    i_offset += 1
                    
            for word in tokens:
                if '#e' in word:
                    indexEvent = tokens.index(word)
                    testRecupContext['Event-'+str(nbContext)] = tokens[indexEvent-nbContext : indexEvent]
                    testRecupContext['Event+'+str(nbContext)] = tokens[indexEvent+1 : indexEvent+nbContext+1]  
                    print(word)
                    print(testRecupContext)
                    print()
                    
                if '#t' in word:
                    indexEvent = tokens.index(word)
                    testRecupContext['Timex-'+str(nbContext)] = tokens[indexEvent-nbContext : indexEvent]
                    testRecupContext['Timex+'+str(nbContext)] = tokens[indexEvent+1 : indexEvent+nbContext+1]  
                    print(word)
                    print(testRecupContext)
                    print()
                    
                if '#s' in word:
                    indexEvent = tokens.index(word)
                    testRecupContext['Signal-'+str(nbContext)] = tokens[indexEvent-nbContext : indexEvent]
                    testRecupContext['Signal+'+str(nbContext)] = tokens[indexEvent+1 : indexEvent+nbContext+1]  
                    print(word)
                    print(testRecupContext)
                    print()
        break
    
    
extractDocuments()
getContextEvent()    
#writeCsvEvent(documents)
#writeCsvTimex(documents)
#writeCsvSignal(documents)