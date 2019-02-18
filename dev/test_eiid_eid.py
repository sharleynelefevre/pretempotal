# -*- coding: utf-8 -*-
"""
Created on Thu Feb 14 15:50:41 2019

@author: Sharleyne-Lefevre
"""
import os
import codecs
from bs4 import BeautifulSoup
import pandas as pd

# Permet de verifier si un event peut avoir plusieurs makeinstances
# si oui on recupere l'identifiant du document
path = "dev/TBAQ-cleaned/"

# ouverture des fichiers des repertoires aq et tb
for foldername in os.listdir(path):
    if os.path.isdir(path+foldername):
        for filename in os.listdir(path+foldername):
            if '.tml' in filename:
                file = codecs.open(path+foldername+'/'+filename, 'r', 'utf8') 
                soup = BeautifulSoup(file.read(), 'xml') 
                file.close()
                
            # recuperation du docid
            docid = soup.find('DOCID').text
            
            # dataframe des makeinstances
            instances = {}
            instances['docid'] = []
            instances['eiid'] = []
            for instanceTag in soup.find_all('MAKEINSTANCE'):
                instances['eiid'].append(instanceTag.get('eiid'))
                instances['docid'].append(docid)
            
            # dataframe des events
            eventid = {}
            eventid['eid'] = []    
            for eventTag in soup.find_all('EVENT'):
                eventid['eid'].append(eventTag.get('eid'))

            dataInstances = instances
            df1 = pd.DataFrame(dataInstances)
            dataEvents = eventid
            df2 = pd.DataFrame(dataEvents)   
            
            # concatenation des deux dataframes
            df = pd.concat([df1, df2], axis=1, sort=False)
            
            # test si on trouve plusieurs makeinstances pour un meme eid
            for rowId, row in df.iterrows() :
                encounters = []
                for rowId2, row2 in df.iterrows() :
                    if row2["eid"] == row["eid"] :
                        idInstance = row['eiid']
                        if not idInstance in encounters:
                            encounters.append(idInstance)
                        else:
                            print(row2["eid"] + ' ' + docid) # Resultat : il n'y a pas d'event ayant plusieurs makeinstances