#
## THIS IS TO CREATE FILES FOR ANALYSIS
## Files created in this script include files from /csv_lemmatized folder
## Files will be handled so that before their harder processing rows will be filtered by speech_type:
## > keep categories where preparation is necessary: 'Esittelypuheenvuoro', 'Ryhmäpuheenvuoro', 'Varsinainen puheenvuoro', 'Puheenvuoro'
## > Therefore: lemmatised content will be used.

import pandas as pd
import numpy as np
import re
import os
from scipy import stats
from utils import helpers
import pyvoikko
directory = helpers.get_parent_directory()

csv_files_to_use_list = [i for i in os.listdir(f'{directory}/csv_lemmatized') if re.match(r'speeches_\d+\.csv', i) is not None]

year, max_year = int(min(re.findall(r'\d+', ' '.join(csv_files_to_use_list)))), int(max(re.findall(r'\d+', ' '.join(csv_files_to_use_list))))

CHATGPT_RELEASE_YEAR = int(2022)
FINNISH_ALPHABET = 'abcdefghijklmnopqrstuvwxyzåäö'

WANTED_SPEECH_TYPES = ['Esittelypuheenvuoro', 'Ryhmäpuheenvuoro', 'Varsinainen puheenvuoro', 'Puheenvuoro']

# clean up 'speech_type' values: hard coded cleaning
def clean_speech_type(speech_type: str) -> str:
    if 'vastauspuheenvuoro' in speech_type:
        return 'Vastauspuheenvuoro'
    elif 'esittelypuheenvuoro' in speech_type:
        return 'Esittelypuheenvuoro'
    else:
        return speech_type.strip()

# Retrieve distinct WORDS from lemmatized speeches per each raw data csv year. Process each years csv_lemmatized/*.csv separately.
# Count frequency for each individual word per year, combine them in a dictionary and build a dataframe for all years. The df is later
# pivoted into wide format.
# Each enriched csv_lemmatized/*.csv is first read, individual words from 'content_lemmatized' column sent for individual word extraction,
# the words are then counted (end up with a dictionary where key=word and value=n). The dict is then saved as a df and as a csv.
# These csvs are again later read and combined into one, wide, pivoted csv.
while year <= max_year:
    # save the year's word freqs as a csv ("checkpoint save")
    save_file_name = f'word_frequency_per_year_{year}_filtered.csv'
    # if the file already exists -> skip the year
    # -> if you want to remake the data for the year Y, delete the file and run the script
    if save_file_name in os.listdir(f'{directory}/csv_analysis/filtered/'):
        pass
    else:
        # read the year's contents from a csv
        year_csv = pd.read_csv(f'{directory}/csv_lemmatized/speeches_{year}.csv', sep=';', header=0)
        # keep only rows where speech_type is in WANTED_SPEECH_TYPES list
        year_csv.loc[:, 'speech_type'] = year_csv['speech_type'].apply(clean_speech_type)
        year_csv = year_csv[year_csv['speech_type'].isin(WANTED_SPEECH_TYPES)]
        # calculate the appearances/frequencies of individual words, store from dict -> df
        word_frequency_dict = {}
        for index, row in year_csv.iterrows():
            if type(row.content_lemmatized) != str:
                pass
            else:
                string_cleaned = ' '.join([helpers.clean_string(i) for i in row.content_lemmatized.split()])
                tmp_dict = helpers.count_word_freqs_in_string(string_cleaned)
                for k, v in tmp_dict.items():
                    if k not in word_frequency_dict.keys():
                        word_frequency_dict[k] = v
                    else:
                        word_frequency_dict[k] += v
        # set a df for storing info and saving it for later
        word_frequecy_per_year_df = pd.DataFrame(columns=['year', 'word', 'n']).astype({'year': int, 'word': str, 'n': int})
        # populate the df
        for k, v in word_frequency_dict.items():
            word_frequecy_per_year_df = pd.concat([word_frequecy_per_year_df, pd.DataFrame.from_dict(data={'year': [year], 'word': [k], 'n': [v]}, orient='columns')], axis=0, ignore_index=True)
        # remove empty '' words from the dataset before saving as csv
        word_frequecy_per_year_df = word_frequecy_per_year_df[word_frequecy_per_year_df['word'].str.len() > 0]
        # save the file
        if save_file_name in os.listdir(f'{directory}/csv_analysis/filtered/'):
            os.remove(f'{directory}/csv_analysis/{save_file_name}')
        word_frequecy_per_year_df.to_csv(f'{directory}/csv_analysis/filtered/{save_file_name}', sep=';', header=True, index=False, encoding='utf-8')
    year = year+1

