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
from nltk.stem import PorterStemmer
from nltk.stem.porter import *
from nltk.stem import *
import nltk
import pandas as pd
import re
from nltk.corpus import wordnet

def openFilesTML():
    """ ouverture des fichiers .tml """
    # ouverture de chaque fichier du repertoire 
    path = "ressources/TBAQ-cleaned/"
    soup = []
    # pour chaque fichier dans les fichiers du repertoire
    for foldername in os.listdir(path):
        if os.path.isdir(path+foldername):
            for filename in os.listdir(path+foldername):
                if '.tml' in filename:
                    file = codecs.open(path+foldername+'/'+filename, 'r', 'utf8') 
                    # parser le xml
                    soup.append(BeautifulSoup(file.read(), 'xml')) 
                    file.close()
    return soup
        

def extractInstances(file):
    """ recuperation des attributs des makeinstances et ajout dans le dictionnaire instance """
    attributes = ['eventID','eiid','aspect','tense','pos','polarity','modality','cardinality']
    
    instances = {}
    
    for makeinstance in file.find_all('MAKEINSTANCE'):
        instance = {}
        
        for attribute in attributes :
            instance[attribute] = makeinstance.get(attribute)
        instances[makeinstance.get('eventID')] = instance
        
    return instances
        
        
def extractEvents(file, document):
    """ extraction des events """
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
        verb['event']['lemmeNltk'] = lemmatizeEvent(verb)
        # creation des synsets / hyperonymes
        verb['event']['Wordnet'] = extractSynset(verb)
        # ajout du dictionnaire verbe dans le dictionnaire events
        events[eventTag.get('eid')] = verb
        
    document['verbes'] = events
    

def extractTimex(file, document):
    """ extraction des timex """
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
    
    
def creationDocument(file):
    """ le contenu d'un fichier (event, timex, signaux) se trouve dans le dictionnaire 'document' """
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
    
    return document
    

def extractDocuments():
    """ la liste 'documents' contient chaque dictionnaire 'document' """
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

    print('Documents crées \n')
    return documents


def lemmatizeEvent(event):
    """ lemmatization d'un event """ 
    lemmatizer = WordNetLemmatizer()
    # on n'a pas toujours d'instance pour un event
    # si on en a un
#    print(event['instance'])
    if event['instance'] != None : 
        # on recupere le temps
        tense = event['instance']['tense']
        # on recupere le pos
        pos = event['instance']['pos'][0].lower()
    else :
        tense = None
#        print(event) # /!\ Events sans instance 
        # sinon on assigne 'None' au pos des events n'ayant pas d'instance
        pos = None
    
    if pos in ['u', 'p', 'o', None]:  # NLTK ne prend pas en compte les p et les o (OTHER), les u (UNKNOWN) et None pour les events sans instance
        # si le temps de l'event est 'NONE', il y a de grandes chances pour que l'event soit un nom
        if tense == 'NONE':
            # donc on lui donne le pos n (noun)
            pos = 'n'
        else:
            # sinon par defaut on lui donne le pos v (verb) et on retourne l'event lemmatise
            pos = 'v'
    
    return lemmatizer.lemmatize(event['libelle'], pos)


def extractSynset(event):
    synset = {}
    synonyms = wordnet.synsets(event['libelle'])
    s = str(synonyms).replace("Synset(","").replace(")","").replace("[","").replace(']',"").replace("'", "").replace(" ", "")
    synset["synonymes"] = s
    
    for syn in synonyms:
        hyper = syn.hypernyms()
        h = str(hyper).replace("Synset(","").replace(")","").replace("[","").replace(']',"")
        synset["hyperonymes"] = h
        for l in syn.lemmas(): 
            if l.antonyms(): 
                synset["antonymes"] = l.antonyms()[0].name()
            
    if not "hyperonymes" in synset:
        synset["hyperonymes"] = ''
        
    if not "antonymes" in synset:
        synset["antonymes"] = ''

    return synset


