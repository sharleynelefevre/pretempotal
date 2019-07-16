# -*- coding: utf-8 -*-
"""
Created on Fri Jul  5 13:24:11 2019

@author: Sharleyne-Lefevre
"""

import pandas as pd 
import time


FILEINPUT = "CSV/events_contexts_id.csv"
TIMEBANKDENSE = "CSV/timebankDenseCSV.csv"
RELATIONS_DEPENDENCIES = "CSV/relations_event_event.csv"
FILEOUTPUT = "CSV/pairesToWeka.csv"


def initData(file): 
    print("------- Initialisation des données -------")
    # Ouverture du CSV event_context_id.csv
    df = pd.read_csv(file, sep=";")
    data = {}
    # Pour chaque ligne
    for index, rows in df.iterrows():
        # On met le nom des fichiers en clé dans le dictionnaire data
        if not rows.docID in data.keys():
            data[rows.docID] = []
        # Ajout des lignes entières (events+traits) des events du CSV pour une même clé docID (plusieurs events dans un même doc)   
        data[rows.docID].append(rows)
    print("------- Initialisation des données terminée -------")
    return data


def getPairesEvents(data) :
    print("------- Calcul des paires -------")
    output = {}
    # Pour chaque fichier en clé
    for key in data.keys():
        output[key] = {}
        # Pour chaque ligne (event+traits) dont la clé est le nom du doc
        # Deux for pour faire la paire de deux events (line = ev1, line2 = ev2)
        for line in data[key] :
            for line2 in data[key]:
                # Test même document AND Empecher de remonter AND Phrase adjacente
                if line.docID == line2.docID and line2.idEvent > line.idEvent and line.idSent in [(line2.idSent),(line2.idSent-1)]: 
                    output[key][(line.id,line2.id)] = {}
                    output[key][(line.id,line2.id)]['rows'] = (line, line2)
                    output[key][(line.id,line2.id)]['timebankDense'] = ""
                    output[key][(line.id,line2.id)]['rulesAfter'] = ""
                    output[key][(line.id,line2.id)]['rulesBefore'] = ""
    print("------- Calcul des paires terminé -------")
    return output


def setRelations(data, paires): # ajout des relations à partir du csv timebank dense
    for docId in data.keys():
        for i in range(len(data[docId])):
            row = data[docId][i]
            if (row.e1,row.e2) in paires[docId].keys():
                paires[docId][(row.e1,row.e2)]['timebankDense'] = row.relation


def setRelationsDependencies(data, paires): # ajout des relations à partir du csv relation_event_event = analyse en dépendance (deux events séparés par un signal)
    for docId in data.keys():
        for i in range(len(data[docId])):
            row = data[docId][i]
            if (row.id_event1,row.id_event2) in paires[docId].keys():
                paires[docId][(row.id_event1,row.id_event2)]['relationDependency'] = row.typeRelation


def wordNet(paires):
    for docId, paire in paires.items():
        for key, value in paire.items():
            tup = value['rows']
            if isinstance(tup[0].Hyperonyme,str) and isinstance(tup[1].Hyperonyme,str):
                for hypE1 in tup[0].Hyperonyme.split(','):
                    for hypE2 in tup[1].Hyperonyme.split(','):
                        paires[docId][key]['hyperonyme'] = hypE1 == hypE2            
            else:
                paires[docId][key]['hyperonyme'] = False
            if isinstance(tup[0].Synsets,str) and isinstance(tup[1].Synsets,str):
                for synE1 in tup[0].Synsets.split(','):
                    for synE2 in tup[1].Synsets.split(','):
                        paires[docId][key]['synonyme'] = synE1 == synE2
            else:
                paires[docId][key]['synonyme'] = False
                        

p1 = "PAST-PERFECTIVE"
p2 = "PAST-NONE"
p4 = "PRESENT-PERFECTIVE"

f1 = "FUTURE-NONE"
f2 = "FUTURE-PERFECTIVE"
f3 = "FUTURE-NONE"