# read file(s) from /csv_analysis -> combine them into one df: word_frequency_combined_df
word_frequency_combined_df = pd.DataFrame(columns=['year', 'word', 'n', 'z_per_year']).astype({'year': int, 'word': str, 'n': int, 'z_per_year': float})

for csv in [i for i in os.listdir(f'{directory}/csv_analysis/filtered/') if 'word_frequency_per_year' in i]:
    df = pd.read_csv(f'{directory}/csv_analysis/filtered/{csv}', sep=';', encoding='utf-8', header=0)

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

# normalise the data: min-max normalisation for n_YYYY columns
# -> store normalised values in norm_YYYY columns
input_cols = [col for col in frequency_comp_df.columns if re.search(r'n_\d+$', col) is not None]
for col in input_cols:
    col_max = frequency_comp_df[col].max(skipna=True)
    col_min = frequency_comp_df[col].min(skipna=True)
    new_col = f'norm_{re.search(r'[0-9]+', col)[0]}'
    frequency_comp_df[new_col] = None
    frequency_comp_df[new_col] = frequency_comp_df.apply(lambda x: None if type(x) != float is None else (x[col]-col_min)/(col_max-col_min), axis=1)

# identify significant changes after the release of genAI tools
# list of year columns in df before release of chatgpt
# LINEAR EXTRAPOLATION IS RUN ON NORMALISED VALUES IN NORM_YYYY COLUMNS, NOT THE N_YYYY VALUES
years_antegpt = [col for col in frequency_comp_df.columns if re.search(r'norm_\d+', col) is not None and int(re.search(r'\d+', col)[0]) <= helpers.CHATGPT_RELEASE_YEAR]
# 2023 prediction based on years before chatgpt
frequency_comp_df['norm_2023_predicted'] = frequency_comp_df.apply(lambda x: helpers.linear_extrapolation(y=x[years_antegpt].values.tolist(), x=years_antegpt, n=1)[0], axis=1)
frequency_comp_df['norm_2023_diffs'] = frequency_comp_df.apply(lambda x: x['norm_2023'] - x['norm_2023_predicted'], axis=1)
frequency_comp_df['norm_2023_ratios'] = frequency_comp_df.apply(lambda x: x['norm_2023'] / (1 if (x['norm_2023_predicted'] is None or x['norm_2023_predicted']==np.float64(0)) else x['norm_2023_predicted']), axis=1)
# 2024 prediction based on years before chatgpt
frequency_comp_df['norm_2024_predicted'] = frequency_comp_df.apply(lambda x: helpers.linear_extrapolation(y=x[years_antegpt].values.tolist(), x=years_antegpt, n=1)[0], axis=1)
frequency_comp_df['norm_2024_diffs'] = frequency_comp_df.apply(lambda x: x['norm_2024'] - x['norm_2024_predicted'], axis=1)
frequency_comp_df['norm_2024_ratios'] = frequency_comp_df.apply(lambda x: x['norm_2024'] / (1 if (x['norm_2024_predicted'] is None or x['norm_2024_predicted']==np.float64(0)) else x['norm_2024_predicted']), axis=1)
# 2025 prediction based on years before chatgpt
frequency_comp_df['norm_2025_predicted'] = frequency_comp_df.apply(lambda x: helpers.linear_extrapolation(y=x[years_antegpt].values.tolist(), x=years_antegpt, n=1)[0], axis=1)
frequency_comp_df['norm_2025_diffs'] = frequency_comp_df.apply(lambda x: x['norm_2025'] - x['norm_2025_predicted'], axis=1)
frequency_comp_df['norm_2025_ratios'] = frequency_comp_df.apply(lambda x: x['norm_2025'] / (1 if (x['norm_2025_predicted'] is None or x['norm_2025_predicted']==np.float64(0)) else x['norm_2025_predicted']), axis=1)

# save files for analysis
save_file_name = 'word_z_score_all_years.csv'
if save_file_name in os.listdir(f'{directory}/csv_analysis/filtered/'):
    os.remove(f'{directory}/csv_analysis/filtered/{save_file_name}')