def writeCsvEvent(documents): 
    print('ecriture csv event')
    # ouverture du csv en ecriture
    with open('CSV/features_events.csv', 'w', newline='') as f:
        # en-tete des colonnes
        fieldnames = ['Libelle', 'docID', 'id', 'eiid', 'Class', 'Stem', 'StemNltk', 'LemmeNltk', 'Aspect', 'Tense', 'POS', 'Polarity', 'Modality', 'Cardinality', 'Synsets', 'Hyperonyme', 'Antonyme']#'Hyperonyme'
        # le writer est au format dictionnaire
        writer = csv.DictWriter(f, fieldnames = fieldnames, delimiter = ';')

        writer.writeheader()
        
        for document in documents:
            for verb in document['verbes']:
                verb = document['verbes'][verb]
                if verb['instance'] != None:
#                    if verb['event']["Wordnet"]['synonymes'] != '':
                    # remplissage des colonnes avec les elements provenant de event et instance + docId
                    writer.writerow({'docID' : document['docId'], 
                                     'Libelle' : verb['libelle'],
                                     'id' : verb['event']['eid'],
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
                                     'Cardinality' : verb['instance']['cardinality'],
                                     'Synsets' : verb['event']["Wordnet"]['synonymes'],
                                     'Hyperonyme' : verb['event']["Wordnet"]['hyperonymes'],
                                     'Antonyme' : verb['event']["Wordnet"]['antonymes']})
    
    print('ecriture csv event finie \n')
    f.close()


