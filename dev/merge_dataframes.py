# -*- coding: utf-8 -*-
"""
Created on Tue Mar 12 11:49:19 2019

@author: Sharleyne-Lefevre
"""

import pandas as pd


events = pd.read_csv('CSV/features_events.csv', sep=';')
timexs = pd.read_csv('CSV/features_timex.csv', sep=';')
signaux = pd.read_csv('CSV/features_signaux.csv', sep=';')
contexts = pd.read_csv('CSV/dataframe_contexts.csv', sep=';')
artificial_id = pd.read_csv('CSV/dataframe_id.csv', sep=';')


df = [[events,'events_contexts_id', 'idEvent'], [timexs, 'timexs_contexts_id', 'idTimex'], [signaux, 'signaux_contexts_id', 'idSignal']]

for i in df:
    result = pd.merge(i[0],
                     contexts[['docID', 'id', 'context-4', 'context+4', 'contextPOS-4', 'contextPOS+4', 'contextSTEM-4', 'contextSTEM+4', 'Adv_Negation', 'Adv_Modality']],
                     on=['id', 'docID'])

    result = pd.merge(result,
                     artificial_id[['docID', 'id', 'idWord', 'idSent', i[2]]],
                     on=['id', 'docID'])

    result[i[2]] = pd.to_numeric(result[i[2]], downcast = 'unsigned')
    
    result = result.drop_duplicates()
    result.to_csv('CSV/'+i[1]+'.csv', sep=';', encoding='utf-8') 
    
    