z_score_comp_df.to_csv(f'{directory}/csv_analysis/filtered/{save_file_name}', sep=';', header=True, index=False, encoding='utf-8')

save_file_name = 'word_frequency_all_years.csv'
if save_file_name in os.listdir(f'{directory}/csv_analysis/filtered/'):
    os.remove(f'{directory}/csv_analysis/filtered/{save_file_name}')
frequency_comp_df.to_csv(f'{directory}/csv_analysis/filtered/{save_file_name}', sep=';', header=True, index=False, encoding='utf-8')

# prep speaker and speech specific data for analysis

# declare functions for this operation
def clean_string(string: str) -> str:
    try:
        # remove blanks in start and end
        string = string.strip()
        string = string.lower()
        # the string must contain characters
        if any(c in string for c in FINNISH_ALPHABET)==False:
            string = ''
        # remove tabulations, line breaks etc., also special characters
        remove_these = r'[\+\*!"”’?.:,…()§\'[\] \t\n\r\f\v]'
        string = re.sub(remove_these, '', string)
        # remove weird parentheses and backwards linebreaks from starts of strings
        string = re.sub(r'^\)\\[a-z]', '', string)
        # remove weird '\[alphabet]' strings at start of strings
        string = re.sub(r'^\\[a-z]', '', string)
        # remove numbers
        string = re.sub(r'[0-9]', '', string)
        # remove dashes '-' at the start and end of string
        string = re.sub(r'^-|-$', '', string)
        # remove individual forward and backward slashes '/', '\'
        string = re.sub(r'[\/\\]', '', string)
        # remove double dashes '--'
        string = string.replace('--', '-')
        # remove the equal sign '='
        string = string.replace('=', '')
        # at the end of the cleaning, remove all characters from the string which are not in the alphabet except for dash (compound words)
        remove_these = ''.join([str(c) for c in string if c != '-' and c not in [i for i in FINNISH_ALPHABET]])
        string = re.sub(remove_these, '', string)
        # remove blanks in start and end again
        string = string.strip()
        # remove empty if string length < 2
        string = '' if len(string) < 2 else string
        return string
    except:
        print(f'Unexpected error at helpers.clean_string(), string: {string}')
        raise

def count_word_freqs_in_string(string: str):
    """Counts the words in the input string.
    Returns a dictionary where the word is the key and the frequency is the value.
    """
    if ((string is None) or (string == 'nan')):
        return None
    else:
        words_list = re.split(' ', string)
        wordfreq_dict = {}
        for word in words_list:
            if word not in wordfreq_dict.keys():
                wordfreq_dict[word] = 1
            else:
                wordfreq_dict[word] += 1

        return wordfreq_dict

def get_normalised(df: pd.DataFrame, speaker_id: str, year: int, word_n: int) -> float:
    w_min = df['word_n'].loc[(df['speaker_id']==speaker_id)&(df['year']==year)].min()
    w_max = df['word_n'].loc[(df['speaker_id']==speaker_id)&(df['year']==year)].max()
    return ((word_n-w_min)/(w_max-w_min))

def linear_extrapolation(y: list, x: list, n=1) -> list:
    """Linear extrapolation based on last two x and y observations. Returns the extrapolated value of y for a given x based on y1x1 and y2x2.
    Parameter x will be standardised to a running sequence of numbers so extrapolations works on a linear scale.
    Args:
        y (list): list of values
        x (list): list of values
        n (int, optional): for how many times shall extrapolation be done. Defaults to 1. Larger values will start extrapolating on extrapolated values.

    Returns:
        list: extrapolated value(s) of y. The length of the list will be n.
    """
    # x and y must be arrays of same length
    # CHANGE THIS TO ASSERT
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
            # format xx: it shall take a running sequence of numbers as its values
            xx = [i for i in range(len(x))]
            m = (yy[-1] - yy[-2]) / (xx[-1] - xx[-2])
            y_v = yy[-2] + m * ((xx[-1] + 1) - xx[-2])
            xx.append([xx[-1]+1])
            yy.append(y_v)
            return_list.append(y_v)
            n = n-1
        return return_list

