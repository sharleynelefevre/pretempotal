# -*- coding: utf-8 -*-
"""
Created on Tue Feb 26 13:21:07 2019

@author: Sharleyne-Lefevre
"""
from bs4 import BeautifulSoup
import codecs
import os
import re

from os import path

path_tbaq = "dev/TBAQ-cleaned/"
for foldername in os.listdir(path_tbaq):
    if os.path.isdir(path.join(path_tbaq, foldername)):
        for filename in os.listdir(path.join(path_tbaq, foldername)):
            (basename, ext) = path.splitext(filename)
            if ext == '.tml':
                with open(path.join(path_tbaq, foldername, filename), 'r', encoding='utf8') as file:
                    soup = BeautifulSoup(file.read(), 'xml') # parsing xml


            for eventTag in soup.find_all('EVENT'):  
                # mettre les events au format libelleE#eid
                new_event = ' '.join(['{}#{}'.format(w, eventTag.get('eid')) for w in eventTag.text.split(' ')]) 
                eventTag.string.replace_with(new_event)
                

            for timexTag in soup.find_all('TIMEX3'):   
                # mettre les timexs au format libelleT#tid
                new_timex = ' '.join(['{}#{}'.format(w, timexTag.get('tid')) for w in timexTag.text.split(' ')]) 
                timexTag.string.replace_with(new_timex)

                
            for signalTag in soup.find_all('SIGNAL'):
                # mettre les signaux au format libelleS#sid
                new_signal = ' '.join(['{}#{}'.format(w, signalTag.get('sid')) for w in signalTag.text.split(' ')]) 
                signalTag.string.replace_with(new_signal)

            
            soup = re.sub('<[^<]+>', '', str(soup)) # remove tags
            soup = soup.rstrip("\n\r") # remove empty lines
            
            with open(path.join("dev/TBAQ_txt", basename+".txt"), "w", encoding="utf8") as fileW:
                fileW.write(soup)
