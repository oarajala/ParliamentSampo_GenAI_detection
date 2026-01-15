import pandas as pd
import requests
import socket
import re
import os
import time
from scipy import stats
from scipy import interpolate
#from wordcloud import WordCloud
#import matplotlib.pyplot as plt
from utils import helpers

# test run
directory = helpers.get_parent_directory()

csv_files_to_use_list = [i for i in os.listdir(f'{directory}/csv_lemmatized') if re.match(r'speeches_\d+\.csv', i) is not None]

year, max_year = int(min(re.findall(r'\d+', ' '.join(csv_files_to_use_list)))), int(max(re.findall(r'\d+', ' '.join(csv_files_to_use_list))))

# ### HOX HOX HOX
# ### HARD CODING FOR TEST
#year = 2025
#max_year = 2025

while year <= max_year:

    print(f'year: {year}')

    # read the year's contents from a csv
    year_csv = pd.read_csv(f'{directory}/csv_lemmatized/speeches_{year}.csv', sep=',', header=0)

    # calculate the progression of the electoral term
    #year_csv['electoral_term_progression'] = year_csv.apply(lambda x: helpers.calculate_electoral_term_progression(x['date'], x['electoral_term']), axis=1)

    # fetch individual words from speeches (column 'content')
    #year_csv['words'] = year_csv.apply(lambda x: helpers.extract_words(x['content_lemmatized']), axis=1)

    # fetch individual sentences from speeches (column 'content')
    #year_csv['sentences'] = year_csv.apply(lambda x: helpers.extract_sentences(x['content_lemmatized']), axis=1)

    # calculate the appearances/frequencies of individual words, store from dict -> df
    word_frequency_dict = {}
    for index, row in year_csv.iterrows():
        if type(row.content_lemmatized) != str:
            pass
        else:
            tmp_dict = helpers.count_word_freqs_in_string(row.content_lemmatized)
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
word_frequency_combined_df = pd.DataFrame(columns=['year', 'word', 'n', 'z_per_year']).astype({'year': int, 'word': str, 'n': int, 'z_per_year': float})

for csv in [i for i in os.listdir(f'{directory}/csv_analysis/') if 'word_frequency_per_year' in i]:
    df = pd.read_csv(f'{directory}/csv_analysis/{csv}', sep=';', encoding='utf-8', header=0)

    # calculate z-score for each word
    # -> THIS WILL BE CALCULATED FOR YEARLY DATA, NOT OVER THE COMBINED DATASET!
    df['z_per_year'] = None
    ser = pd.Series(df['n'])
    z_scores = pd.Series(stats.zscore(ser))
    df['z_per_year'] = z_scores

    word_frequency_combined_df = pd.concat([word_frequency_combined_df, df], axis=0, ignore_index=True)

# Now that we have the z-score per every word per every year, let's pivot the data for readability and availability for analysis.
# We want a wide df instead of long: for every row (axis=0) we have the word and its z-score per year; therefore columns: word and years.
# Let's also process frequencies.
z_score_comp_df = word_frequency_combined_df.pivot_table(values='z_per_year', index='word', columns=['year']).rename_axis(columns=None)
frequency_comp_df = word_frequency_combined_df.pivot_table(values='n', index='word', columns=['year']).rename_axis(columns=None)
# Prep the df for saving for futher analysis:
# - add 'word' as a column instead of index
# - rename year columns 'YYYY' -> 'z_YYYY'
z_score_comp_df['word'] = z_score_comp_df.index
z_score_comp_df.reset_index(drop=True, inplace=True)
z_score_comp_df.rename(columns={k : f'z_{k}' for k in z_score_comp_df.columns if str(k)!='word'}, inplace=True)
z_score_comp_df.sort_index(axis=1, inplace=True)

frequency_comp_df['word'] = frequency_comp_df.index
frequency_comp_df.reset_index(drop=True, inplace=True)
frequency_comp_df.rename(columns={k : f'n_{k}' for k in frequency_comp_df.columns if str(k)!='word'}, inplace=True)
frequency_comp_df.sort_index(axis=1, inplace=True)