# create the data in loops: 
## > loop the csvs for years 2015-2025
## > extract each word per speaker per df (=year), this is done in a for loop
## > combine them all into dataframe df_speaker_words_year
# declare the years: 
## hard code year and max_year: 2015, 2025 respectively
## speaker_id is present in raw data from 2015!
year, max_year = 2015, 2025
# start looping the csvs
while year <= max_year:
    # name for saving the file
    save_file_name = f'speaker_words_{year}.csv'

    if save_file_name in os.listdir(f'{directory}/csv_analysis/filtered/'):
        pass
    else:
        # get the csv to match the year from directory: directory/csv_lemmatized/
        year_csv = pd.read_csv(f'{directory}/csv_lemmatized/speeches_{year}.csv', sep=';', header=0)
        # format a dataframe to store the results
        # > columns: speaker_id, year, word, word_n (how many times the word appears)
        df_speaker_words_year = pd.DataFrame(columns=['speaker_id', 'year', 'word', 'word_n']).astype({'speaker_id': str, 'year': int, 'word': str, 'word_n': int})    
        # extract each word per speaker per df (=year)
        for speaker in year_csv['speaker_id'].loc[(year_csv['speaker_id'].notna()==True)&(year_csv['speaker_id'].str.len()>0)].unique():
            # extract only rows for the speaker in iteration, and only if a lemmatized speech exists, and only if the lemmatized speech is longer than 0 chars
            df_filtered = year_csv.loc[(year_csv['speaker_id']==speaker)&(year_csv['content_lemmatized'].notna()==True)&(year_csv['content_lemmatized'].str.len()>0)]
            # extract each lemmatized speech; compile them into a single string
            speaker_all_speeches = ' '.join(df_filtered['content_lemmatized'])
            # string cleaning: clean special characters from the string
            speaker_all_speeches = ' '.join([clean_string(word) for word in speaker_all_speeches.split(' ')])
            # get the count of each word in the string, return a dict
            speaker_words_dict = count_word_freqs_in_string(speaker_all_speeches)
            # delete empty '' keys (words) from the dict, if such have made it there. these are failed lemmatizations
            try:
                del speaker_words_dict['']
            except KeyError:
                pass
            # add the speaker's subset (speaker_id, year, word, word_n) in the combination dataframe
            # > from the speaker_words_dict, and year, and speaker
            # > create another "temporary" dataframe for this, concatenate this to the df_speaker_words_year df
            concat_df = pd.DataFrame.from_dict(data=speaker_words_dict, orient='index', columns=['word_n'])
            concat_df['speaker_id'], concat_df['year'], concat_df['word'] = speaker, year, concat_df.index
            concat_df.reset_index(drop=True, inplace=True)
            concat_df = concat_df[['speaker_id','year','word','word_n']]  
            df_speaker_words_year = pd.concat([df_speaker_words_year, concat_df], axis=0, ignore_index=True)
        # store the data in a csv (savepoint!)
        # > directory and file name template: directory/csv_analysis/speaker_words_YYYY.csv
        df_speaker_words_year.to_csv(f'{directory}/csv_analysis/filtered/{save_file_name}', sep=';', header=True, index=False, encoding='utf-8')
        # time for the next year
    year = year+1

# data for words per speaker for years 2015-2025 has now been created
# next: pick the speakers who appear in all datasets
# > speakers who are present in all datasets 2015-2025
df_speaker_words_comp = pd.DataFrame(columns=['speaker_id', 'year', 'word', 'word_n', 'word_norm']).astype({'speaker_id':str, 'year':int, 'word':str, 'word_n':int, 'word_norm':float})
for f in [file for file in os.listdir(f'{directory}/csv_analysis/filtered/') if re.search(r'speaker_words_\d+\.csv', file)]:
    df = pd.read_csv(f'{directory}/csv_analysis/filtered/{f}', sep=';', header=0, encoding='utf-8', dtype={'speaker_id': str, 'year': int, 'word': str, 'word_n': int})
    # calculate the normalised frequency of word per speaker per year: min-max normalisation
    # store in column: word_norm
    # running this in one apply with subqueries into the dataframe causes setting with copy warnings and takes way too long due to relatively large row counts
    # > therefore let's do this step by step with fewer repetitive queries
    df['word_norm'] = None
    # loop through each speaker
    for speaker in df['speaker_id'].unique():
        # minimum and maximum word counts per speaker
        w_min, w_max = df['word_n'].loc[df['speaker_id']==speaker].min(), df['word_n'].loc[df['speaker_id']==speaker].max()
        # calculate the normalised frequency per each word of the speaker
        df.loc[df['speaker_id']==speaker, 'word_norm'] = df.apply(lambda x: (x['word_n']-w_min)/(w_max-w_min), axis=1)
    df_speaker_words_comp = pd.concat([df_speaker_words_comp, df], axis=0, ignore_index=True)

