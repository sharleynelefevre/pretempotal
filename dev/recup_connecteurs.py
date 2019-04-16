# -*- coding: utf-8 -*-
"""
Created on Tue Mar 19 14:18:23 2019

@author: Sharleyne-Lefevre
"""
import os
import codecs
import nltk 
from nltk.parse.stanford import StanfordParser
import re


def stanfordParser():
    # ajout des variables d'environnement
    os.environ['CLASSPATH'] = "stanford-parser/stanford-parser-full-2018-10-17"
    os.environ['JAVAHOME'] = "D:/Program Files/java/bin"

    # chemin du parser Stanford Parser
    parser = StanfordParser(model_path = "edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz")
    # chemin de l'input / output
    path_input = "ressources/TBAQ-txt-annot/TimeBank-txt-annot/TimeBank/"    
    path_output = 'ressources/TBAQ-txt-annot/TimeBank-txt-annot/TimeBank_StanfordParser/' 
     
    for filename in os.listdir(path_input):
        print(filename)
        file = codecs.open(path_input+filename, 'r', 'utf8').read()
        
        # pour remplacer les retours à la ligne en debut de fichier -> empechaient le tagging des phrases
        file = file.lstrip().replace('\r\n\r\n\r\n', ' ').replace('\r\n\r\n', ' ').replace('\r\n', ' ')
        # tokenization en phrase
        sents = nltk.sent_tokenize(file)
    
        # chaine vide
        parsedText = ""
        # pour chaque phrase on passe le stanford parser
        for sent in sents:
            sent = re.sub('(\.){6,}', '', sent)
            constituancies = list(parser.raw_parse(sent))
            # regex pour mettre en forme la sortie pour que le format convienne à addDiscourse
            constituancies = re.sub(r'''(\[)(Tree)(\()('ROOT')(\,)( )(\[)(Tree)''', '(S1 (S ', str(constituancies))
            constituancies = re.sub(r'''(((\,)( )(\[)(Tree))|((\,)( )(Tree)))''', ' ', str(constituancies))
            constituancies = re.sub(r'''(\[)((')|("))|((')|("))(\])''', "'", str(constituancies))
            constituancies = re.sub(r'''(\])''', ')', str(constituancies))
            constituancies = re.sub(r'''(')''', '', str(constituancies))
            # ajout des phrases tagguées dans la chaine vide
            parsedText += str(constituancies)
        
        # ouverture des fichiers 
        with open((path_output+filename), 'w', encoding='utf8') as fileW:
            # écriture des fichiers
            fileW.write(parsedText)


def addDiscourse():
    # chemin de addDiscourse
    path_addDiscourse = "C:/Users/Sharleyne-Lefevre/Desktop/stage_LIFO/pretempotal/dev/addDiscourse/addDiscourse.pl"
    # chemins d'input / d'output
    path_input = 'ressources/TBAQ-txt-annot/TimeBank-txt-annot/TimeBank_StanfordParser/' 
    path_output = "ressources/TBAQ-txt-annot/TimeBank-txt-annot/TimeBank_AddDiscourse/"

    for filename in os.listdir(path_input):
        file = path_input+filename
        # utilisation de addDiscourse en ligne de commande sur les fichiers taggués par stanford parser
        os.system(path_addDiscourse+' --parses '+file+' --output '+path_output+filename)
    

