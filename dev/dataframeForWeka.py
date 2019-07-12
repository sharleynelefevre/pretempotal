# -*- coding: utf-8 -*-
"""
Created on Fri Jul  5 13:24:11 2019

@author: Sharleyne-Lefevre
"""

import pandas as pd 
import time


FILEINPUT = "CSV/events_contexts_id.csv"
TIMEBANKDENSE = "CSV/timebankDenseBeforeAfterIsincludedIncludes.csv"
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
                    output[key][(line.id,line2.id)]['relation']=""
    print("------- Calcul des paires terminé -------")
    return output


def setRelations(data, paires):
    for docId in data.keys():
        for i in range(len(data[docId])):
            row = data[docId][i]
            if (row.e1,row.e2) in paires[docId].keys():
                paires[docId][(row.e1,row.e2)]['relation'] = row.relation
                
                
def applyRules(paires):
    for docId, paire in paires.items():
        for key, value in paire.items():
            tup = value['rows']
            if value['relation'] == "" :
                if tup[0].Tense == "PAST" and tup[1].Tense == "FUTURE" :
                    value['relation'] = "b"
                if tup[0].Tense == "FUTURE" and tup[1].Tense == "PAST" :
                    value['relation'] = "a"    
                if tup[0].Tense == "PRESENT" and tup[1].Tense == "FUTURE" :
                    value['relation'] = "b" 
                    
                if tup[0].Tense == "PRESENT" and tup[0].Aspect == "PERFECTIVE" and tup[1].Tense == "PAST" and tup[1].Aspect == "NONE" :
                    if "that" in str(tup[1].contextMoins4):
                        value['relation'] = "a" 
                        
                if "after" in str(tup[1].contextMoins4) or \
                    "when" in str(tup[1].contextMoins4) or \
                    "since" in str(tup[1].contextMoins4) or\
                    "during" in str(tup[1].contextMoins4) :
                    value['relation'] = "a" 
                    
                if "before" in str(tup[1].contextMoins4) or \
                    "until" in str(tup[1].contextMoins4) :
                    value['relation'] = "b" 
                    
                if tup[0].Class == 'OCCURRENCE' and tup[1].Class == 'OCCURRENCE':
                    if tup[0].Tense == 'PAST' and tup[0].Aspect == "NONE" and tup[1].Tense == 'PAST' and tup[1].Aspect == "PERFECTIVE" or \
                       tup[0].Tense == 'PRESENT' and tup[0].Aspect == "PERFECTIVE" and tup[1].Tense == 'PAST' and tup[1].Aspect == "PERFECTIVE" : 
                       value['relation'] = "a" 
                       
                    elif tup[0].Tense == 'FUTURE' and tup[0].Aspect == "NONE" and tup[1].Tense == 'FUTURE' and tup[1].Aspect == "PERFECTIVE" or \
                         tup[0].Tense == 'FUTURE' and tup[0].Aspect == "PERFECTIVE" and tup[1].Tense == 'FUTURE' and tup[1].Aspect == "NONE" :                
                         value['relation'] = "a" 
                         
                    elif tup[0].Tense == 'PRESENT' and tup[0].Aspect == "NONE" or tup[0].Tense == 'PRESPART' and tup[0].Aspect == "NONE":
                        if tup[1].Tense == 'PAST' and tup[1].Aspect == "PERFECTIVE" or \
                           tup[1].Tense == 'PAST' and tup[1].Aspect == "NONE" or \
                           tup[1].Tense == 'PRESENT' and tup[1].Aspect == "PERFECTIVE":                
                           value['relation'] = "a"     

                    elif tup[0].Tense == 'PRESENT' and tup[0].Aspect == "PERFECTIVE" and tup[1].Tense == 'PAST' and tup[1].Aspect == "NONE" :
                       if not "or" in tup[1].contextMoins4:
                          value['relation'] = "a"  
                
                elif tup[0].Class == 'REPORTING':
                    if tup[0].Tense == 'PAST' and tup[0].Aspect == "NONE" and tup[1].Tense == 'PAST' and tup[1].Aspect == "NONE":
                        if not "would" in str(tup[1].contextMoins4)  and \
                           not "could" in str(tup[1].contextMoins4)  and \
                           not "might" in str(tup[1].contextMoins4)  and \
                           not "should" in str(tup[1].contextMoins4) and \
                           not "and" in str(tup[1].contextMoins4)    and \
                           not "slated" in str(tup[0].contextMoins4) :
                           value['relation'] = "a"    
                
                elif tup[0].Class == 'REPORTING' and tup[1].Class in ["OCCURRENCE", "STATE", "I_STATE", "I_ACTION", "PERCEPTION", "ASPECTUAL"]:
                    if not "when" in str(tup[0].contextMoins4)  and \
                       not "would" in str(tup[1].contextMoins4) and \
                       not "could" in str(tup[1].contextMoins4) and \
                       not "might" in str(tup[1].contextMoins4) and \
                       not "should" in str(tup[1].contextMoins4) :
                       value['relation'] = "a"  
                
                elif tup[0].Class == 'REPORTING' and tup[1].Class == 'REPORTING':
                    if tup[0].Tense == 'PRESPART' and tup[0].Aspect == "NONE" and tup[1].Tense == 'PAST' and tup[1].Aspect == "PERFECTIVE" or \
                       tup[0].Tense == 'PAST' and tup[0].Aspect == "NONE" and tup[1].Tense == 'PAST' and tup[1].Aspect == "PERFECTIVE_PROGRESSIVE" :
                       value['relation'] = "a"  

                    elif tup[0].Tense == 'PAST' and tup[1].Tense == "PRESENT":
                        if not "will" in str(tup[1].contextMoins4):
                            value['relation'] = "a"  

                elif tup[1].Class == "STATE": 
                    if not "would" in str(tup[1].contextMoins4)  and \
                       not "could" in str(tup[1].contextMoins4)  and \
                       not "might" in str(tup[1].contextMoins4)  and \
                       not "should" in str(tup[1].contextMoins4) and \
                       not "that" in str(tup[0].contextMoins4) :
                       value['relation'] = "a"   

                if  tup[0].Class == "I_STATE" and tup[1].Class in ["OCCURRENCE", "STATE", "I_STATE", "I_ACTION", "PERCEPTION", "ASPECTUAL"]:   
                    if not "would" in str(tup[0].contextMoins4) and \
                       not "could" in str(tup[0].contextMoins4) and \
                       not "might" in str(tup[0].contextMoins4) and \
                       not "should" in str(tup[0].contextMoins4):
                       value['relation'] = "a" 
                            
                    if tup[0].Tense != "PAST" and tup[0].Aspect == "NONE" and tup[1].Tense != "PRESENT" and tup[1].Aspect == "NONE":
                        value['relation'] = "a" 

    