# save as csv
file_path_write = f'{directory}/csv_analysis/filtered/speaker_words_comp.csv'
try:
    df_speaker_words_comp.to_csv(file_path_write, sep=';', header=True, index=False, encoding='utf-8')
except FileExistsError:
    os.remove(file_path_write)
    df_speaker_words_comp.to_csv(file_path_write, sep=';', header=True, index=False, encoding='utf-8')

# compute extrapolated value for each speaker's each word:
# -> what would the extrapolated of the word be in 2023, 2024, 2025 based on the frequency in last preceeding years
df_speaker_words_comp = pd.read_csv(f'{directory}/csv_analysis/filtered/speaker_words_comp.csv',sep=';',header=0,encoding='utf-8',dtype={'speaker_id': str, 'year': int, 'word': str, 'word_n': int, 'word_norm':float})
# keep only records where the speaker_id is a valid identifier (string of numbers)
df_speaker_words_comp = df_speaker_words_comp.loc[df_speaker_words_comp['speaker_id'].str.contains(pat=r'\d+')==True]

# compute extrapolated values of word frequencies only for this range of years
loop_years = [2023, 2024, 2025]
for year in loop_years:
    # name for a new column: extrapolated word frequency
    # > a new column will be created for each looped year
    col_word_norm_extrap = f'word_norm_extrap_{year}'
    #df_speaker_words_comp[col_word_norm_extrap] = None
    # merging the dataframe will speed this up instead of looping each row
    # > create a new df to quickly compute the linear extrapolation for word frequency: df_merge
    # > df_merge is created by joining df_speaker_words_comp for year, said df year-1 and year-2 on speaker_id and word
    # > INNER JOIN filters rows where there are no normalised frequencies in the previous years -> extrapolation for these words would fail
    # > LEFT JOIN keeps all recrods - this can be done to keep the records 
    # > finally the extrapolated normalised frequency is updated into df_speaker_words_comp in the update
    df_merge = df_speaker_words_comp[['speaker_id','year','word','word_norm']].loc[df_speaker_words_comp['year']==year].merge(
                   df_speaker_words_comp[['speaker_id','year','word','word_norm']].loc[df_speaker_words_comp['year']==year-1],
                   how='left', on=['speaker_id', 'word'], suffixes=(None,'_t_1'))
    df_merge = df_merge.merge(df_speaker_words_comp[['speaker_id','year','word','word_norm']].loc[df_speaker_words_comp['year']==year-2],
        how='left', on=['speaker_id', 'word'], suffixes=(None,'_t_2'))
    df_merge[col_word_norm_extrap] = df_merge.apply(lambda x: linear_extrapolation(y=[x['word_norm_t_2'], x['word_norm_t_1']],x=[year-2, year-1],n=1)[0], axis=1)
    df_speaker_words_comp = df_speaker_words_comp.merge(df_merge[['speaker_id','word','year',col_word_norm_extrap]], how='left', on=['speaker_id','word','year'])

# collapse word_norm_extrap_[2023, 2024, 2025] into a single column, word_norm_extrap, since year is already a column in the df
df_speaker_words_comp.loc[df_speaker_words_comp['year']==2023, 'word_norm_extrap'] = df_speaker_words_comp['word_norm_extrap_2023'] 
df_speaker_words_comp.loc[df_speaker_words_comp['year']==2024, 'word_norm_extrap'] = df_speaker_words_comp['word_norm_extrap_2024'] 
df_speaker_words_comp.loc[df_speaker_words_comp['year']==2025, 'word_norm_extrap'] = df_speaker_words_comp['word_norm_extrap_2025']
# keep only columns speaker_id, year, word, word_n, word_norm, word_norm_extrap
df_speaker_words_comp = df_speaker_words_comp[['speaker_id','year','word','word_n','word_norm','word_norm_extrap']]