n = "PRESENT-NONE"

def applyRulesConcordTemps(paires): # relations récupérées à partir de la théorie du temps de Reichenbach
    for docId, paire in paires.items():
        for key, value in paire.items():
            tup = value['rows']     
            
            e1 = str(tup[0].Tense)+"-"+str(tup[0].Aspect)
            e2 = str(tup[1].Tense)+"-"+str(tup[1].Aspect)
            
            
            
            if e1 == p2 and e2 == p1 or \
               e1 == p4 and e2 == p1 or \
               e1 == p4 and e2 == p2 or \
               e1 == f1 and e2 == f2 or \
               e1 == f2 and e2 == f3 or \
               e1 == n  and e2 == p1 or \
               e1 == n  and e2 == p2 or \
               e1 == n  and e2 == p4 or \
               e1 == f2 and e2 == n  or \
               e1 == n  and e2 == f1 or \
               e1 == n  and e2 == f3 :
               
               value['concordTemps'] = "a" 
               
            if e1 == p1 and e2 == p1 or \
               e1 == p1 and e2 == p2 or \
               e1 == p1 and e2 == p4 or \
               e1 == p2 and e2 == p2 or \
               e1 == p2 and e2 == p4 or \
               e1 == p4 and e2 == p4 or \
               e1 == f1 and e2 == f1 or \
               e1 == f2 and e2 == f1 or \
               e1 == f2 and e2 == f2 or \
               e1 == f3 and e2 == f2 or \
               e1 == f3 and e2 == f3 or \
               e1 == n  and e2 == n  or \
               e1 == p1 and e2 == n  or \
               e1 == p2 and e2 == n  or \
               e1 == p4 and e2 == n  or \
               e1 == f1 and e2 == n  or \
               e1 == f3 and e2 == n  or \
               e1 == n  and e2 == f2 :
       
               value['concordTemps'] = "b" 
               
               
