import pandas as pd
import requests
import socket
import re
import os
import time
from scipy import stats
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

for i in asd['words'][:10]:
    print(i)

# test run

directory = helpers.get_parent_directory()

csv_files_to_use_list = [i for i in os.listdir(f'{directory}/csv_lemmatization_added') if re.match(r'speeches_\d+\.csv', i) is not None]

year, max_year = int(min(re.findall(r'\d+', ' '.join(csv_files_to_use_list)))), int(max(re.findall(r'\d+', ' '.join(csv_files_to_use_list))))

# ### HOX HOX HOX
# ### HARD CODING FOR TEST
#year = 2010
#max_year = 2012

while year <= max_year:

    print(f'year: {year}')

    # read the year's contents from a csv
    year_csv = pd.read_csv(f'{directory}/csv_lemmatization_added/speeches_{year}.csv', sep=',', header=0)

    # calculate the progression of the electoral term
    year_csv['electoral_term_progression'] = year_csv.apply(lambda x: helpers.calculate_electoral_term_progression(x['date'], x['electoral_term']), axis=1)

    # fetch individual words from speeches (column 'content')
    year_csv['words'] = year_csv.apply(lambda x: langtools.extract_words(x['content']), axis=1)

    # fetch individual sentences from speeches (column 'content')
    year_csv['sentences'] = year_csv.apply(lambda x: langtools.extract_sentences(x['content']), axis=1)

    # calculate the appearances/frequencies of individual words, store from dict -> df
    word_frequency_dict = {}
    for index, row in year_csv.iterrows():
        tmp_dict = langtools.count_word_freqs_in_string(row.words)
        for k, v in tmp_dict.items():
            if k not in word_frequency_dict.keys():
                word_frequency_dict[k] = v
            else:
                word_frequency_dict[k] += v

    # set a df for storing info and saving it for later
    word_frequecy_per_year_df = pd.DataFrame(columns=['year', 'word', 'n'])

    # populate the df
    for k, v in word_frequency_dict.items():
        word_frequecy_per_year_df.loc[len(word_frequecy_per_year_df)] = {'year': year, 'word': k, 'n': v}

    # save the year's word freqs as a csv ("checkpoint save")
    save_file_name = f'word_frequency_per_year_{year}.csv'

    if save_file_name in os.listdir(f'{directory}/csv_analysis/'):
        os.remove(f'{directory}/csv_analysis/{save_file_name}')
    word_frequecy_per_year_df.to_csv(f'{directory}/csv_analysis/{save_file_name}', sep=';', header=True, index=False, encoding='utf-8')

    year = year+1

# read file(s) from /csv_analysis -> combine them into one df: word_frequency_combined_df
word_frequency_combined_df = pd.DataFrame(columns=['year', 'word', 'n', 'z_per_year'])

for csv in os.listdir(f'{directory}/csv_analysis/'):
    df = pd.read_csv(f'{directory}/csv_analysis/{csv}', sep=';', encoding='utf-8', header=0)

    # calculate z-score for each word
    # -> THIS WILL BE CALCULATED FOR YEARLY DATA, NOT OVER THE COMBINED DATASET!
    df['z_per_year'] = None
    ser = pd.Series(df['n'])
    z_scores = pd.Series(stats.zscore(ser))
    df['z_per_year'] = z_scores

    word_frequency_combined_df = pd.concat([word_frequency_combined_df, df], axis=0, ignore_index=True)

# let's build a df for the words in combined df's 2025 words and their z-scores per year
comparison_df = pd.DataFrame(columns=['word', *[f'z_{y}' for y in word_frequency_combined_df['year'].unique()]])

for i, d in word_frequency_combined_df.iterrows():
    if d.word not in comparison_df['word']:
        comparison_df.loc[len(comparison_df), 'word'] = d.word
        col_val = f'z_{d.year}'
        comparison_df.loc[comparison_df['word'] == d.word, col_val] = d.z_per_year
    else:
        col_val = f'z_{d.year}'
        comparison_df.loc[comparison_df['word'] == d.word, col_val] = d.z_per_year

print(comparison_df)

# # #
# # #
# # #

df = pd.read_csv(f'{directory}/csv_analysis/word_frequcy_per_year_2010.csv', sep=';', encoding='utf-8', header=0)

df['z_per_year'] = float()
df['n'].apply(stats.zscore, axis=0)

ser = pd.Series(df['n'])
print(ser)

ser2 = pd.Series(stats.zscore(ser))
print(ser2)
df['z_per_year'] = ser2
print(df)

print(year_csv[['topic', 'content']].loc[year_csv['electoral_term'].isna() == True])
year_csv['electoral_term_progression'] = year_csv.apply(lambda x: helpers.calculate_electoral_term_progression(x['date'], x['electoral_term']), axis=1)

print(year_csv['electoral_term'].loc[year_csv['electoral_term'].isna() == True])
print(year_csv['electoral_term'].unique())
'2011-04-20-2015-04-21'[:10]

#print(word_frequency_dict)
#print(word_frequecy_per_year_df[['word', 'n']])
#print(pd.DataFrame.from_dict(data=word_frequency_dict, columns=['n'], orient='index'))