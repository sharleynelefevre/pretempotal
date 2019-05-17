# -*- coding: utf-8 -*-
"""
Created on Wed Apr 24 09:35:21 2019

@author: Sharleyne-Lefevre
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Feb 19 09:40:32 2019

@author: Sharleyne-Lefevre
"""

import os
import nltk
import pandas as pd
from os import path
from nltk.parse.stanford import StanfordDependencyParser
import re
import json


GLOBAL_PATH   = "ressources/"
INPUT_FOLDER  = str(GLOBAL_PATH)+"TBAQ-new_input/"
OUTPUT_FOLDER = str(GLOBAL_PATH)+"TBAQ-dependencies/"


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
    texts = {}
    for foldername in os.listdir(INPUT_FOLDER):
        if os.path.isdir(path.join(INPUT_FOLDER, foldername)):
           for filename in os.listdir(path.join(INPUT_FOLDER, foldername)):
               (basename, ext) = path.splitext(filename)
               if ext == '.txt':
                   with open(path.join(INPUT_FOLDER, foldername, filename), 'r', encoding='utf8') as file:
                       texts[str(INPUT_FOLDER)+str(foldername)+"/"+str(basename)] = file.read()
               
    return texts


def createId():
   files = openFilesTxt()
   eventsTexts = []
   timexsTexts = []
   signauxTexts = []
   
   filenames = []
   
   lstlstSentences = []
   for filename, fileContent in files.items():  
       print(filename)
       filenames.append(filename)
       iterSent  = 0 # iterateur pour les identifiants de phrases
       iterEvent = 0 # iterateur pour les identifiants d'events
       iterTimex = 0 # iterateur pour les identifiants de timex
       iterSignal = 0 # iterateur pour les identifiants de signaux
       
       sents = nltk.sent_tokenize(fileContent)

       lstSentences = []
       for sent in sents:  
           iterWord  = 0 # iterateur pour les identifiants de mots
           iterSent += 1
           # on tokenize les phrase en mots
           tokens = nltk.word_tokenize(sent)
           new = []

           """ pour rassembler les timex tokenizes sur le # """
           i = 0
           while i < len(tokens):
               t = tokens[i]
               if t == '#':
                   t2 = tokens[i-1] + t + tokens[i+1]
                   new.append(t2)
                   indexT2 = new.index(t2)
                   if new[indexT2].split("#")[0] == new[indexT2-1]:
                       del new[indexT2-1]
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
                       
           for mot in new:
                if mot == ">":
                    new.remove(mot)
           
           for w in new:
               if '#e' in w:
                   eventsTexts.append(w)
               if '#t' in w:
                   timexsTexts.append(w)
               if '#s' in w:
                   signauxTexts.append(w)

           for word in new:
               iterWord += 1
               dfId['word'].append(word)
               dfId['idWord'].append(iterWord)
               dfId['idSent'].append(iterSent)  
               dfId['docID'].append(filename.split('/')[3])
               
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
                   
      
           lstSentences.append(new) # 1 fichier = 1 liste de listes de phrases tokenizées en phrases puis en mots
           for i in lstSentences: # on enleve l'annotation des events pour tout passer dans stanford parser dependency
               for l in range(len(i)):
                   if '#' in i[l]:
                       i[l] = i[l].replace(i[l], i[l].split("#", maxsplit=1)[0])                        
       lstlstSentences.append(lstSentences)

       # mise en dataframe du dictionnaire de listes
       res = pd.DataFrame(dict([(k,pd.Series(v)) for k,v in dfId.items()]))
       # ecriture dans le csv
       res.to_csv('CSV/TEST_DEPENDENCIES_dataframe_id.csv', sep=';', encoding='utf-8') 
   return filenames, lstlstSentences


def dependencies(): # création des fichiers - articles passé dans le stanford parser / analyse en dépendances
    (filenameDep, inputDependencies) = createId()
    
    os.environ['CLASSPATH'] = "stanford-parser/stanford-parser-full-2018-10-17"
    os.environ['JAVAHOME'] = "D:/Program Files/java/bin"
    path_parser = "stanford-parser/stanford-parser-full-2018-10-17/stanford-parser.jar"
    path_model = "stanford-parser/stanford-parser-full-2018-10-17/stanford-parser-3.9.2-models.jar"
    dependency_parser = StanfordDependencyParser(path_to_jar = path_parser, path_to_models_jar = path_model)

    texts_dependencies = {}
    for i in range(len(inputDependencies)):
        parsedText = ""
        dependencies = dependency_parser.parse_sents(inputDependencies[i])
        
        for dep in dependencies:
            for d in dep:
                parsedText += str(d)
        texts_dependencies[filenameDep[i]] = parsedText
        print(filenameDep[i])
    return texts_dependencies