def applyRules(paires):
    for docId, paire in paires.items():
        for key, value in paire.items():
            tup = value['rows']
            e1 = str(tup[0].Tense)+"-"+str(tup[0].Aspect)
            e2 = str(tup[1].Tense)+"-"+str(tup[1].Aspect)
            
            if value['rulesBefore'] == "" or value['rulesAfter'] == "":
                if tup[0].Tense == "PAST" and tup[1].Tense == "FUTURE" :
                    value['rulesBefore'] = "b"
                if tup[0].Tense == "FUTURE" and tup[1].Tense == "PAST" :
                    value['rulesAfter'] = "a"    
                if tup[0].Tense == "PRESENT" and tup[1].Tense == "FUTURE" :
                    value['rulesBefore'] = "b" 
                    
                if e1 == p4 and e2 == p2 :
                    if "that" in str(tup[1].contextMoins4):
                        value['rulesAfter'] = "a" 
               
                if "after" in str(tup[1].contextMoins4) or \
                    "when" in str(tup[1].contextMoins4) or \
                    "since" in str(tup[1].contextMoins4) or\
                    "during" in str(tup[1].contextMoins4) :
                    value['rulesAfter'] = "a" 
                    
                if "before" in str(tup[1].contextMoins4) or \
                    "until" in str(tup[1].contextMoins4) :
                    value['rulesBefore'] = "b" 
                    
                if tup[0].Class == 'OCCURRENCE' and tup[1].Class == 'OCCURRENCE':
                    if e1 == p2 and e2 == p1 or \
                       e1 == p4 and e2 == p1 : 
                       value['rulesAfter'] = "a" 
                       
                    elif e1 == f1 and e2 == f2 or \
                         e1 == f2 and e2 == f1 :                
                         value['rulesAfter'] = "a" 
                         
                    elif e1 == n or tup[0].Tense == 'PRESPART' and tup[0].Aspect == "NONE":
                        if e2 == p1 or \
                           e2 == p2 or \
                           e2 == p4:                
                           value['rulesAfter'] = "a"     
    
                    elif e1 == p4 and e2 == p2 :
                       if not "or" in tup[1].contextMoins4:
                          value['rulesAfter'] = "a"  
                 
                elif tup[0].Class == 'REPORTING':
                    if e1 == p2 and e2 == p2:
                        if not "would" in str(tup[1].contextMoins4)  and \
                           not "could" in str(tup[1].contextMoins4)  and \
                           not "might" in str(tup[1].contextMoins4)  and \
                           not "should" in str(tup[1].contextMoins4) and \
                           not "and" in str(tup[1].contextMoins4)    and \
                           not "slated" in str(tup[0].contextMoins4) :
                           value['rulesAfter'] = "a"    
               
                        
                elif tup[0].Class == 'REPORTING' and tup[1].Class in ["OCCURRENCE", "STATE", "I_STATE", "I_ACTION", "PERCEPTION", "ASPECTUAL"]:
                    if not "when" in str(tup[0].contextMoins4)  and \
                       not "would" in str(tup[1].contextMoins4) and \
                       not "could" in str(tup[1].contextMoins4) and \
                       not "might" in str(tup[1].contextMoins4) and \
                       not "should" in str(tup[1].contextMoins4) :
                       value['rulesAfter'] = "a"  
              
                       
                elif tup[0].Class == 'REPORTING' and tup[1].Class == 'REPORTING':
                    if tup[0].Tense == 'PRESPART' and tup[0].Aspect == "NONE" and e2 == p1 or \
                       e1 == p2 and tup[1].Tense == 'PAST' and tup[1].Aspect == "PERFECTIVE_PROGRESSIVE" :
                       value['rulesAfter'] = "a"  
    
                    elif tup[0].Tense == 'PAST' and tup[1].Tense == "PRESENT":
                        if not "will" in str(tup[1].contextMoins4):
                            value['rulesAfter'] = "a"  
     
                        
                elif tup[1].Class == "STATE": 
                    if not "would" in str(tup[1].contextMoins4)  and \
                       not "could" in str(tup[1].contextMoins4)  and \
                       not "might" in str(tup[1].contextMoins4)  and \
                       not "should" in str(tup[1].contextMoins4) and \
                       not "that" in str(tup[0].contextMoins4) :
                       value['rulesAfter'] = "a"   

                        
                if  tup[0].Class == "I_STATE" and tup[1].Class in ["OCCURRENCE", "STATE", "I_STATE", "I_ACTION", "PERCEPTION", "ASPECTUAL"]:   
                    if not "would" in str(tup[0].contextMoins4) and \
                       not "could" in str(tup[0].contextMoins4) and \
                       not "might" in str(tup[0].contextMoins4) and \
                       not "should" in str(tup[0].contextMoins4):
                       value['rulesAfter'] = "a" 

                    if e1 == p2 and e2 == n:
                        value['rulesAfter'] = "a" 

    
def main(fileInput, fileInputRelation, fileInputRelationDependency, fileOutput):
    start_time = time.time()
    data = initData(fileInput)
    dataRelation = initData(fileInputRelation)
    dataRelationDependency = initData(fileInputRelationDependency)
    paires = getPairesEvents(data)
    wordNet(paires)
    setRelations(dataRelation, paires)
    setRelationsDependencies(dataRelationDependency, paires)
    applyRulesConcordTemps(paires)
    applyRules(paires)
    createDataframe(paires, fileOutput)
    print("Temps d execution : %s secondes ---" % (time.time() - start_time))

    
def createDataframe(paires, fileOutput):
    print("------- Extraction du CSV -------")
    df = {}
    df['event1'] = []
    df['event2'] = []
    df['docId'] = []
    df['sameLemme'] = []
    
    df['tenseE1'] = []
    df['tenseE2'] = []
    df['sameTense'] = []
    
    df['aspectE1'] = []
    df['aspectE2'] = []
    df['sameAspect'] = []
    
    df['classE1'] = []
    df['classE2'] = []
    df['sameClass'] = []
    
    df['posE1'] = []
    df['posE2'] = []
    df['samePOS'] = []
    
