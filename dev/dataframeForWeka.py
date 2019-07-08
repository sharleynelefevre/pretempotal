# -*- coding: utf-8 -*-
"""
Created on Fri Jul  5 13:24:11 2019

@author: Sharleyne-Lefevre
"""

import pandas as pd 
import time


FILEINPUT = "CSV/events_contexts_id.csv"
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
        output[key] = []
        # Pour chaque ligne (event+traits) dont la clé est le nom du doc
        # Deux for pour faire la paire de deux events (line = ev1, line2 = ev2)
        for line in data[key] :
            for line2 in data[key]:
                # Test même document AND Empecher de remonter AND Phrase adjacente
                if line.docID == line2.docID and line2.idEvent > line.idEvent and line.idSent in [(line2.idSent),(line2.idSent-1)]: 
                    output[key].append((line, line2))
    print("------- Calcul des paires terminé -------")
    return output

    
def main(fileInput, fileOutput):
    start_time = time.time()
    data = initData(fileInput)
    paires = getPairesEvents(data)
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
    df['modalE1'] = []
    df['modalE2'] = []
    df['polarityE1']  = []
    df['polarityE2']  = []
    df['relation']  = [] # a faire
    
    for docId, paire in paires.items():
        for i in range(len(paire)):
            df['Paires'].append(str(paire[i][0].id) + ", "+ str(paire[i][1].id))
            df['docId'].append(docId)
            df['tenseE1'].append(paire[i][0].Tense) # Temps Ev1
            df['tenseE2'].append(paire[i][1].Tense) # Temps Ev2
            df['aspectE1'].append(paire[i][0].Aspect) # Aspect Ev1
            df['aspectE2'].append(paire[i][1].Aspect) # Aspect Ev2
            df['classE1'].append(paire[i][0].Class) # Classe Ev1
            df['classE2'].append(paire[i][1].Class) # Classe Ev2
            df['modalE1'].append(paire[i][0].Modality == None) # Booléen True si il y a un modal avant Ev1
            df['modalE2'].append(paire[i][1].Modality == None) # Booléen True si il y a un modal avant Ev2
            df['polarityE1'].append(paire[i][0].Polarity) # Polarité Ev1 (POS si non précédé par une négation, sinon NEG)
            df['polarityE2'].append(paire[i][1].Polarity) # Polarité Ev2 (POS si non précédé par une négation, sinon NEG)
            df['relation'].append("") # a faire
    # Mise en dataframe        
    res = pd.DataFrame(dict([(k,pd.Series(v)) for k,v in df.items()]))
    res.to_csv(fileOutput, sep=';', encoding='utf-8') 
    print("------- Extraction du CSV terminée -------")

main(FILEINPUT, FILEOUTPUT)
