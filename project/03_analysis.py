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

import pyvoikko

s = 'Arvoisa puhemies! Tämä ”tiedustelukulttuuri” tässä vilahtelee. Ja kun aihe kiinnostaa kollegoita, niin hieman taustaa. En ole teemaa tai sanaa itse keksinyt. Se on asiaa paremmin tuntevien käyttöön ottama, mutta olen itse sitä ruvennut valiokunnassa käyttämään ja eduskunnassa käyttämään, koska minun mielestäni se on hyvä sana, joka kuvaa lainsäädäntöä, luottamusta, viranomaistoimintaa ja kaikkea sitä, mikä tähän kuuluu. Jos — niin kuin tiedän — esimerkiksi edustaja Kiljunen on kiinnostunut kirjallisuudesta tutkijana, niin teoksen nimi on ”Suomalaisen tiedustelukulttuurin jäljillä”, ja se on Maanpuolustuskorkeakoulun julkaisu vuodelta 2020, toimittanut Tommi Koivula, sotataidon laitos. Julkaisu on ladattavissa myös verkosta, ja eduskunnan kirjasto auttaa tarvittaessa erinomaisella tavalla, jos joku haluaa. Olen kirjan lukenut, ja itselleni se oli kyllä hyvin antoisa teos, joka antoi syvyyttä tällaiselle siviilille, poliitikolle, joka sitten mielellään kuulee ja lukee asiantuntijoiden näkemyksiä asioista. Sieltä kumpuaa tämä ”tiedustelukulttuuri”‑sana. [Kimmo Kiljunen: Kiitos vihjeestä!]'
ss = s.split()

dd = {}
for i in ss:
    i = helpers.clean_string(i)
    if i not in dd.keys():
        a = pyvoikko.analyse(i)
        if (a is not None) and (len(a)>0) and (a[0].CLASS != 'etunimi'):
            dd[i] = a[0].BASEFORM
    #oo = pyvoikko.analyse(i)
    
for k, v in dd.items():
    print(k, v)

dd = {}
for i in ss:
    i = helpers.clean_string(i)
    print(i)
    print(pyvoikko.analyse(i))
    if i not in dd.keys():
        a = pyvoikko.analyse(i)
        if a is not None:
            dd[i] = pyvoikko.analyse(i)[0]
    #oo = pyvoikko.analyse(i)

type(pyvoikko.analyse('kissaa'))

for k, v in dd.items():
    print(k, ': ', v)

l = []
for file in os.listdir(f'{directory}/csv_rawdata/'):
    if '.csv' in file:
        p = f'{directory}/csv_rawdata/{file}'
        try:
            f = pd.read_csv(p, sep=',', encoding='utf-8')
        except:
            f = pd.read_csv(p, sep=';', encoding='utf-8')    
        finally:
             print(f'{file}: {f.shape[0]}')  
             l.append(f.shape[0])

print(np.mean(l))

# read csv for analysis from csv_analysis directory
freq = pd.read_csv(f'{directory}/csv_analysis/word_frequency_all_years.csv', sep=';', encoding='utf-8')

# note: small peeks into the set at this point

# np.log10(ratios[ind]) > np.log10(2) - (np.log10(x[ind]) + 4) * (np.log10(2) / 4):
# calculate log10(r)>(log10(2)/4)*(log10(p)) (r=ratios year Y, p=frequency year Y) for more tools to find excess words (courtesy of Kobak D. et al (2025))
# -> select years for which to calculate
years = set([re.search(r'\d+', col)[0] for col in df.columns if re.search(r'norm_\d+', col) is not None])
years = ['2023','2024','2025']
for y in years:
    df[f'log10_r_{y}'] = df[f'norm_{y}_ratios'].apply(np.log10)
    df[f'coef_log10_p_{y}'] = df.apply(lambda x: (np.log10(2)/4)*np.log10(x[f'norm_{y}']), axis=1)

df.loc[((df['norm_2023_diffs']>0.01) | (df['log10_r_2023'] > df['coef_log10_p_2023'])==True) & 
       ((df['norm_2024_diffs']>0.01) | (df['log10_r_2024'] > df['coef_log10_p_2024'])==True) &
       ((df['norm_2025_diffs']>0.01) | (df['log10_r_2025'] > df['coef_log10_p_2025'])==True)]

save_file_name = 'analysis_first_peek.csv'
if save_file_name in os.listdir(f'{directory}/csv_analysis/'):
    os.remove(f'{directory}/csv_analysis/{save_file_name}')
df.to_csv(f'{directory}/csv_analysis/{save_file_name}', sep=';', header=True, index=False, encoding='utf-8')

# unique words per year
df = freq

print(f'words 2022: {len(df[df['norm_2022'].notna()==True])}')
print(f'words 2023: {len(df[df['norm_2023'].notna()==True])}')
print(f'words 2024: {len(df[df['norm_2024'].notna()==True])}')
print(f'words 2025: {len(df[df['norm_2025'].notna()==True])}')

print(f'words 2020: {len(df[df['norm_2020'].notna()==True])}')
print(f'words 2019: {len(df[df['norm_2019'].notna()==True])}')
print(f'words 2018: {len(df[df['norm_2018'].notna()==True])}')
print(f'words 2017: {len(df[df['norm_2017'].notna()==True])}')

for i in range(2015, 2026):
    c = f'norm_{i}'
    l = len(df[df[c].notna()==True])
    print(f'words {i}: {l}')

# what words appeared only after 2022/2023
words_2021 = df['word'].loc[(df['norm_2021'].notna()==True)&(df['norm_2021']>0.0)].tolist()
words_2022 = df['word'].loc[(df['norm_2022'].notna()==True)&(df['norm_2022']>0.0)].tolist()
words_2023 = df['word'].loc[(df['norm_2023'].notna()==True)&(df['norm_2023']>0.0)].tolist()
words_2024 = df['word'].loc[(df['norm_2024'].notna()==True)&(df['norm_2024']>0.0)].tolist()
words_2025 = df['word'].loc[(df['norm_2025'].notna()==True)&(df['norm_2025']>0.0)].tolist()

words_2023_excl_2022 = list(set(words_2023).difference(set(words_2022)))
words_2024_excl_2022 = list(set(words_2024).difference(set(words_2022)))
words_2025_excl_2022 = list(set(words_2025).difference(set(words_2022)))

len(words_2023_excl_2022)
len(words_2024_excl_2022)
len(words_2025_excl_2022)

t_intersect= list(set(words_2024_excl_2022).intersection(set(words_2025_excl_2022)))
print(t_intersect)

df[['word', 'n_2022']].loc[df['word']=='pahnanpohjimmainen']

# what words became more frequent after 2022/2023

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