def dependencies_trans_json():
    dependances = dependencies()
    
    for filename, dep in dependances.items():
        """ Regex de transformation de la sortie au format JSON """
        dep = dep.replace("None", "null").replace("'",'"') # remplacer les ' par " et None par null
        dep = re.sub(r'(defaultdict\(<function DependencyGraph\.__init__\.<locals>\.<lambda> at)(.*)(>)', r'\n\t"\1\2\3"', dep) # mettre la clé entre "
        dep = re.sub(r'(at)(.*)(>)(")(\,)', r'\1\2\3)\4 : [', dep) # ajouter ) : [ après la clé
        dep = re.sub(r'(\}\}\))', r'\1}', dep) # fermeture avec }
        dep = re.sub(r'(\}\})(\))(\})', r'\1]\3', dep) # fermeture avec ]
        dep = re.sub(r'([0-9]{1,})(\: )', r'"\1"\2', dep) # mettre les id de mots entre "
        dep = re.sub(r'^(\n)', r'{"Dependencies" : {\n', dep) # création de la clé Dependencies qui englobe le tout
        dep = re.sub(r'(\})\Z', r'\1\n}', dep) # ajout d'une fermeture } en fin de fichier
        dep = re.sub(r'(defaultdict\(<class "list">)(.*)(\,)', r'"\1\2\3', dep) # mettre les valeurs defaultdict entre " ouvertes
        dep = re.sub(r'(\}\))(\,)', r'\1"\2', dep) # ajout de " entre } et ), suppression de virgule
        dep = re.sub(r'(\")(list|root)(\")(\:|>)', r"'\2'", dep) # mettre les list et root entre ' plutôt que "
        dep = re.sub(r'(\}\}\])', r'\1,', dep) # ajout d'une virgule après }}]
        dep = re.sub(r"(\"defaultdict\(<class 'list')(\,)", r'[{\1)" : \n', dep) # mettre les valeurs defaultdict entre " fermées
        dep = re.sub(r'(\}\}\]\,)(\})', r'\1', dep) # suppression de la fermeture } après une virgule
        dep = re.sub(r"(\"defaultdict\(<class 'list')(\,)(\r\n)", r'\1" : \3', dep) # ajout de " : entre clé defaultdict et suppression de la , + passage à la ligne
        dep = re.sub(r'(\]\})(\))(\")(\,)', r'\1}]\4', dep) # ajout de fermetures }]
        dep = re.sub(r"('root')", r'"root"', dep) # modification des guillemets de certains root
        dep = re.sub(r'(\{\})(\))(\")(\,)', r'\1}]\4', dep) # ajout de fermetures }] et suppression de ", -> {})", > {}}],
        dep = re.sub(r'(\{\".*\")( )(\[.*\]\})', r'\1: \3', dep) #
        dep = re.sub(r"(\"defaultdict\(<class 'list')(\")", r'\1)\2', dep) # fermeture avec )
        dep = re.sub(r"(\"deps\"\: )(\"defaultdict\(<class 'list')", r'\1[{ \2', dep) # ajout de [{ entre deps : et defaultdict
        dep = re.sub(r'(\])(\,)(\n)(\})', r'\1\3\4', dep) # retirer la , entre },}
        dep = re.sub(r'(\])(\,)(\n)(\})', r'\1\3\4}', dep) # ajout d'une fermeture 
        dep = re.sub(r'(\}\Z)', r'}}', dep) # fermeture avec deux } en fin de document
        dep = re.sub(r'(\")(\")([a-zA-Z]{1,})(\")', r"\1'\3\4", dep) # remplacer les ""s" par "'s" / "n"t" par "n't" / """ par "'" / ""ll" par "'ll"
        dep = re.sub(r'(\")([a-zA-Z]{1})(\")(.*)(\")', r"\1\2'\4\5", dep) # pour les noms propres avec ' : D'Amato / O'Laughlin
        dep = dep.replace('"""', '''"'"''') # remplacer les """ par "'"
        
        i = 1
        writeFile = ""
        for line in dep.split("\n"):
            if "defaultdict(<function" in line:
                writeFile += '\n"'+str(i)+'" : ['
                i += 1
            else:
                writeFile += "\n"+str(line)
                
        filename = str(filename.replace(INPUT_FOLDER, OUTPUT_FOLDER))+".json"
        with open(filename, 'w', encoding='utf8') as fileW:
            fileW.write(writeFile)
            
            
def open_json_files():
    json_texts = {}
    for foldername in os.listdir(OUTPUT_FOLDER):
        if os.path.isdir(path.join(OUTPUT_FOLDER, foldername)):
           for filename in os.listdir(path.join(OUTPUT_FOLDER, foldername)):
               (basename, ext) = path.splitext(filename)
               if ext == '.json':
                   with open(path.join(OUTPUT_FOLDER, foldername, filename), 'r', encoding='utf8') as json_file:
                       json_texts[str(OUTPUT_FOLDER)+str(foldername)+"/"+str(basename)] = json.load(json_file)
                       break
    return json_texts

def find_events():
    json_texts = open_json_files()
             
    for filename, json_content in json_texts.items():
        print(filename.split("/")[3])
        for dependencies, idSent in json_content.items():
            for idS,idWord in idSent.items():
                print("ID SENT : "+str(idS))
                for elem in idWord:
                    for idW, reste in elem.items():
                        print("ID WORD : "+str(idW))
                print()
                print()
            
                          
                       

    
#dependencies_trans_json()
find_events()