# compute differences and ratios between actual normalised frequencies and the extrapolated values:
# > diffs: actual value minus extrapolated value
# > ratios: actual value divided by extrapolated value
# >> replace None/NaN extrapolated value with 1 to avoid divide by zero errors
df_speaker_words_comp['word_diffs'] = df_speaker_words_comp.apply(lambda x: x['word_norm'] - x['word_norm_extrap'], axis=1)
df_speaker_words_comp['word_ratios'] = df_speaker_words_comp.apply(lambda x: x['word_norm'] / (1 if (x['word_norm_extrap'] is None or x['word_norm_extrap']==np.float64(0)) else x['word_norm_extrap']), axis=1)

# add word_class column before saving to csv - this takes a while so better to save after this
df_speaker_words_comp['word_class'] = df_speaker_words_comp.apply(lambda x: pyvoikko.analyse(x['word'])[0].CLASS if len(pyvoikko.analyse(x['word'])) != 0 else None, axis=1)

# checkpoint save
# save as csv
file_path_write = f'{directory}/csv_analysis/filtered/speaker_words_comp.csv'
try:
    df_speaker_words_comp.to_csv(file_path_write, sep=';', header=True, index=False, encoding='utf-8')
except FileExistsError:
    os.remove(file_path_write)
    df_speaker_words_comp.to_csv(file_path_write, sep=';', header=True, index=False, encoding='utf-8')

# check for cases where diffs and ratios are higher in 2024 and 2025 than normalised frequenccy in previous years
# -> compare df (filtered df) to df_comp (unfiltered, years 2015-2025)
# -> we are interested in differences in 2024 & 2025 that are larger than in all previous years
# --> this filters out topic-related words that surface for topical issues and probably go out of vogue very soon (spikes in certain years)
# ---> observe change over time, see if there actually is anything there
# --> hypothesis: we could be left with "filler words"
# - loop down from year 2025 to 2015, pick speakers and words exist in all years
df_filter = pd.DataFrame(columns=['speaker_id', 'year', 'word', 'word_n', 'word_norm', 'word_norm_extrap', 'word_diffs', 'word_ratios', 'word_class']).astype({'speaker_id':str,'year':int,'word':str,'word_n':int,'word_norm':float,'word_norm_extrap':float,'word_diffs':float,'word_ratios':float, 'word_class':str})
years = df_speaker_words_comp['year'].unique()

# df_merge WILL BE SAVED IN WIDE FORMAT!!!
df_merge = pd.DataFrame(columns=['speaker_id','word','word_n_2015','word_norm_2015','word_norm_extrap_2015','word_diffs_2015','word_ratios_2015']).astype({'speaker_id':str,'word':str,'word_n_2015':int,'word_norm_2015':float,'word_norm_extrap_2015':float,'word_diffs_2015':float,'word_ratios_2015':float})
# get the speaker's words that appear in all years (2015-2025)
for year in years:
   # format for the first year
   if year==2015:
      df_merge = df_speaker_words_comp[['speaker_id','word_class','word','word_n','word_norm','word_norm_extrap','word_diffs','word_ratios']].loc[df_speaker_words_comp['year']==year]
      df_merge.rename(columns={'speaker_id':'speaker_id','word_class':'word_class','word':'word','word_n':'word_n_2015','word_norm':'word_norm_2015','word_norm_extrap':'word_norm_extrap_2015','word_diffs':'word_diffs_2015','word_ratios':'word_ratios_2015'}, inplace=True)
   # pass for 2025, no need to run this   
   if year==2025:
      pass
   else:
      df_merge = df_merge.merge(df_speaker_words_comp.loc[df_speaker_words_comp['year']==year+1], on=['speaker_id','word','word_class'], how='left', suffixes=(f'_{year}',f'_{year+1}'))

# ADDING Z-SCORES FOR FURTHER COMPARSIONS
year, max_year = 2015, 2025
speakers = df_merge['speaker_id'].unique()
while year <= max_year:
    col_name = f'z_{year}'
    df_merge[col_name] = None
    tmp_ser = pd.Series(data=None, dtype=float)

    for speaker in speakers:
        ser = df_merge[f'word_norm_{year}'].loc[df_merge['speaker_id']==speaker]
        z_scores = pd.Series(stats.zscore(ser))
        tmp_ser = pd.concat([tmp_ser, z_scores], ignore_index=True)

    df_merge[col_name] = tmp_ser
    year=year+1

