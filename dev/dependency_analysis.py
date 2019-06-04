# -*- coding: utf-8 -*-
"""
Created on Wed Apr 24 09:35:21 2019

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
       res.to_csv('CSV/dependency_dataframe_id.csv', sep=';', encoding='utf-8') 
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
    return json_texts


def df_id_to_json():
    # ouverture du csv en dataframe
    openData = pd.read_csv("CSV/dependency_dataframe_id.csv", sep=';') 
    # selection des colonnes qui nous intéressent
    datas = openData[['docID', 'word', 'idSent', 'idWord', 'id']]
    # transformation format dataframe to json 
    datas = datas.to_json(orient='records')
    
    # pour "pretty print" dans le fichier dans lequel il sera enregistré
    loadJsonDatas = json.loads(datas)
    indentedJson = json.dumps(loadJsonDatas, indent=2, sort_keys=True)
    
    # enregistrement du dataframe transformé en json dans un fichier
    with open('dataframe_id_JSON.json', 'w') as f: 
        f.write(indentedJson)


""" diviser en fonctions """
def find_events(): 
    # appel de la fct qui renvoit les fichiers du corpus au format json
    json_texts = open_json_files()
    
    # ouverture du fichier json du dataframe des identifiants pour la dependance
    with open('dataframe_id_JSON.json', 'r') as json_df: 
        df_id_json = json.load(json_df)
        
    # listes de dictionnaires des events, des timex et des signaux obtenus a partir du dataframe des id + leurs infos (docid, idsent, idword)
    dctEvents = []
    dctSignaux = []
    dctTimex = []
    
    # signaux de type after pour les events
    signalAfterEvents = ['after', 'since', 'when', 'during']
    # signaux de type after pour les timex
    signalAfterTimex = signalAfterEvents+['at', 'in']    
    #signaux de type before (les mêmes pour les events et les timexs)
    signalBefore = ['before', 'until']
    
    attributes = [['e',dctEvents], ['s', dctSignaux], ['t', dctTimex]]
    # récupération des events et des signaux via le dataframe des identifiants
    for dct in df_id_json:
        for i in attributes:
            if dct['id'] != None and i[0] in dct['id'] :
                i[1].append(dct)
        
    relations = [[signalAfterTimex, '#t', '#e', 'event_timex'], [signalAfterEvents, '#e', '#e', 'event_event']]
    for relation in relations :   
        # dictionnaire de liste pour les dataframes finaux (écriture dans les csv)
        dictRel = {}
        dictRel["docID"] = []
        dictRel["signal"] = []
        dictRel["type relation"] = []
        dictRel["event1"] = []
        dictRel["event2"] = []
        dictRel["tag_event1"] = []
        dictRel["tag_event2"] = []
        dictRel["id_signal"] = []
        dictRel["id_event1"] = []
        dictRel["id_event2"] = []
        dictRel["relation E1-E2"] = []  
         
        # pour chaque cle dans le corpus json
        for key in json_texts.keys():
            content = json_texts[key]['Dependencies']
            # récupération du filename (qui est le chemin de la destination du fichier donc on récupère le dernier élément qui est le nom du fichier)
            filenameCorpus = key.split('/')[len(key.split('/'))-1]
            
            allData = []
            allData.extend(dctEvents+dctTimex+dctSignaux)
    
            # pour chaque dictionnaire dans tous les dictionnaires (tout confondu : signal, event, timex)
            for data in allData:
                idSent = str(data['idSent'])
                idWord = str(data['idWord'])
                if filenameCorpus == data['docID']:
                    if idSent in content.keys() and idWord in content[idSent][0].keys():
                        content[idSent][0][idWord]['idWord'] = data['word'] 
    
                # si la valeur de la clé word est un signal et que son filename est le même que celui dans le dataframe des id
                if "#s" in data['word'] and filenameCorpus == data['docID']:
                    sentence = content[idSent][0]
                    word = sentence[idWord]
                    
                     
                    # si le signal est de type after ou si le signal est de type before
                    if word['word'].lower() in relation[0] or word['word'].lower() in signalBefore:
                        wordHead = ""
                        wordHeadHead = ""
                        # pour chaque cle, dictionnaire de mot
                        for key, wordRef in sentence.items():
                            # si la valeur de l'attribut "adresse" (de la tête) est le même que la valeur de l'attribut "head" (du signal)
                            if str(wordRef['address']) == str(word['head']):
                                # la tête est devient dictionnaire du mot de la tête du signal
                                wordHead = wordRef
                                break
                            
                        # on récupère la tête de la tête du signal    
                        for key, wordRef in sentence.items():
                            if str(wordRef['address']) == str(wordHead['head']):
                                wordHeadHead = wordRef
                                break
                            
                        # si il y a une clé idWord dans le dictionnaire de la tête du signal et dans le dict de la tête de la tête du signal    
                        if 'idWord' in wordHead and 'idWord' in wordHeadHead:
                            # si la valeur de idWord contient un #e pour la tête et pour la tête de la tête
                            if relation[1] in wordHead['idWord'] and relation[2] in wordHeadHead['idWord']:
                                # on prend le target-path      
                                path = getTargetPath([word],word,sentence)
                                
                                for i in range(len(path)-2):
                                    signal = path[i]
                                    event1 = path[i+1]
                                    event2 = path[i+2]
        
                                    if signal['word'].lower() in relation[0] or signal['word'].lower() in signalBefore:
                                        if signal['word'].lower() in relation[0] :
                                            typeRelation = " -> "
                                        elif signal['word'].lower() in signalBefore :
                                            typeRelation = " <- "
                                            
                                    # -3 pour ne pas prendre en compte la relation root avec le symbole "> root"
                                    if i == len(path)-3:
                                        datas = [["docID",filenameCorpus],["signal", signal['word']],["type relation",typeRelation],["event1",event1['word']],
                                                 ["event2",event2['word']], ["tag_event1",event1['tag']], ["tag_event2",event2['tag']], ["id_signal",signal['idWord'].split('#')[1]]]
                                        # on met les données dans un dictionnaire 
                                        for i in datas:
                                            dictRel[i[0]].append(i[1])
                                        if 'idWord' in event1.keys():
                                            dictRel["id_event1"].append(event1['idWord'].split('#')[1].replace('.',''))
                                        if 'idWord' in event2.keys():
                                            dictRel["id_event2"].append(event2['idWord'].split('#')[1].replace('.',''))
                                        dictRel["relation E1-E2"].append(event1['rel'])
                        
                        df = pd.DataFrame(dict([(k,pd.Series(v)) for k,v in dictRel.items()]))
                        df.to_csv('CSV/relations_'+relation[3]+'.csv', sep=';', encoding='utf-8') 


def getTargetPath(path, target, sentence):
    # path : le dictionnaire de la dépendance du signal, le dictionnaire de la dépendance du head
    # target : la dépendance du head
    # sentence : la dépendance de chaque mot qui compose une phrase
    
    # pour chaque clé (idWord) et dépendance du word 
    for key, word in sentence.items() :
        # si l'idWord est le même que l'id du head du mot 
        if str(key) == str(target['head']) :
            # on récupère le target path du mot
            path.append(word)
            # si le head du mot est 0 
            if word['head'] == 0 : 
                # alors on retourne le path car après il n'y a plus rien (à par "root")
                return path
            break    
    if len(path)<3:
        return getTargetPath(path, path[len(path)-1],sentence)
    else:    
        return path

#dependencies_trans_json()
#df_id_to_json()    
find_events()