def writeCsvTimex(documents):
    print('ecriture csv timex')    
    with open('CSV/features_timex.csv', 'w', newline='') as f:
        fieldnames = ['Libelle', 'docID', 'id', 'Type', 'Value', 'Mod', 'temporalFunction', 'functionInDocument', 'beginPoint', 'endPoint', 'quant', 'freq', 'anchorTimeID']
        writer = csv.DictWriter(f, fieldnames = fieldnames, delimiter = ';')

        writer.writeheader()
        
        for document in documents:
            for word in document['timexs']:
                word = document['timexs'][word]
                writer.writerow({'docID' : document['docId'], 
                                 'Libelle' : word['libelle'],
                                 'id' : word['timex']['tid'],
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
    

def openFilesTXT():
    """ ouverture des fichiers .txt """
    path = 'ressources/TBAQ-new_input/'
    texts = {}
    for foldername in os.listdir(path):
        if os.path.isdir(path+foldername):
            for filename in os.listdir(path+foldername):
                if '.txt' in filename:
                    file = codecs.open(path+foldername+'/'+filename, 'r', 'utf8').read()
                    texts[filename.replace(".txt","")] = file
    return texts 


def extractSignaux():
    files = openFilesTXT()

    dataframeConnecteurs = {}
    dataframeConnecteurs['Libelle'] = []
    dataframeConnecteurs['docID'] = []
    dataframeConnecteurs['id'] = []
    
    # pour chaque fichier
    for fileName, fileContent in files.items():
        print(fileName)
        for w in fileContent.split():
            if '#s' in w:
                signal = re.split('\#|\>', w)
                dataframeConnecteurs['docID'].append(fileName)
                dataframeConnecteurs['id'].append(signal[1])
                if len(signal) > 2:
                    dataframeConnecteurs['Libelle'].append(str(signal[0])+' '+str(signal[2]))
                else:
                    dataframeConnecteurs['Libelle'].append(signal[0])

        # mise en dataframe du dictionnaire de listes
        res = pd.DataFrame(dict([(k,pd.Series(v)) for k,v in dataframeConnecteurs.items()]))
        # ecriture dans le csv
        res.to_csv('CSV/features_signaux.csv', sep=';', encoding='utf-8') 
 
        
def tokenizeTexts(): 
    # appel de la fonction pour ouvrir les fichiers txt
    files = openFilesTXT()
    
    # pour chaque fichier
    for fileName, fileContent in files.items():
        # on tokenize le fichier en phrase
        sents = nltk.sent_tokenize(fileContent)
        newToken = []
        # pour chaque phrase
        for sent in sents:
            # on tokenize les phrase en mots
            tokens = nltk.word_tokenize(sent)
            new = []
            # definition d'un séparateur de mots (pour les timex)
            sep = '>'
             
            """ pour rassembler les timex tokenizes sur le # """
            i = 0
            # tant que i est inferieur à la taille de la liste tokens (nb de mots dans la liste)
            # evite un out of range
            while i < len(tokens):
                # t est le mot
                t = tokens[i]

                # si t est un #
                if t == '#':
                    # nouvelle string qui est composee du mot qui precede le # et du mot qui le suit
                    t2 = tokens[i-1] + t + tokens[i+1]
                    # on met la nouvelle chaine dans la liste new
                    new.append(t2)
                    # pour redefinir l'index du mot qui comporte un #
                    indexT2 = new.index(t2)
                    # suppression du mot-1 (car il y a une repetition)
                    if new[indexT2].split("#")[0] == new[indexT2-1]:
                        del new[indexT2-1]
                    i += 2
                    
                else:
                    # sinon si t n'est pas un #
                    # on met t dans la liste new
                    new.append(t)
                    # et on incremente le compteur de 1 pour dire que le mot qui suit t est t+1
                    i += 1            
            
            """ pour retirer les doublons : on on#s1 / for for#s1 et doublons dans les dates """
            for k in reversed(range(len(new))):
                if '#s' in new[k]:
                    if new[k-1] == new[k].split('#')[0]:
                        indexDoublon = new.index(new[k-1])
                        new.remove(new[indexDoublon])  
                    
                elif '#t' in new[k]:
                    # fichier wsj 122, un espace de trop en fin de timex dans le fichier tml = ">t0" en trop
                    if ">" in new[k]:
                        new.remove(new[k])
                    
                    
                    if new[k-1] == new[k].split('#')[0]:
                        indexDoublon = new.index(new[k-1])
                        new.remove(new[indexDoublon]) 
                        
                    # fichier wsj 159 un espace en trop au debut du timex   
                    if new[0] == ">":
                        new.remove(new[0])

            finalText = []
            j = 0
            """ rassembler les mots composés d'une apostrophe qui ont été tokenisés """ # 'next#t90>year', "'s#t90>first#t90>quarter#t90"
            while j < (len(new)):

                if "#t" in new[j] and new[j].startswith("'s"):
                    t2 = new[j-1]+new[j]
                    finalText.append(t2)
                    indexT2 = finalText.index(t2)
                    finalText.remove(finalText[indexT2-1])
                    j += 1
                else:
                    finalText.append(new[j])
                    j += 1
            
            """ pour rassembler les timex tokenizes sur le > (timex multi-mots) """
            # tant qu'il y a le separateur dans la liste new
            while sep in finalText:
                # on recupere l'index du separateur
                indexSep = finalText.index(sep)
                # on ajoute au mot qui precede le separateur : le separateur + le mot qui suit le separateur
                finalText[indexSep-1] += finalText[indexSep] + finalText[indexSep+1]
                # on supprime le mots qui suit le separateur et le separateur
                finalText.remove(finalText[indexSep+1])
                finalText.remove(finalText[indexSep])
#            print(finalText)
            newToken.append(finalText)
        files[fileName] = newToken
    return files


def getContext():
    # appel de la fonction pour tokenizer
    tokens = tokenizeTexts()
#    print(tokens)
    stemmer = PorterStemmer()
    regex = re.compile(r'(t|s)[0-9]{1,}')

    # definition du nombre de mots dans le contexte que l'on souhaite recuperer
    nbContext = 4 
    
    annotatedWords = [] # liste des events/timex/signaux
    contextM4 = [] # juste le contexte -4 mots
    contextP4 = [] # juste le contexte +4 mots
    fileNames = []
    contextPosM4 = []
    contextPosP4 = []
    contextPos = []

    # pour trouver les events, timex, signaux parmi tous les mots
    sep = ['#e', '#t', '#s']  
    
    # pour chaque phrase
    for fileName, sents in tokens.items():
        for sent in sents:
            # pour chaque mot        
            for word in sent:
                # pour chaque separateur
                for s in sep:
                    # si il y a un separateur dans le mot
                    if s in word:
                        # on ajoute le mot a la liste annotatedWords
                        annotatedWords.append(word)
                        # on recupere l'index du mot
                        indexEvent = sent.index(word)
                    
                        beforeEvent = []
                        # context -4/+4
                        for i in range(nbContext,0,-1):
                            if i <= indexEvent:
                                beforeEvent.append(sent[indexEvent-i])
                        contextM4.append(beforeEvent)
                        contextP4.append(sent[indexEvent+1 : indexEvent+nbContext+1])
                        
                        posBefore = []
                        # context -4/+4
                        for i in range(nbContext,0,-1):
                            if i <= indexEvent:
                                posBefore.append(nltk.pos_tag(sent[indexEvent-i].split('#')[0].split()))
                        contextPosM4.append(posBefore)
                        
                        contextPosP4.append(nltk.pos_tag(sent[indexEvent+1 : indexEvent+nbContext+1]))
                        
                        # pour rassembler le context-4 et le context+4 des pos = vérifier si dans le contexte il y a une negation ou adv de modalité
                        # au lieu d'avoir une liste de tuples pour le context pos -4 et une liste de tuples pour le context pos +4
                        # on a une seule liste de tuples pour les deux contexts confondus
                        # servira pour savoir si on a une negation ou un adverbe de modalite dans le context
                        contextGlobal = []
                        contextPosM = nltk.pos_tag(sent[indexEvent-nbContext : indexEvent])
                        contextPosP = nltk.pos_tag(sent[indexEvent+1 : indexEvent+nbContext+1]) 
                        contextGlobal.extend(contextPosM)
                        contextGlobal.extend(contextPosP)
                        contextPos.append(contextGlobal)
                        fileNames.append(fileName)
        
        """contexte en POS"""                
        ctxPOSM4 = []
        ctxPOSP4 = []              
        for context in contextPosM4:
            ctxPosM4 = []
            for l in context:
                for tupl in l:
                    ctxPosM4.append(tupl[1])
            ctxPOSM4.append(ctxPosM4)

        for context in contextPosP4:
            ctxPosP4 = []
            for tupl in context:
                ctxPosP4.append(tupl[1])
            ctxPOSP4.append(ctxPosP4)
            
            
        """contexte en stems"""    
        contextM4Stem = []
        contextP4Stem = []
        for ctx in contextM4:
            beforeEventSTEM = []
            for w in ctx:
                if '#' in w and not '>' in w:
                    w = w.split('#')
                    beforeEventSTEM.append(stemmer.stem(w[0]))
                elif '#' in w and '>' in w:
                    w = re.split('(\#|>)', w)
                    for mot in w:
                        if mot != '#' and mot != '>' and not regex.search(str(mot)):
                            beforeEventSTEM.append(stemmer.stem(mot))
                else:
                    beforeEventSTEM.append(stemmer.stem(w))
            contextM4Stem.append(beforeEventSTEM)
            
        for ctx in contextP4:
            afterEventSTEM = [] 
            for w in ctx:
                if '#' in w and not '>' in w:
                    w = w.split('#')
                    afterEventSTEM.append(stemmer.stem(w[0]))
                elif '#' in w and '>' in w:
                    w = re.split('(\#|>)', w)
                    for mot in w:
                        if mot != '#' and mot != '>' and not regex.search(str(mot)):
                            afterEventSTEM.append(stemmer.stem(mot))
                else:
                    afterEventSTEM.append(stemmer.stem(w))
            contextP4Stem.append(afterEventSTEM)
            
    return [annotatedWords, contextM4, contextP4 , contextPos, fileNames, ctxPOSM4, ctxPOSP4, contextM4Stem, contextP4Stem]


def negation_advModality(contextPos):
    # listes des negations et des adverbes de modalite
    RB_neg = ['not', 'no', 'neither', 'nor', 'n\'t', 'never', 'off']
    RB_modality = ['probably', 'possibly', 'evidently', 'allegedly', 'surely', 'certainly', 'apparently', 'previously', 'definitively'] 
    
    allNeg = []
    allMd = []
    
    # pour chaque contexte dans tous les contextes
    for context in contextPos:
        # liste de deux booleens
        l = [False,False]
        # pour chaque tuple dans le contexte
        for tuplWordPos in context:
            # si le deuxieme element du tuple est RB
            if tuplWordPos[1] == 'RB':
                # on regarde si le premier element du tuple est dans la liste RB_neg
                if tuplWordPos[0].lower() in RB_neg:
                    # si oui, le premier element de la liste de booleens sera True
                    l[0] = True
                # sinon si, le premier element du tuple est dans la liste RB_modality
                elif tuplWordPos[0].lower() in RB_modality:
                    # alors le deuxieme element de la liste de booleens sera True
                    l[1] = True
            # sinon si, le deuxieme element du tuple est MD        
            elif tuplWordPos[1] == 'MD':
                # alors le deuxieme element de la liste de booleens sera True (comme pour les RB_modality)
                l[1] = True 
        
        # on met le tout dans des listes et on retourne ces listes
        allNeg.append(l[0])
        allMd.append(l[1])
    return allNeg, allMd


def dataframeContext():
    # dictionnaire de listes pour faire un dataframe avec pandas
    env  = {}  
    env['id'] = []
    
    # appel de la fonction getContext()
    context = getContext()
    
    # pour chaque mot dans context[0] soit annotatedWords
    for word in context[0]:
        word_segment = nltk.word_tokenize(word) # on tokenize -> 'said#e1" = 'said', '#', 'e1'
        if word_segment[1] == "'s":
            env['id'].append(word_segment[3])
        else:
            env['id'].append(word_segment[2]) # on recupere l'element 2 qui est l'identifiant

    # ajout le dict
    env['docID'] = context[4]
    env['word'] = context[0] 
    env['context-4'] = ['|'.join(ctx) for ctx in context[1]]
    env['context+4'] = ['|'.join(ctx) for ctx in context[2]]
    env['contextPOS-4'] = ['|'.join(ctx) for ctx in context[5]]
    env['contextPOS+4'] = ['|'.join(ctx) for ctx in context[6]] 
    env['contextSTEM-4'] = ['|'.join(ctx) for ctx in context[7]]
    env['contextSTEM+4'] = ['|'.join(ctx) for ctx in context[8]] 
    
    # appel de la fonction negation_advModality() avec le parametre context[3] soit contextPos de la fonction getContext()
    neg_adv = negation_advModality(context[3])
    env['Adv_Negation'] = neg_adv[0] # ce qu'il y a dans ce que retourne neg_adv soit allNeg
    env['Adv_Modality'] = neg_adv[1] # ce qu'il y a dans ce que retourne neg_adv soit allMd 
        
    # mise en dataframe
    res = pd.DataFrame(dict([(k,pd.Series(v)) for k,v in env.items()]))
    # ecriture dans le csv
    res.to_csv('CSV/dataframe_contexts.csv', sep=';', encoding='utf-8') 
    
    
documents = extractDocuments()
writeCsvEvent(documents)
writeCsvTimex(documents)
extractSignaux()
dataframeContext()