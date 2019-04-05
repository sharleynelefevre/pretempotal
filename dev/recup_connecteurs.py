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
    os.environ['CLASSPATH'] = "stanford-parser/stanford-parser-full-2018-10-17"
    os.environ['JAVAHOME'] = "D:/Program Files/java/bin"

    parser = StanfordParser(model_path = "edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz")
    path_input = "ressources/TBAQ-txt-annot/TimeBank/"    
    path_output = 'ressources/TBAQ-txt-annot/TimeBank_StanfordParser/' 
     
    for filename in os.listdir(path_input):
        print(filename)
        file = codecs.open(path_input+filename, 'r', 'utf8').read()
        
        file = file.lstrip().replace('\r\n\r\n\r\n', ' ').replace('\r\n\r\n', ' ').replace('\r\n', ' ')
        sents = nltk.sent_tokenize(file)
    
        parsedText = ""
        for sent in sents:
            constituancies = list(parser.raw_parse(sent))
            constituancies = re.sub(r'''(\[)(Tree)(\()('ROOT')(\,)( )(\[)(Tree)''', '(S1 (S ', str(constituancies))
            constituancies = re.sub(r'''(((\,)( )(\[)(Tree))|((\,)( )(Tree)))''', ' ', str(constituancies))
            constituancies = re.sub(r'''(\[)((')|("))|((')|("))(\])''', "'", str(constituancies))
            constituancies = re.sub(r'''(\])''', ')', str(constituancies))
            constituancies = re.sub(r'''(')''', '', str(constituancies))
            parsedText += str(constituancies)
            
        with open((path_output+filename), 'w', encoding='utf8') as fileW:
            fileW.write(parsedText)


def addDiscourse():
    path_addDiscourse = "C:/Users/Sharleyne-Lefevre/Desktop/stage_LIFO/pretempotal/dev/addDiscourse/addDiscourse.pl"
    path_input = 'ressources/TBAQ-txt-annot/TimeBank_StanfordParser/' 
    path_output = "ressources/TBAQ-txt-annot/TimeBank_AddDiscourse/"

    for filename in os.listdir(path_input):
        file = path_input+filename
        os.system(path_addDiscourse+' --parses '+file+' --output '+path_output+filename)
    

def cleanTexts():
    path_input = "ressources/TBAQ-txt-annot/TimeBank_AddDiscourse/"
    path_output = "ressources/TBAQ-txt-annot/TimeBank_Connecteurs/"
    
    texts = {}
    for filename in os.listdir(path_input):
        file = codecs.open(path_input+filename, 'r', 'utf8').read()
        texts[filename.replace(".txt","")] = file
    
    for fileName, fileContent in texts.items():    
        # remplacement des balises, des syntagmes et des postags par un espace """
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
        cleanedContent = re.sub(r'''( )(#)(\,)(\#)( )''', '  #  ', cleanedContent) 
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
        #pour les # 50 million on # 980 million -> #50 million on #980 million
        cleanedContent = re.sub(r'''(\#)(\,)(\#)( )''', ' #', cleanedContent) 
        # pour wsj _ 0376 -> wsj_0376
        cleanedContent = re.sub(r'(wsj)( )(\_)( )', 'wsj_', cleanedContent) 
        # pour les next#t90>year s#t90>first#t90>quarter#t90 -> next#t90>year's#t90>first#t90>quarter#t90
        cleanedContent = re.sub(r'( )(s)(\#)(t)', ''''s#t''', cleanedContent) 

        with open((path_output+fileName+'.txt'), 'w', encoding='utf8') as fileW:
            fileW.write(cleanedContent)
            

def addSignalId(): # A AMELIORER + COMMENTER
    path_input = "ressources/TBAQ-txt-annot/TimeBank_Connecteurs/"
    path_output = "ressources/TBAQ-txt-annot/TimeBank_NewInput/"

    regex = re.compile(r'(\#)[0-9]{1,}(\#)(0|Temporal|Contingency|Comparison|Expansion)')
    
    for filename in os.listdir(path_input):
        file = codecs.open(path_input+filename, 'r', 'utf8').read()        
        j = 1        

        word = []
        for w in file.split():
            word.append(w)
        
        for i in range(len(word)): 
            afterTimex = word[i+1 : i+2]
            beforeTimex = word[i-1]
            beforeEvent = word[i-1]
            envBeforeEvent = word[i-3 : i-1]
            
            ### TIMEX ###
            if '#t' in word[i]:
                if regex.search(beforeTimex) : 
                    if not beforeTimex.split('#')[0] in ['but', 'But', 'next', 'separately']:
                        for e in beforeTimex.split():
                            if regex.search(e):
                                word[i-1] = re.sub(regex, '#s'+str(j), e)
                                j += 1 
            
                elif beforeTimex in ['in','In', 'on', 'On', 'over', 'Over', 'during', 'During', 'at', 'At'] :
                    word[i-1] = beforeTimex.replace(beforeTimex, beforeTimex+'#s'+str(j))               
                    j += 1  
            
                if regex.search(str(afterTimex)): 
                    if str(afterTimex).split('#')[0].replace("['", '') in ['before', 'after', 'later']:
                        for e in afterTimex:
                            if regex.search(e):
                                indexConnecteur = word.index(e)
                                word[indexConnecteur] = re.sub(regex, '#s'+str(j), word[indexConnecteur])
                                j += 1 
            
            # TODO : gestion des as early as / so far...

            ### EVENTS ###
            elif '#e' in word[i]:                
                if regex.search(beforeEvent):
                    if beforeEvent.split('#')[0] in ['after', 'before', 'After', 'Before']:
                        for e in beforeEvent.split():
                            if regex.search(e):
                                word[i-1] = re.sub(regex, '#s'+str(j), e)
                                j += 1 
                                    
                if regex.search(str(envBeforeEvent)):
                    if str(envBeforeEvent).split('#')[0].replace("['", '') in ['after', 'before', 'After', 'Before', 'until', 'Until']:
                        for e in envBeforeEvent:
                            if regex.search(e):
                                # recuperation de l'index du connecteur 
                                indexConnecteur = word.index(e)
                                if regex.search(e):
                                    # remplacer le before#0#1 par before#s1 grace à sa place dans le texte (indexConnecteur)
                                    word[indexConnecteur] = re.sub(regex, '#s'+str(j),  word[indexConnecteur])
                                    j += 1
        file = ""
        for w in word:
            file += w + " "
        
        for word in file.split():
            if regex.search(word):
                file = (file.replace(regex.search(word).group(), ''))
                
        with open((path_output+filename), 'w', encoding='utf8') as fileW:
            fileW.write(file)


stanfordParser() 
addDiscourse()
cleanTexts()
addSignalId()