# df_merge WILL BE SAVED IN WIDE FORMAT!!!
df_merge.to_csv(f'{directory}/csv_analysis/filtered/speaker_words_comp_wide.csv', header=True, encoding='utf-8', sep=';', index=False)

# ######################################################################

# calculate the lengths of the speakers' speeches per year
# -> length of speech = number of words in speech
def calculate_speech_length(speech: str) -> int:
    # start processing only if the input value actually is a string
    if type(speech) == str:
        # clean each word in string
        speech = [clean_string(i) for i in speech.split(' ')]
        # return length of list: number of words in speech
        # -> check that the length of the word is over 0; clean_string returns '' for removed characters, such as '!'
        return len([i for i in speech if len(i)>0])
    else:
        return None

# get the speeches, combine them in a df: df_speeches
csvs = [i for i in os.listdir(f'{directory}/csv_lemmatized') if (re.match(r'speeches_\d+\.csv', i) and ((int((re.search(r'\d+', i)[0])) > 2014)))]

df_speeches = pd.DataFrame()

for csv in csvs:
    path = f'{directory}/csv_lemmatized/{csv}'
    df = pd.read_csv(path, sep=';', header=0, encoding='utf-8')
    # keep only rows where the speech type is in one of the wanted categories
    df.loc[:, 'speech_type'] = df['speech_type'].apply(clean_speech_type)
    df = df[df['speech_type'].isin(WANTED_SPEECH_TYPES)]
    # add 'year' column to df, populate with the year of the csv
    year = int(re.search(r'\d+', csv)[0])
    df['year'] = year
    if len(df_speeches)==0:
        df_speeches = df
    else:
        df_speeches = pd.concat([df_speeches, df], axis=0, ignore_index=True)

df_speeches['n_words_in_speech'] = df_speeches.apply(lambda x: calculate_speech_length(x['content']), axis=1)

# save speech lengths in a separate df
df_speech_lengths = pd.DataFrame(columns=['speaker_id','year','len_min','len_max','len_mean','len_median','words_total']).astype({'speaker_id':str,'year':int,'len_min':float,'len_max':float,'len_mean':float,'len_median':float,'words_total':int})
for speaker in df_speeches['speaker_id'].unique():
    for year in df_speeches['year'].unique():
        len_min = df_speeches['n_words_in_speech'].loc[(df_speeches['year']==year)&(df_speeches['speaker_id']==str(speaker))].min()
        len_max = df_speeches['n_words_in_speech'].loc[(df_speeches['year']==year)&(df_speeches['speaker_id']==str(speaker))].max()
        len_mean = df_speeches['n_words_in_speech'].loc[(df_speeches['year']==year)&(df_speeches['speaker_id']==str(speaker))].mean()
        len_median = df_speeches['n_words_in_speech'].loc[(df_speeches['year']==year)&(df_speeches['speaker_id']==str(speaker))].median()
        words_total = df_speeches['n_words_in_speech'].loc[(df_speeches['year']==year)&(df_speeches['speaker_id']==str(speaker))].sum()
        df_speech_lengths = pd.concat([df_speech_lengths,pd.DataFrame.from_dict(data={'speaker_id':[speaker], 'year':[year], 'len_min':[len_min], 'len_max':[len_max],'len_mean':[len_mean],'len_median':[len_median],'words_total':[words_total]}, orient='columns')], axis=0, ignore_index=True)

df_speech_lengths = df_speech_lengths[df_speech_lengths['speaker_id'].notna()]

# checkpoint save
# save df_speech_lengths to csv
file_path_write = f'{directory}/csv_analysis/filtered/speaker_speech_lengths_lemma.csv'
try:
    df_speech_lengths.to_csv(file_path_write, sep=';', header=True, index=False, encoding='utf-8')
except FileExistsError:
    os.remove(file_path_write)
    df_speech_lengths.to_csv(file_path_write, sep=';', header=True, index=False, encoding='utf-8')

# checkpoint save
# save df_speech_lengths to csv
file_path_write = f'{directory}/csv_analysis/filtered/speeches_combined_plus_length_lemma.csv'
try:
    df_speeches.to_csv(file_path_write, sep=';', header=True, index=False, encoding='utf-8')
except FileExistsError:
    os.remove(file_path_write)
    df_speeches.to_csv(file_path_write, sep=';', header=True, index=False, encoding='utf-8')