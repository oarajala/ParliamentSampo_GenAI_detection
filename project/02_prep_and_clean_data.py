import pandas as pd
import numpy as np
import re
import os
from scipy import stats
from utils import helpers
directory = helpers.get_parent_directory()

csv_files_to_use_list = [i for i in os.listdir(f'{directory}/csv_lemmatized') if re.match(r'speeches_\d+\.csv', i) is not None]

year, max_year = int(min(re.findall(r'\d+', ' '.join(csv_files_to_use_list)))), int(max(re.findall(r'\d+', ' '.join(csv_files_to_use_list))))

# Retrieve distinct WORDS from lemmatized speeches per each raw data csv year. Process each years csv_lemmatized/*.csv separately.
# Count frequency for each individual word per year, combine them in a dictionary and build a dataframe for all years. The df is later
# pivoted into wide format.
# Each enriched csv_lemmatized/*.csv is first read, individual words from 'content_lemmatized' column sent for individual word extraction,
# the words are then counted (end up with a dictionary where key=word and value=n). The dict is then saved as a df and as a csv.
# These csvs are again later read and combined into one, wide, pivoted csv.
# ### HOX HOX HOX
# ### HARD CODING FOR TEST
year = 2025
max_year = 2025
while year <= max_year:
    # save the year's word freqs as a csv ("checkpoint save")
    save_file_name = f'word_frequency_per_year_{year}.csv'
    # if the file already exists -> skip the year
    # -> if you want to remake the data for the year Y, delete the file and run the script
    if save_file_name in os.listdir(f'{directory}/csv_analysis/'):
        pass
    else:
        # read the year's contents from a csv
        year_csv = pd.read_csv(f'{directory}/csv_lemmatized/speeches_{year}.csv', sep=';', header=0)
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
if save_file_name in os.listdir(f'{directory}/csv_analysis/'):
    os.remove(f'{directory}/csv_analysis/{save_file_name}')
z_score_comp_df.to_csv(f'{directory}/csv_analysis/{save_file_name}', sep=';', header=True, index=False, encoding='utf-8')

save_file_name = 'word_frequency_all_years.csv'
if save_file_name in os.listdir(f'{directory}/csv_analysis/'):
    os.remove(f'{directory}/csv_analysis/{save_file_name}')
frequency_comp_df.to_csv(f'{directory}/csv_analysis/{save_file_name}', sep=';', header=True, index=False, encoding='utf-8')