import pandas as pd
import requests
import socket
import re
import os
import time
from scipy import stats
#from wordcloud import WordCloud
import matplotlib.pyplot as plt
from utils import helpers
directory = helpers.get_parent_directory()

# read csv for analysis from csv_analysis directory
freq = pd.read_csv(f'{directory}/csv_analysis/word_frequency_all_years.csv', sep=';', encoding='utf-8')

# note: small peeks into the set at this point
print(freq[['word', 'n_2021', 'n_2022', 'n_2023_predicted', 'n_2023', 'n_2024_predicted', 'n_2024', 'n_2025_predicted', 'n_2025', 'n_2023_diffs', 'n_2023_ratios',
            'n_2024_diffs', 'n_2024_ratios', 'n_2025_diffs', 'n_2025_ratios']].loc
      [(freq['n_2023'] > freq['n_2023_predicted'])&(freq['n_2024'] > freq['n_2024_predicted'])&(freq['n_2025'] > freq['n_2025_predicted'])]
      .sort_values(by='n_2025_diffs', ascending=False))

input_cols = [col for col in freq.columns if re.search(r'n_\d+$', col) is not None]
for col in input_cols:
    col_max = freq[col].max(skipna=True)
    col_min = freq[col].min(skipna=True)
    print(f'col: {col}, col_max: {col_max}, col_min: {col_min}')
    new_col = f'norm_{re.search(r'[0-9]+', col)[0]}'
    freq[new_col] = None
    freq[new_col] = freq.apply(lambda x: None if type(x) != float is None else (x[col]-col_min)/(col_max-col_min), axis=1)

print(freq[['word', 'n_2025', 'norm_2025']].loc[freq['n_2025'].idxmax(skipna=True)])

freq['norm_2021'] = freq.apply(lambda x: None if x is None else (x['n_2021'] - freq['n_2021'].min(skipna=True))/(freq['n_2021'].max(skipna=True) - freq['n_2021'].min(skipna=True)), axis=1)
print(freq[['word', 'n_2021', 'norm_2021']])

print(freq[['word', 'n_2021', 'n_2022', 'n_2023_predicted', 'n_2023']].loc[freq['n_2023'] > freq['n_2023_predicted']])

for i, d in freq[['word', 'n_2021', 'n_2022', 'n_2023_predicted', 'n_2023', 'n_2023_diffs']].loc[freq['n_2023'] > freq['n_2023_predicted']].iterrows():
    if (re.search(r'\w+', d.word) is not None) & (len(d.word)) >= 3 & ('/' not in d.word):
        print(f'word: {d.word} | n_2021: {d.n_2021} | n_2022: {d.n_2022} | n_2023_predicted: {d.n_2023_predicted} | n_2023: {d.n_2023} | n_2023_diffs: {d.n_2023_diffs}')    

for i, d in freq.loc[freq['n_2023'] > freq['n_2023_predicted']].sort_values(by='n_2023_diffs', ascending=True).iterrows():
    if (re.search(r'\w+', d.word) is not None) & (len(d.word)) >= 3 & ('/' not in d.word):
        print(f'word: {d.word} | n_2021: {d.n_2021} | n_2022: {d.n_2022} | n_2023_predicted: {d.n_2023_predicted} | n_2023: {d.n_2023} | n_2023_diffs: {d.n_2023_diffs} | n_2023_ratios: {d.n_2023_ratios}')    

# check the largest 2023, 2024, 2025 r scores (ratio)
# pick the words with large ratios per 2023, 2024, 2025 to separate analysis df
for i, d in freq.loc[freq['n_2023'] > freq['n_2023_predicted']].sort_values(by='n_2023_ratios', ascending=True).iterrows():
    if (re.search(r'\w+', d.word) is not None) & (len(d.word)) >= 3 & ('/' not in d.word):
        print(f'word: {d.word} | n_2021: {d.n_2021} | n_2022: {d.n_2022} | n_2023_predicted: {d.n_2023_predicted} | n_2023: {d.n_2023} | n_2023_diffs: {d.n_2023_diffs} | n_2023_ratios: {d.n_2023_ratios}')    

