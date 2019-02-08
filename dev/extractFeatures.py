# -*- coding: utf-8 -*-
"""
Created on Wed Feb  6 13:22:40 2019

@author: Sharleyne-Lefevre
"""
from __future__ import print_function
import os
import csv
import codecs
from bs4 import BeautifulSoup
from nltk.stem import WordNetLemmatizer
from nltk.stem.porter import *
from nltk.stem import *

def extractFeaturesFromTml():
    # chemin du repertoire des fichiers
    path = "C:/Users/Sharleyne-Lefevre/Desktop/stage_LIFO/python/TBAQ-cleaned/TimeBank/" 
    
    documents = []
    # ouverture de chaque fichier du repertoire 
    for filename in os.listdir(path):
        if ".tml" in filename:
            file = codecs.open(path+filename, "r", "utf8") 
            # parser le xml
            soup = BeautifulSoup(file.read(), "lxml")
            file.close()
        
        docId = soup.find('docid').text
        
        document = {}
        document["docId"] = docId
          
        # ----------------------------------------------
        #                     EVENTS
        # ----------------------------------------------
        # pour recuperer le stem de chaque event
        stemmer = PorterStemmer()
        # pour recuperer le lemme de chaque event
        lemmatizer = WordNetLemmatizer()   
        
        events = {}
        # recuperation des events
        for eventTag in soup.find_all('event'):
            event = eventTag.text
            verb = {}    
            dictEvent = {}
            # recuperation des attributs des events + ajout dans dictEvent 
            dictEvent['eid'] = eventTag.get('eid') 
            dictEvent['class'] = eventTag.get('class')
            dictEvent['stem'] = eventTag.get('stem')
            dictEvent['stemNLTK'] = stemmer.stem(event)
            dictEvent['lemmeNLTK'] = lemmatizer.lemmatize(event)
            # ajout de event dans le dictionnaire verbe
            verb['libelle'] = event
            # ajout du dictEvent dans le dictionnaire verbe
            verb['event'] = dictEvent
            # ajout du dictionnaire verbe dans le dictionnaire events
            events[eventTag.get('eid')] = verb
        
        # on met chaque event dans document, la cle de events est "verbes"
        document['verbes'] = events
        
        # ----------------------------------------------
        #                  INSTANCES
        # ----------------------------------------------
        for makeinstance in soup.find_all('makeinstance'):
            dictInstance = {}
            # recuperation des attributs des makeinstances et ajout dans le dictionnaire dictInstance
            dictInstance["eventid"] = makeinstance.get('eventid')
            dictInstance["eiid"] = makeinstance.get('eiid')
            dictInstance["aspect"] = makeinstance.get('aspect')
            dictInstance["tense"] = makeinstance.get('tense')
            dictInstance["pos"] = makeinstance.get('pos')
            dictInstance["polarity"] = makeinstance.get('polarity')
            dictInstance["modality"] = makeinstance.get('modality')
            
            # on met le dictionnaire dictInstance dans le chemin : document > eid > instance > dictInstance
            # dictInstance a pour cle "instance"
            document['verbes'][makeinstance.get('eventid')]['instance'] = dictInstance
        
        # ajout du document contenant les informations des events qu'il contient
        documents.append(document)
    return documents


def display(documents): # permet de mieux visualiser les données sur Python
    for document in documents:
        print("Document : " + str(document["docId"]))
        for verb in document["verbes"]:
            verb = document["verbes"][verb]
            print("\t Libelle  : " + str(verb["libelle"]))
            print("\t Event    : " + str(verb["event"]))
            if "instance" in verb.keys():
                print("\t Instance : " + str(verb["instance"]))
            print()
        print("\n\n")


def writeCSV(documents):
    # chemin du repertoire du fichier csv
    path = "C:/Users/Sharleyne-Lefevre/Desktop/stage_LIFO/python/csv-features.csv" 
    
    # ouverture du csv en ecriture
    with open(path, 'w', newline='') as f:
        # en-tete des colonnes
        fieldnames = ["Libelle", "docID", "eventId", "eventInstanceId", "Class", "Stem", "StemNltk", "LemmeNltk", "Aspect", "Tense", "POS", "Polarity", "Modality"]
        # le writer est au format dictionnaire
        writer = csv.DictWriter(f, fieldnames = fieldnames, delimiter = ';')

        writer.writeheader()
        
        for document in documents:
            for verb in document["verbes"]:
                verb = document["verbes"][verb]
                if "instance" in verb.keys():
                    # remplissage des colonnes avec les elements provenant de event et instance + docId
                    writer.writerow({"docID" : document["docId"], 
                                     "Libelle" : verb["libelle"],
                                     "eventId" : verb["event"]["eid"],
                                     "Class" : verb["event"]["class"],
                                     "Stem" : verb["event"]["stem"],
                                     "StemNltk" : verb["event"]["stemNLTK"],
                                     "LemmeNltk" : verb["event"]["lemmeNLTK"],
                                     "eventInstanceId" : verb["instance"]["eiid"],
                                     "Aspect" : verb["instance"]["aspect"],
                                     "Tense" : verb["instance"]["tense"],
                                     "POS" : verb["instance"]["pos"],
                                     "Polarity" : verb["instance"]["polarity"],
                                     "Modality" : verb["instance"]["modality"]})

    f.close()

documents = extractFeaturesFromTml()
#display(documents) # a decommenter pour voir, dans chaque document, tous les events trouves
writeCSV(documents)