def main(fileInput, fileInputRelation, fileOutput):
    start_time = time.time()
    data = initData(fileInput)
    dataRelation = initData(fileInputRelation)
    paires = getPairesEvents(data)
    setRelations(dataRelation, paires)
    applyRules(paires)
    createDataframe(paires, fileOutput)
    print("Temps d execution : %s secondes ---" % (time.time() - start_time))

    
def createDataframe(paires, fileOutput):
    print("------- Extraction du CSV -------")
    df = {}
    df['Paires'] = []
    df['docId'] = []
    df['tenseE1'] = []
    df['tenseE2'] = []
    df['aspectE1'] = []
    df['aspectE2'] = []
    df['classE1'] = []
    df['classE2'] = []
    df['contextMoins4E1'] = []
    df['contextMoins4E2'] = []
    df['contextPlus4E1'] = []
    df['contextPlus4E2'] = []
    df['modalE1'] = []
    df['modalE2'] = []
    df['polarityE1']  = []
    df['polarityE2']  = []
    df['relation']  = [] 
    
    for docId, paire in paires.items():
        for key, value in paire.items():
            tup = value['rows']
            df['Paires'].append(str(tup[0].id) + ", "+ str(tup[1].id))
            df['docId'].append(docId)
            df['tenseE1'].append(tup[0].Tense) # Temps Ev1
            df['tenseE2'].append(tup[1].Tense) # Temps Ev2
            df['aspectE1'].append(tup[0].Aspect) # Aspect Ev1
            df['aspectE2'].append(tup[1].Aspect) # Aspect Ev2
            df['classE1'].append(tup[0].Class) # Classe Ev1
            df['classE2'].append(tup[1].Class) # Classe Ev2
            df['contextMoins4E1'].append(tup[0].contextMoins4)
            df['contextMoins4E2'].append(tup[1].contextMoins4)
            df['contextPlus4E1'].append(tup[0].contextPlus4)
            df['contextPlus4E2'].append(tup[1].contextPlus4)
            df['modalE1'].append(isinstance(tup[0].Modality,str)) # Booléen True si il y a un modal avant Ev1 (NaN = type float (False), sinon type str (True))
            df['modalE2'].append(isinstance(tup[1].Modality,str)) # Booléen True si il y a un modal avant Ev2
            df['polarityE1'].append(tup[0].Polarity) # Polarité Ev1 (POS si non précédé par une négation, sinon NEG)
            df['polarityE2'].append(tup[1].Polarity) # Polarité Ev2 (POS si non précédé par une négation, sinon NEG)
            if 'relation' in value.keys():
                df['relation'].append(value['relation'])
            else:
                df['relation'].append("")
                
    # Mise en dataframe        
    res = pd.DataFrame(dict([(k,pd.Series(v)) for k,v in df.items()]))
    res.to_csv(fileOutput, sep=';', encoding='utf-8') 
    print("------- Extraction du CSV terminée -------")

main(FILEINPUT, TIMEBANKDENSE, FILEOUTPUT)