# skew test: can checking the skew make finding interesting words easier?
input_cols = [col for col in z_score_comp_df.columns if re.search(r'\d', col) is not None]
z_score_comp_df['z_score_skew'] = z_score_comp_df[input_cols].apply(lambda x: stats.skewtest(a=x, nan_policy='omit')[0], axis=1)
input_cols = [col for col in frequency_comp_df.columns if re.search(r'\d', col) is not None]
frequency_comp_df['n_skew'] = frequency_comp_df[input_cols].apply(lambda x: stats.skewtest(a=x, nan_policy='omit')[0], axis=1)
# chatgpt was released in late 2022 - let's check if there are words where z_2023 is higher than in previous years
# also z-scores for previous years are not missing
years_antegpt = [col for col in z_score_comp_df.columns if re.search(r'\d', col) is not None and int(re.search(r'\d+', col)[0]) <= helpers.CHATGPT_RELEASE_YEAR]
years_postgpt = [col for col in z_score_comp_df.columns if re.search(r'\d', col) is not None and int(re.search(r'\d+', col)[0]) > helpers.CHATGPT_RELEASE_YEAR]
z_score_comp_df['z_mean_larger_post_release'] = z_score_comp_df.apply(lambda x: True if x[years_postgpt].mean() > x[years_antegpt].mean() else False, axis=1)

years_antegpt = [col for col in frequency_comp_df.columns if re.search(r'\d', col) is not None and int(re.search(r'\d+', col)[0]) <= helpers.CHATGPT_RELEASE_YEAR]
years_postgpt = [col for col in frequency_comp_df.columns if re.search(r'\d', col) is not None and int(re.search(r'\d+', col)[0]) > helpers.CHATGPT_RELEASE_YEAR]
frequency_comp_df['n_mean_larger_post_release'] = frequency_comp_df.apply(lambda x: True if x[years_postgpt].mean() > x[years_antegpt].mean() else False, axis=1)
# checkpoint save
save_file_name = 'word_z_score_all_years.csv'
if save_file_name in os.listdir(f'{directory}/csv_analysis/'):
    os.remove(f'{directory}/csv_analysis/{save_file_name}')
z_score_comp_df.to_csv(f'{directory}/csv_analysis/{save_file_name}', sep=';', header=True, index=False, encoding='utf-8')

save_file_name = 'word_frequency_all_years.csv'
if save_file_name in os.listdir(f'{directory}/csv_analysis/'):
    os.remove(f'{directory}/csv_analysis/{save_file_name}')
frequency_comp_df.to_csv(f'{directory}/csv_analysis/{save_file_name}', sep=';', header=True, index=False, encoding='utf-8')

# first batch of analysis - trying to recognise significant changes after the release of genAI tools

def linear_extrapolation(y: list, x: list, n=1) -> list:
    #m = (y2 – y1) / (x2 – x1)
    #y = y1 + m · (x – x1)
    # x and y must be arrays of same length
    if len(y) != len(x):
        print('array length mismatch')
        return None
    else:
        # format helper parameters to not modify lists outside the function
        xx = [*[i for i in x]]
        yy = [*[i for i in y]]
        return_list = [] # format list to be returned
        # loop n times -> return list of n length with n extrapolations
        # note: extrapolating on extrapolations if n>1
        while n >= 1:
            # format x: it shall take a running sequence of numbers as its values
            xx = [i for i in range(len(xx))]
            m = (yy[-1] - yy[-2]) / (xx[-1] - xx[-2])
            y_v = yy[-2] + m * ((xx[-1] + 1) - xx[-2])
            xx.append([xx[-1]+1])
            yy.append(y_v)
            return_list.append(y_v)
            n = n-1
        return return_list
    
freq = pd.read_csv(f'{directory}/csv_analysis/word_frequency_all_years.csv', sep=';', encoding='utf-8')

years_antegpt = [col for col in freq.columns if re.search(r'\d', col) is not None and int(re.search(r'\d+', col)[0]) <= helpers.CHATGPT_RELEASE_YEAR]
ver = freq[years_antegpt].iloc[5].values.tolist() # 15429

