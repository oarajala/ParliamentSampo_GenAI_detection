import pandas as pd
import requests
import socket
import re
import os
import time
#from wordcloud import WordCloud
#import matplotlib.pyplot as plt
from utils import helpers

# Analysis limited to time where lemmatized texts are available.

directory = helpers.get_parent_directory()

asd = pd.read_csv(directory+'/csv_lemmatization_added/speeches_2024.csv', sep=',', header=0)

print(asd.columns)

asd[['session', 'date', 'topic', 'speech_type', 'content']]

print(asd)
print(asd['url'].loc[asd['content_lemmatized'].notna() == True])
print(asd['topic'].unique())

print(len(set(asd['topic'].values)))

for i in (set(asd['topic'].values)):
    print(i)