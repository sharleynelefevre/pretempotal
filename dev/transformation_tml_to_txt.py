# -*- coding: utf-8 -*-
'''
Created on Tue Feb 26 13:21:07 2019

@author: Sharleyne-Lefevre
'''
from bs4 import BeautifulSoup
import os
from os import path

path_tbaq = 'ressources/TBAQ-cleaned/'
for foldername in os.listdir(path_tbaq):
    if os.path.isdir(path.join(path_tbaq, foldername)):
        output_dir = path.join('ressources', 'TBAQ-txt', foldername)
        if not path.isdir(output_dir):
            os.mkdir(path.join('ressources', 'TBAQ-txt', foldername))
            
        for filename in os.listdir(path.join(path_tbaq, foldername)):
            (basename, ext) = path.splitext(filename)
            if ext == '.tml':
                with open(path.join(path_tbaq, foldername, filename), 'r', encoding='utf8') as file:
                    soup = BeautifulSoup(file.read(), 'xml') # parsing xml

            dct =  soup.find('DCT')
            title = soup.find('TITLE')
            text = soup.find('TEXT')

            toWrite = ""
            for date in dct:
                toWrite += str('>'.join(['{}#{}'.format(j, date.get('tid')) for j in date.text.split(' ')]))+'.'+'\n'
          
            if title:
                toWrite += str(title.text)+'.'
                
            for eventTag in text.find_all('EVENT'): 
                if " " in eventTag.text:
                    eventTag.string = eventTag.string.replace(' ','')                
                # mettre les events au format libelleE#eid
                # separateur d'unite lexicale : >
                new_event = '>'.join(['{}#{}'.format(w, eventTag.get('eid')) for w in eventTag.text.split(' ')]) 
                eventTag.string.replace_with(new_event)
                
            for timexTag in text.find_all('TIMEX3') :  
                if ',' in timexTag.text :
                    contentText = timexTag.text.replace(',','')
                    # mettre les timexs au format libelleT#tid en retirant la virgule           
                    new_timex = '>'.join(['{}#{}'.format(w, timexTag.get('tid')) for w in contentText.split(' ')]) 
                    timexTag.string.replace_with(new_timex)
                else:
                    # mettre les timexs au format libelleT#tid
                    new_timex = '>'.join(['{}#{}'.format(w, timexTag.get('tid')) for w in timexTag.text.split(' ')]) 
                    timexTag.string.replace_with(new_timex)
                                 
            for signalTag in text.find_all('SIGNAL'):
                # mettre les signaux au format libelleS#sid
                new_signal = '>'.join(['{}#{}'.format(w, signalTag.get('sid')) for w in signalTag.text.split(' ')]) 
                signalTag.string.replace_with(new_signal)
            
            toWrite += text.text.rstrip('\n')

            with open(path.join(output_dir, basename+'.txt'), 'w', encoding='utf8') as fileW:
                fileW.write(toWrite)