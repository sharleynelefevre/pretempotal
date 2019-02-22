# -*- coding: utf-8 -*-
"""
Created on Wed Feb 20 14:40:39 2019

@author: Sharleyne-Lefevre
"""
import codecs
from nltk.stem.porter import *

def verbocean():
    # ouverture du fichier avec les relations happens-before de verbocean / fichier csv en lecture / fichiers txt en ecriture
    verbocean = codecs.open('dev/happens-before.txt' , 'r')
    commonsEventVerbocean = codecs.open('dev/commonsEventVerbocean.txt', 'w')
    uncommonsEventVerbocean = codecs.open('dev/uncommonsEventVerbocean.txt', 'w')
    
    stemmer = PorterStemmer()
    
    # initialisation de tableaux vides
    libelleEvent = []
    libelleVerbocean = []
    commons = []
    
    # --------------------
    # TODO : synonymes
    # --------------------
    with open('dev/csv_features_events.csv', 'r', newline ='') as csvfile:      
        for line in csvfile:
            if (line.split(';')[0]) != 'Libelle':
                libelleEvent.append(stemmer.stem(line.split(';')[0].lower()))
        
    for verb in verbocean:  
        libelleVerbocean.append(stemmer.stem(verb.split()[0].strip('\r\n')))
    
    # retirer les doublons   
    libelleEvent = list(set(libelleEvent))
    libelleVerbocean = list(set(libelleVerbocean))
    uncommons = libelleEvent
    
    for event in libelleEvent:
        if event in libelleVerbocean :
            commons.append(event)
            uncommons.remove(event)
    
    commons = list(set(commons))
    
    for word in uncommons:     
        uncommonsEventVerbocean.write(word + '\n')
    
    for word in commons:
        commonsEventVerbocean.write(word + '\n')          

    return commons   

commons = verbocean()
