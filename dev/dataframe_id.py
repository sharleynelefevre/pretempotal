# -*- coding: utf-8 -*-
"""
Created on Tue Feb 19 09:40:32 2019

@author: Sharleyne-Lefevre
"""

import os
import nltk
import pandas as pd
from os import path

dfId  = {}  

dfId['docID'] = []
dfId['word'] = []
dfId['idWord'] = []
dfId['idSent'] = []
dfId['id'] = []

dfId['event'] = []
dfId['idEvent'] = []

dfId['timex'] = []
dfId['idTimex'] = []

dfId['signal'] = []
dfId['idSignal'] = []


def openFilesTxt():
    path_tbaq = 'ressources/TBAQ-new/' # modif path
    texts = {}
    for foldername in os.listdir(path_tbaq):
        if os.path.isdir(path.join(path_tbaq, foldername)):
           for filename in os.listdir(path.join(path_tbaq, foldername)):
               (basename, ext) = path.splitext(filename)
               if ext == '.txt':
                   with open(path.join(path_tbaq, foldername, filename), 'r', encoding='utf8') as file:
                       texts[filename.replace(".txt","")] = file.read()
    return texts


def createId():
   files = openFilesTxt()

   eventsTexts = []
   timexsTexts = []
   signauxTexts = []
   
   for fileName, fileContent in files.items():
       iterSent  = 0 # iterateur pour les identifiants de phrases
       iterWord  = 0 # iterateur pour les identifiants de mots
       iterEvent = 0 # iterateur pour les identifiants d'events
       iterTimex = 0 # iterateur pour les identifiants de timex
       iterSignal = 0 # iterateur pour les identifiants de signaux

       sents = nltk.sent_tokenize(fileContent)
       for sent in sents:
           iterSent += 1
           # on tokenize les phrase en mots
           tokens = nltk.word_tokenize(sent)
                   
           new = []
           # definition d'un séparateur de mots (pour les timex)
           sep = '>'
            
           """ pour rassembler les timex tokenizes sur le # """
           i = 0
           while i < len(tokens):
               t = tokens[i]
               if t == '#':
                   t2 = tokens[i-1] + t + tokens[i+1]
                   new.append(t2)
                   indexT2 = new.index(t2)
                   new.remove(new[indexT2-1])
                   i += 2
               else:
                   new.append(t)
                   i += 1
                   
           """ pour retirer les doublons : on on#s1 / for for#s1 et doublons dans les dates """
           for i in reversed(range(len(new))):
               if '#s' in new[i]:
                   if new[i-1] == new[i].split('#')[0]:
                       indexDoublon = new.index(new[i-1])
                       new.remove(new[indexDoublon])  
                   
               elif '#t' in new[i]:
                   if ">" in new[i]:
                       new.remove(new[i])
                   
                   if new[i-1] == new[i].split('#')[0]:
                       indexDoublon = new.index(new[i-1])
                       new.remove(new[indexDoublon]) 
         
           finalText = []
           """ rassembler les mots composés d'une apostrophe qui ont été tokenisés """ 
           while i < (len(new)):
               if new[i].startswith("'"):
                   t2 = new[i-1]+new[i]
                   finalText.append(t2)
                   indexT2 = finalText.index(t2)
                   finalText.remove(finalText[indexT2-1])
                   i += 2
               else:
                   finalText.append(new[i])
                   i += 1
           
           for i in reversed(range(len(finalText))):
               if "#t" in finalText[i] and "'s" in finalText[i]:
                   index = finalText.index(finalText[i])                    
                   finalText[index:index+2] = ['>'.join(finalText[index:index+2])]
          
           """ pour rassembler les timex tokenizes sur le > (timex multi-mots) """
           while sep in finalText:
               indexSep = finalText.index(sep)
               finalText[indexSep-1] += finalText[indexSep] + finalText[indexSep+1]
               finalText.remove(finalText[indexSep+1])
               finalText.remove(finalText[indexSep])

           for w in finalText:
               if '#e' in w:
                   eventsTexts.append(w)
                   
               if '#t' in w:
                   timexsTexts.append(w)
                  
               if '#s' in w:
                   signauxTexts.append(w)

           for word in finalText:
               iterWord += 1
               dfId['word'].append(word)
               dfId['idWord'].append(iterWord)
               dfId['idSent'].append(iterSent)  
               dfId['docID'].append(fileName)
               
               if '#' in word:
                   w = nltk.word_tokenize(word)
                   dfId['id'].append(w[2])
               else:                   
                   dfId['id'].append('')
               
               if word in eventsTexts:
                   iterEvent += 1
                   # et on ajoute le token event dans la colonne event
                   dfId['event'].append(word)
                   # on ajoute aussi son numero d'identifiant
                   dfId['idEvent'].append(iterEvent)
               else:
                   # sinon on ajoute une chaine vide
                   dfId['event'].append('')
                   dfId['idEvent'].append('')
                   
               if word in timexsTexts :
                   iterTimex += 1
                   dfId['timex'].append(word)
                   dfId['idTimex'].append(iterTimex)

               else:
                   dfId['timex'].append('')
                   dfId['idTimex'].append('')
                   
                   
               if word in signauxTexts :
                   iterSignal += 1
                   dfId['signal'].append(word)
                   dfId['idSignal'].append(iterSignal)

               else:
                   dfId['signal'].append('')
                   dfId['idSignal'].append('') 
                   
       # mise en dataframe du dictionnaire de listes
       res = pd.DataFrame(dict([(k,pd.Series(v)) for k,v in dfId.items()]))
       # ecriture dans le csv
       res.to_csv('CSV/dataframe_id.csv', sep=';', encoding='utf-8') 

createId()