def cleanTexts():
    path_input = "ressources/TBAQ-txt-annot/TimeBank-txt-annot/TimeBank_AddDiscourse/"
    path_output = "ressources/TBAQ-txt-annot/TimeBank-txt-annot/TimeBank_Connecteurs/"
    
    # initialisation d'un dictionnaire vide
    texts = {}
    for filename in os.listdir(path_input):
        file = codecs.open(path_input+filename, 'r', 'utf8').read()
        # dans le dictionnaire on met les filenames en key et les textes en value
        texts[filename.replace(".txt","")] = file
    
    for fileName, fileContent in texts.items():  
        
        """Application des regex de nettoyage"""
        
        # remplacement des balises, des syntagmes et des postags par un espace 
        cleanedContent = re.sub(r'''(\()|(\))(\,)?|(\[)(')?|(')?(\])|(SBARQ|SINV|WHPP|CONJP|SBAR|SYM|PDT|RBS|FRAG|ROOT|INTJ|JJS|NNPS|NNP|VBZ|PRP\$|WHADVP|WRB|PRN|PRT|PP|IN|DT|JJR|POS|JJ|ADVP|ADJP|CC|EX|VBG|VBN|WHNP|NNS|VP|\-RRB\-|\-LRB\-|RBR|RB|WDT|WP|VBP|PRP|CD|SQ|NN|NP|VBD|VB|TO|RP|QP|MD|S1|UH|S)(( )|(\,))''', '', fileContent)
        # rassembler les docId avec ponct  _ 
        cleanedContent = re.sub(r'([a-zA-Z]*?)( )*(\_)( )*([0-9]*)', r'\1\3\5', cleanedContent) 
        # rassembler les events/timex """
        cleanedContent = re.sub(r'( )*(\#)', '#', cleanedContent) 
        # rassembler les timex multi-mots 
        cleanedContent = re.sub(r'( )*(\>)( )*', '>', cleanedContent) 
        # repl espace au debut par rien 
        cleanedContent = re.sub(r'^( )*', '', cleanedContent) 
        # ca "n't" -> can't 
        cleanedContent = re.sub(r'''( )*(\")([a-zA-Z]*?)(')([a-zA-Z]*?)(\")''', r'\2\3\4', cleanedContent) 
        # repl plusieurs espaces par un seul espace 
        cleanedContent = re.sub(r'( ){2,}', ' ', cleanedContent) 
        # repl toutes les ponct doublées par une seule ponct (sauf le cas du '#')  
        cleanedContent = re.sub(r'''( )(?!(#|\$|\_))((\.)|(\,)|(\:))(\,)( )?''', '', cleanedContent) 
        cleanedContent = re.sub(r'''(\"\")(\,)( )''', "''", cleanedContent)
        # traiter les # qui ne font pas partie des #e/#t.. 
        cleanedContent = re.sub(r'''(#)(\,)(\#)''', '', cleanedContent) 
        # traiter les $ pour qu'ils ne soient pas collés aux mots 
        cleanedContent = re.sub(r'''( )(\$)(\,)( )(\$)( )''', '  $  ', cleanedContent) 
        # traiter les _ pour qu'ils ne soient pas collés aux mots 
        cleanedContent = re.sub(r'''(\_)''', ' _ ', cleanedContent) 
        # rassembler docID
        cleanedContent = re.sub(r'( )(\.)', '.', cleanedContent) 
        # stanford parser a convertit les ( en -LRB- et les ) en -RRB- -> regex pour remplacer par les parentheses 
        cleanedContent = re.sub(r'(\-LRB\- )', '(', cleanedContent)
        cleanedContent = re.sub(r'( )?(\-RRB\-)', ')', cleanedContent)
        cleanedContent = re.sub(r'(\.\.)', '.', cleanedContent)
        # pour reunir les it s en it's / Here / can't / they're
        cleanedContent = re.sub(r'( s )', '\'s ', cleanedContent)
        cleanedContent = re.sub(r'( nt )', 'n\'t ', cleanedContent)
        cleanedContent = re.sub(r'( d )', '\'d ', cleanedContent)
        cleanedContent = re.sub(r'( re )', '\'re ', cleanedContent)
        cleanedContent = re.sub(r'''(\`\`)(\,)( )''', '', cleanedContent) 
        # pour les next#t90>year s#t90>first#t90>quarter#t90 -> next#t90>year's#t90>first#t90>quarter#t90
        cleanedContent = re.sub(r'( )(s)(\#)(t)', ''''s#t''', cleanedContent) 
        # pour wsj _ 0376 -> wsj_0376
        cleanedContent = re.sub(r'(wsj )(\_)( ){1,}', 'wsj_', cleanedContent) 
        # rassembler les dates au format 00/00/00 
        cleanedContent = re.sub(r'(\/)( )', '/', cleanedContent) 

        # ouverture des fichiers d'écriture
        with open((path_output+fileName+'.txt'), 'w', encoding='utf8') as fileW:
            # écriture des fichiers avec le contenu nettoyé
            fileW.write(cleanedContent)
            

def addSignalId(): # A AMELIORER + COMMENTER
    path_input = "ressources/TBAQ-txt-annot/TimeBank-txt-annot/TimeBank_Connecteurs/"
    path_output = "ressources/TBAQ-txt-annot/TimeBank-txt-annot/TimeBank_NewInput/"

    # regex permettant de trouver la partie annotée par addDiscourse d'un mot : mot#0#0 -> #0#0
    regex = re.compile(r'(\#)[0-9]{1,}(\#)(0|Temporal|Contingency|Comparison|Expansion)')
    
    for filename in os.listdir(path_input):
        print(filename)
        file = codecs.open(path_input+filename, 'r', 'utf8').read()   
        
        # initialisation d'un compteur
        j = 1        
        # initialisation d'une liste vide
        word = []
        # split des mots du fichier
        for w in file.split():
            # les mots sont mis dans la liste word
            word.append(w)
        
        # pour chaque mot dans la range de la taille de la liste
        for i in range(len(word)): 
            ### TIMEX ###
            # si le mot est un timex
            if '#t' in word[i]:
                afterTimex = word[i+1 : i+2] # 2 mots après le timex
                beforeTimex = word[i-1] # 1 mot avant le timex