print(years_antegpt)
print(ver)
kek = linear_extrapolation(ver, years_antegpt, n=1)
print(kek)
print(years_antegpt[-1]+1)
print([i for i in range(len(years_antegpt))])   
range([i for i in years_antegpt])
[*[i for i in years_antegpt]]
# # #
# # #
# # #
# chatgpt was released in late 2022 - let's check if there are words where z_2023 is higher than in previous years
# also z-scores for previous years are not missing
years_antegpt = [col for col in z_score_comp_analysis_df.columns if re.search(r'\d', col) is not None and int(re.search(r'\d+', col)[0]) <= helpers.CHATGPT_RELEASE_YEAR]
years_postgpt = [col for col in z_score_comp_analysis_df.columns if re.search(r'\d', col) is not None and int(re.search(r'\d+', col)[0]) > helpers.CHATGPT_RELEASE_YEAR]
z_score_comp_analysis_df['z_mean_larger_post_release'] = z_score_comp_analysis_df.apply(lambda x: True if x[years_postgpt].mean() > x[years_antegpt].mean() else False, axis=1)

z_score_comp_analysis_df.loc[z_score_comp_analysis_df['z_sig_larger'] == True]

print(z_score_comp_df.loc[z_score_comp_df['word']=='&'])
print(word_frequency_combined_df.loc[word_frequency_combined_df['word']=='ravi'])

print(word_frequency_combined_df.loc[word_frequency_combined_df['year'].isin([2010])].pivot(columns='year', index='word', values='z_per_year'))
print(word_frequency_combined_df.loc[word_frequency_combined_df['year'].isin([2010, 2011, 2012, 2013])].pivot_table(values='z_per_year', index='word', columns=['year']))
print(word_frequency_combined_df.pivot_table(values='z_per_year', index='word', columns='year').rename(columns=['word', *[f'z_{y}' for y in word_frequency_combined_df['year'].unique()]]))
testdf = word_frequency_combined_df.pivot_table(values='z_per_year', index='word', columns='year').rename_axis(columns=None)
testdf['word'] = testdf.index
testdf.reset_index(drop=True, inplace=True)
testdf.rename(columns={k : f'z_{k}' for k in testdf.columns if str(k)!='word'}, inplace=True)
print(testdf.sort_index(axis=1))

#testdf['word'] = testdf.index
#testdf = testdf[['word', *[y for y in word_frequency_combined_df['year'].unique()]]].reset_index(drop=True)
#testdf.columns
# ###
# let's build a df for the words in combined df's 2025 words and their z-scores per year
# --> second try to speed things up
# 1) create an empty df, dynamically create columns to match the number of years to be processed (based on the files processed above)
z_score_comp_df = pd.DataFrame(columns=['word', *[f'z_{y}' for y in word_frequency_combined_df['year'].unique()]])
# 2) set data types
z_score_comp_df = z_score_comp_df.astype({k : str if k=='word' else float for k in z_score_comp_df.columns}, copy=False)
errors = 0
error_words = []
for word in [word for word in word_frequency_combined_df['word'].unique()]:
    try:
        word_df = word_frequency_combined_df.loc[word_frequency_combined_df['word'] == word]
        values_list = [word, *helpers.list_z_score_per_df_year(word_df, z_score_comp_df.columns)]
        z_score_comp_df = pd.concat([z_score_comp_df, pd.DataFrame(data=[values_list], columns=z_score_comp_df.columns).astype(z_score_comp_df.dtypes)], 
                                axis=0, ignore_index=True)
    except Exception as e:
        errors = errors+1
        error_words.append(word)
        pass
# ###

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

# Analysis limited to time where lemmatized texts are available.

directory = helpers.get_parent_directory()

asd = pd.read_csv(directory+'/csv_lemmatized/speeches_2024.csv', sep=',', header=0)

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

asd['words'] = asd.apply(lambda x: helpers.extract_words(x['content']), axis=1)

print(asd[['content', 'words']])

asd['sentences'] = asd.apply(lambda x: helpers.extract_sentences(x['content']), axis=1)

print(asd[['content', 'sentences']])

for i in asd['words'][:10]:
    print(i)
