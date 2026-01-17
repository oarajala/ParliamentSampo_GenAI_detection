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

print(freq[['word', 'n_2025', 'norm_2025']].loc[freq['n_2025'].idxmax(skipna=True)])

for i, d in freq[['word', 'n_2021', 'n_2022', 'n_2023_predicted', 'n_2023', 'n_2023_diffs']].loc[freq['n_2023'] > freq['n_2023_predicted']].iterrows():
    if (re.search(r'\w+', d.word) is not None) & (len(d.word)) >= 3 & ('/' not in d.word):
        print(f'word: {d.word} | n_2021: {d.n_2021} | n_2022: {d.n_2022} | n_2023_predicted: {d.n_2023_predicted} | n_2023: {d.n_2023} | n_2023_diffs: {d.n_2023_diffs}')    

for i, d in freq.loc[freq['n_2023'] > freq['norm_2023_predicted']].sort_values(by='norm_2024_diffs', ascending=True).iterrows():
    if (re.search(r'\w+', d.word) is not None) & (len(d.word)) >= 3 & ('/' not in d.word):
        print(f'word: {d.word} | norm_2021: {float(d.norm_2021)} | norm_2022: {d.norm_2022} | n_2023_predicted: {d.norm_2023_predicted} | norm_2023: {d.norm_2023} | n_2023_diffs: {float(d.norm_2023_diffs)} | n_2023_ratios: {d.norm_2023_ratios}')    

for i, d in freq.loc[(freq['norm_2023'] > freq['norm_2023_predicted'])&(freq['norm_2024'] > freq['norm_2024_predicted'])&(freq['norm_2025'] > freq['norm_2025_predicted'])].sort_values(by='norm_2024_ratios', ascending=True).iterrows():
    print(f'word: {d.word} | norm_2022: {d.norm_2022} | norm_2023_predicted: {d.norm_2023_predicted} | norm_2023: {d.norm_2023} | norm_2024_predicted: {d.norm_2024_predicted} | norm_2024: {d.norm_2024} | norm_2025_predicted: {d.norm_2025_predicted} | norm_2025: {d.norm_2025}')

# check the largest 2023, 2024, 2025 r scores (ratio)
# pick the words with large ratios per 2023, 2024, 2025 to separate analysis df
for i, d in freq.loc[freq['n_2023'] > freq['n_2023_predicted']].sort_values(by='n_2023_ratios', ascending=True).iterrows():
    if (re.search(r'\w+', d.word) is not None) & (len(d.word)) >= 3 & ('/' not in d.word):
        print(f'word: {d.word} | n_2021: {d.n_2021} | n_2022: {d.n_2022} | n_2023_predicted: {d.n_2023_predicted} | n_2023: {d.n_2023} | n_2023_diffs: {d.n_2023_diffs} | n_2023_ratios: {d.n_2023_ratios}')    

