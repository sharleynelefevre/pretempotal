# -*- coding: utf-8 -*-
"""
Created on Tue Feb 19 09:40:32 2019

@author: Sharleyne-Lefevre
"""

import os
import nltk
import codecs
import pandas as pd
from nltk import tokenize
from bs4 import BeautifulSoup
from pandas import DataFrame as df


path = 'dev/TBAQ-cleaned/'

dfId  = {}  

dfId['word'] = []
dfId['docId'] = []
dfId['idWord'] = []
dfId['idSent'] = []

dfId['event'] = []
dfId['idEvent'] = []

dfId['timex'] = []
dfId['idTimex'] = []

dfId['signal'] = []
dfId['idSignal'] = []


for foldername in os.listdir(path):
    if os.path.isdir(path+foldername):
       for filename in os.listdir(path+foldername):
           if '.tml' in filename:
               file = codecs.open(path+foldername+'/'+filename, 'r', 'utf8') 
               # parser le xml
               soup = BeautifulSoup(file.read(), 'xml') 
               file.close()
            
           iterSent  = 0 # iterateur pour les identifiants de phrases
           iterWord  = 0 # iterateur pour les identifiants de mots
           iterEvent = 0 # iterateur pour les identifiants d'events
           iterTimex = 0 # iterateur pour les identifiants de timex
           iterSignal = 0 # iterateur pour les identifiants de signaux
            
           for textTag in soup.find_all('TEXT'):
               # on retire les '\n' 
               text = textTag.text.strip('\n') # PB : il y a encore des '\n' qui empechent le decoupage en phrases
            
            
           eventsTexts = []
           for eventTag in soup.find_all('EVENT'):
           #                    print(eventTag)
               eventsTexts.append(eventTag.text)
            
           timexsTexts = []
           for timexTag in soup.find_all('TIMEX3'):
               timexsTexts.append(timexTag.text)
            
           signauxTexts = []
           for signalTag in soup.find_all('SIGNAL'):
               signauxTexts.append(signalTag.text)
                
                
           for sent in tokenize.sent_tokenize(str(text)):  
               iterSent += 1
            
               # on decoupe les phrases en tokens
               for wordTokenized in nltk.word_tokenize(sent):
                   iterWord += 1
                    
                   # dans tous les cas on ajoute le docid le token son id et l'id de phrase dans laquelle il est
                   dfId['docId'].append(soup.find('DOCID').text)
                   dfId['word'].append(wordTokenized)
                   dfId['idWord'].append(iterWord)
                   dfId['idSent'].append(iterSent)
                    
                    
                   # test si le token est un event
                   if wordTokenized in eventsTexts :
                       # si il en est un on incremente le compteur de 1
                       iterEvent += 1
                       # et on ajoute le token event dans la colonne event
                       dfId['event'].append(wordTokenized)
                       # on ajoute aussi son numero d'identifiant
                       dfId['idEvent'].append(iterEvent)  
                   else:
                       # sinon on ajoute une chaine vide
                       dfId['event'].append('')
                       dfId['idEvent'].append('')                               
                       
                   # on fait le meme test pour les timexs et les signaux                        
                   if wordTokenized in timexsTexts :
                       iterTimex += 1
                       dfId['timex'].append(wordTokenized)
                       dfId['idTimex'].append(iterTimex)
                   else:
                       dfId['timex'].append('')
                       dfId['idTimex'].append('')
           
           
                   if wordTokenized in signauxTexts :
                       iterSignal += 1
                       dfId['signal'].append(wordTokenized)
                       dfId['idSignal'].append(iterSignal)
                   else:
                       dfId['signal'].append('')
                       dfId['idSignal'].append('')   
             
           # mise en dataframe du dictionnaire de listes
           res = pd.DataFrame(dict([(k,pd.Series(v)) for k,v in dfId.items()]))
           
           # ecriture dans le csv
           res.to_csv('dev/dataframe_id_ponctuation.csv', sep=';', encoding='utf-8') 
