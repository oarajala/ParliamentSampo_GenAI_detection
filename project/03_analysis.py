import pandas as pd
import numpy as np
#import requests
#import socket
import re
import os
import time
from scipy import stats
#from wordcloud import WordCloud
import matplotlib.pyplot as plt
from utils import helpers
import simplemma
directory = helpers.get_parent_directory()

# read csv for analysis from csv_analysis directory
freq = pd.read_csv(f'{directory}/csv_analysis/word_frequency_all_years.csv', sep=';', encoding='utf-8')

# note: small peeks into the set at this point
df = freq.loc[(freq['norm_2023']>freq['norm_2022'])&(freq['norm_2024']>freq['norm_2022'])&(freq['norm_2025']>freq['norm_2022'])
              &(freq['norm_2023']>freq['norm_2023_predicted'])&(freq['norm_2024']>freq['norm_2024_predicted'])&(freq['norm_2025']>freq['norm_2025_predicted'])].sort_values(by='norm_2025', ascending=False)
               
print(df[['word','norm_2021','norm_2022','norm_2023','norm_2023_ratios','norm_2024','norm_2025']].sort_values(by='norm_2023_ratios', ascending=True))
save_file_name = 'analysis_first_peek.csv'
if save_file_name in os.listdir(f'{directory}/csv_analysis/'):
    os.remove(f'{directory}/csv_analysis/{save_file_name}')
df.to_csv(f'{directory}/csv_analysis/{save_file_name}', sep=';', header=True, index=False, encoding='utf-8')

cols = ['word', 'norm_2000', 'norm_2001', 'norm_2002','norm_2003', 'norm_2004', 'norm_2005', 'norm_2006', 'norm_2007',
        'norm_2008', 'norm_2009', 'norm_2010', 'norm_2011', 'norm_2012', 'norm_2013', 'norm_2014', 'norm_2015', 'norm_2016', 
        'norm_2017','norm_2018', 'norm_2019', 'norm_2020', 'norm_2021', 'norm_2022', 'norm_2023', 'norm_2024', 'norm_2025', 
        'norm_2023_predicted','norm_2023_diffs', 'norm_2023_ratios', 'norm_2024_predicted', 'norm_2024_diffs', 'norm_2024_ratios', 
        'norm_2025_predicted','norm_2025_diffs', 'norm_2025_ratios']
df = pd.read_csv(f'{directory}/csv_analysis/analysis_first_peek.csv', sep=';', encoding='utf-8', usecols=cols)


freq.loc[freq['word']=='tekoäly']
df['norm_2025_ratios'].values.astype(np.float64).max()
df['norm_2025_diffs'].values.max()


df['word'].loc[(df['norm_2023_diffs']>0.01)|(df['norm_2024_diffs']>0.01)|(df['norm_2025_diffs']>0.01)]
# np.log10(ratios[ind]) > np.log10(2) - (np.log10(x[ind]) + 4) * (np.log10(2) / 4):
df_logs = pd.DataFrame()
df_logs[['word', 'norm_2023', 'norm_2023_diffs', 'norm_2023_ratios']] = df[['word', 'norm_2023', 'norm_2023_diffs', 'norm_2023_ratios']]
df_logs['log10_r'] = df_logs.apply(lambda x: np.log10(x['norm_2023_ratios']), axis=1) #> np.log10(2) - (np.log10(df['norm_2023'])+4) * (np.log10(2)/4)
df_logs['log_div'] = df_logs.apply(lambda x: np.log10(2)-((np.log10(x['norm_2023'])+4) * (np.log10(2)/4)), axis=1)
df_logs['comparison'] = df_logs.apply(lambda x: True if x['log10_r']>x['log_div'] else False, axis=1)
print(df_logs)
df['log_comp'] = df_logs['comparison']
df['word'].loc[(df['norm_2023_diffs']>0.01)|(df['norm_2024_diffs']>0.01)|(df['norm_2025_diffs']>0.01)|df['log_comp']==True]

print(df[['word', 'norm_2021', 'norm_2022', 'norm_2023_predicted', 'norm_2023', 'norm_2024_predicted', 'norm_2024', 'norm_2025_predicted', 'norm_2025', 
          'norm_2023_diffs', 'norm_2023_ratios', 'norm_2024_diffs', 'norm_2024_ratios', 'norm_2025_diffs', 'norm_2025_ratios']].loc
      [(df['norm_2023'] > df['norm_2023_predicted'])&(df['norm_2024'] > df['norm_2024_predicted'])&(df['norm_2025'] > df['norm_2025_predicted'])]
      .sort_values(by='norm_2025_ratios', ascending=False))

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

# chatgpt was released in late 2022 - let's check if there are words where z_2023 is higher than in previous years
# also z-scores for previous years are not missing
# -> means commented off, unnecessary so far
years_antegpt = [col for col in z_score_comp_df.columns if re.search(r'\d', col) is not None and int(re.search(r'\d+', col)[0]) <= helpers.CHATGPT_RELEASE_YEAR]
years_postgpt = [col for col in z_score_comp_df.columns if re.search(r'\d', col) is not None and int(re.search(r'\d+', col)[0]) > helpers.CHATGPT_RELEASE_YEAR]
#z_score_comp_df['z_mean_larger_post_release'] = z_score_comp_df.apply(lambda x: True if x[years_postgpt].mean() > x[years_antegpt].mean() else False, axis=1)

years_antegpt = [col for col in frequency_comp_df.columns if re.search(r'\d', col) is not None and int(re.search(r'\d+', col)[0]) <= helpers.CHATGPT_RELEASE_YEAR]
years_postgpt = [col for col in frequency_comp_df.columns if re.search(r'\d', col) is not None and int(re.search(r'\d+', col)[0]) > helpers.CHATGPT_RELEASE_YEAR]
#frequency_comp_df['n_mean_larger_post_release'] = frequency_comp_df.apply(lambda x: True if x[years_postgpt].mean() > x[years_antegpt].mean() else False, axis=1)