#                envBeforeTimex = word[i-4 : i-1] # 4 mots avant le timex
                # si le mot courant match avec la regex
                if regex.search(word[i]):
                    # on remplace la partie trouvée par la regex par rien (car on ne veut pas de connecteur annoté dans un timex, le timex est déjà annoté)
                    word[i] = re.sub(regex, '' , word[i])                    
                # si le mot avant le timex match avec la regex    
                if regex.search(beforeTimex) : 
                    # si le mot ne fait pas partie des mots de la liste
                    if not beforeTimex.split('#')[0].lower() in ['but', 'next', 'separately']:
                        for e in beforeTimex.split():
                            if regex.search(e):
                                # on remplace la partie qui match avec la regex par un #s suivi d'un compteur
                                word[i-1] = re.sub(regex, '#s'+str(j), e)
                                # incrémentation du compteur
                                j += 1 
                # sinon si le mot d'avant fait partie des mots de la liste (ce sont les connecteurs non-annotés par addDiscourse)
                elif beforeTimex.lower() in ['in', 'on', 'over', 'during', 'at', 'between']:
                    # on ajoute au mot un #s + le compteur
                    word[i-1] = beforeTimex.replace(beforeTimex, beforeTimex+'#s'+str(j))   
                    # incrémentation du compteur
                    j += 1  
                
                # si les mots après le timex match avec la regex
                if regex.search(str(afterTimex)): 
                    # si ils font partie de la liste
                    if str(afterTimex).split('#')[0].replace("['", '') in ['before', 'after', 'later', 'earlier']:
                        for e in afterTimex:
                            if regex.search(e):
                                # recuperation de sa position 
                                indexConnecteur = word.index(e)
                                # on remplace dans le mot, la partie que la regex trouve par un #s et un compteur
                                word[indexConnecteur] = re.sub(regex, '#s'+str(j), word[indexConnecteur])
                                # incrémentation du compteur
                                j += 1 
            

                # TODO : gestion des as early as / so far...
#                if regex.search(str(envBeforeTimex)):
#                    if 'as' in str(envBeforeTimex) and 'early' in str(envBeforeTimex):
#                        print(str(envBeforeTimex)+" " + str(word[i]))
            

            ### EVENTS ###
            # sinon si le mot courant est un event
            elif '#e' in word[i]: 
                beforeEvent = word[i-1] # mot avant l'event
                envBeforeEvent = word[i-3 : i-1] # 3 mots avant l'event
                listConn = ['after', 'before', 'until', 'when'] # liste de connecteurs
                
                # si le mot d'avant est trouvé par la regex
                if regex.search(beforeEvent):
                    # si le mot fait partie de la liste de connecteurs
                    if beforeEvent.split('#')[0].lower() in listConn:
                        for e in beforeEvent.split():
                            if regex.search(e):
                                # on remplace la partie matché par la regex dans le mot pat un #s+compteur
                                word[i-1] = re.sub(regex, '#s'+str(j), e)
                                # incrémentation du compteur
                                j += 1 
                
                # si la regex trouve un mot dans les 3 mots avant l'event
                if regex.search(str(envBeforeEvent)):
                    # si le mot fait partie de la liste
                    if str(envBeforeEvent).split('#')[0].lower().replace("['", '') in listConn:
                        for e in envBeforeEvent:
                            if regex.search(e):
                                # recuperation de l'index du connecteur 
                                indexConnecteur = word.index(e)
                                if regex.search(e):
                                    # on remplace le before#0#1 par before#s1 grace à sa place dans le texte (indexConnecteur)
                                    word[indexConnecteur] = re.sub(regex, '#s'+str(j),  word[indexConnecteur])
                                    # incrémentation du compteur
                                    j += 1
        # réécriture du fichier dans une chaine vide
        file = ""
        for w in word:
            file += w + " "
        
        # suppression des connecteurs annotés par addDiscourse (ceux qui ne nous intéressent pas)
        for word in file.split():
            if regex.search(word):
                file = (file.replace(regex.search(word).group(), ''))
#        print(file)        
        # écriture des fichiers dans un nouveau dossier        
        with open((path_output+filename), 'w', encoding='utf8') as fileW:
            fileW.write(file)


#stanfordParser() 
#addDiscourse()
cleanTexts()
addSignalId()