#    df['contextPOSMoins4E1'] = []
#    df['contextPOSMoins4E2'] = []
#    df['contextPOSPlus4E1'] = []
#    df['contextPOSPlus4E2'] = []
    
    df['modalE1'] = []
    df['modalE2'] = []
    
    df['polarityE1']  = []
    df['polarityE2']  = []
    
    df['synonyme'] = []
    df['hyperonyme'] = []
    
    df['timebankDense']  = [] 
    df['concordTemps'] = []
    df['rulesAfter']  = [] 
    df['rulesBefore']  = [] 
    df['relationDependency'] = []
    

    
    for docId, paire in paires.items():
        for key, value in paire.items():
            tup = value['rows']
            df['event1'].append(tup[0].id)
            df['event2'].append(tup[1].id)
            
            df['sameLemme'].append(tup[0].LemmeNltk == tup[1].LemmeNltk)
            df['docId'].append(docId)
            df['tenseE1'].append(tup[0].Tense) # Temps Ev1
            df['tenseE2'].append(tup[1].Tense) # Temps Ev2
            df['sameTense'].append(tup[0].Tense == tup[1].Tense)
            df['aspectE1'].append(tup[0].Aspect) # Aspect Ev1
            df['aspectE2'].append(tup[1].Aspect) # Aspect Ev2
            df['sameAspect'].append(tup[0].Aspect == tup[1].Aspect) # booléen même aspect            
            df['classE1'].append(tup[0].Class) # Classe Ev1
            df['classE2'].append(tup[1].Class) # Classe Ev2
            df['sameClass'].append(tup[0].Class == tup[1].Class)
#            df['contextPOSMoins4E1'].append(tup[0].contextPOSMoins4)
#            df['contextPOSMoins4E2'].append(tup[1].contextPOSMoins4)
#            df['contextPOSPlus4E1'].append(tup[0].contextPOSPlus4)
#            df['contextPOSPlus4E2'].append(tup[1].contextPOSPlus4)
            df['modalE1'].append(isinstance(tup[0].Modality,str)) # Booléen True si il y a un modal avant Ev1 (NaN = type float (False), sinon type str (True))
            df['modalE2'].append(isinstance(tup[1].Modality,str)) # Booléen True si il y a un modal avant Ev2
            df['polarityE1'].append(tup[0].Polarity) # Polarité Ev1 (POS si non précédé par une négation, sinon NEG)
            df['polarityE2'].append(tup[1].Polarity) # Polarité Ev2 (POS si non précédé par une négation, sinon NEG)
            df['rulesAfter'].append(value['rulesAfter'] == 'a')
            df['rulesBefore'].append(value['rulesBefore'] == 'b')
            df['synonyme'].append(value['synonyme'])
            df['hyperonyme'].append(value['hyperonyme'])
            df['posE1'].append(tup[0].POS)
            df['posE2'].append(tup[1].POS)
            df['samePOS'].append(tup[0].POS == tup[1].POS)
            df['timebankDense'].append(value['timebankDense'])
            
            if 'relationDependency' in value.keys():
                df['relationDependency'].append(value['relationDependency'])
            else:
                df['relationDependency'].append("")
                
            if 'concordTemps' in value.keys():
                df['concordTemps'].append(value['concordTemps'])
            else:
                df['concordTemps'].append("")

                
    # Mise en dataframe        
    res = pd.DataFrame(dict([(k,pd.Series(v)) for k,v in df.items()]))
    res.to_csv(fileOutput, sep=';', encoding='utf-8') 
    print("------- Extraction du CSV terminée -------")

main(FILEINPUT, TIMEBANKDENSE, RELATIONS_DEPENDENCIES, FILEOUTPUT)




