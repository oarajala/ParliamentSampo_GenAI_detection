import pandas as pd
import requests
import socket
import re
import os
import time
#from wordcloud import WordCloud
#import matplotlib.pyplot as plt
from utils import helpers, langtools

# Analysis limited to time where lemmatized texts are available.

directory = helpers.get_parent_directory()

asd = pd.read_csv(directory+'/csv_lemmatization_added/speeches_2024.csv', sep=',', header=0)

print(asd.columns)

asd[['session', 'date', 'topic', 'speech_type', 'content']]

print(asd['link'])
print(asd['url'].loc[asd['content_lemmatized'].notna() == True])
print(asd['topic'].unique())

for i in asd['topic'].unique():
    if ('SUULLINEN KYSYMYS' not in i.upper() and 'HALLITUKSEN ESITYS' not in i.upper()):
        print(i)

print(asd['electoral_term'].loc[asd['electoral_term'].notna()==True])

print(len(set(asd['topic'].values)))

for i in (set(asd['topic'].values)):
    print(i)

# test helpers.calculate_electoral_term_progression
print(asd[['date', 'electoral_term']])

asd['electoral_term_progression'] = asd.apply(lambda x: helpers.calculate_electoral_term_progression(x['date'], x['electoral_term']), axis=1)

print(asd[['date', 'electoral_term', 'electoral_term_progression']])


# TEST - read ai_release_timeline.csv -- works 20260105
csv = pd.read_csv(f'{directory}/ai_release_timeline.csv', header=0, encoding='utf-8', sep=';')

print(asd['content'])

asd['words'] = asd.apply(lambda x: langtools.extract_words(x['content']), axis=1)

print(asd[['content', 'words']])

asd['sentences'] = asd.apply(lambda x: langtools.extract_sentences(x['content']), axis=1)

print(asd[['content', 'sentences']])