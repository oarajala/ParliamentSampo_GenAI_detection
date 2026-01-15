import os
from datetime import timedelta, datetime, date
import re
import pandas as pd

CHATGPT_RELEASE_YEAR = int(2022)

def get_parent_directory() -> str:
    """Get the parent directory for handling csv files.

    Returns:
        string: the path to the directory where directories for csv files are located
    """
    #create relative path for parent
    relative_parent = os.path.join(os.getcwd(), '.')

    #use abspath for absolute parent path
    return str(os.path.abspath(relative_parent)).replace('\\', '/')

def clean_special_chars_from_str(string: str):
    """Clean special characters from input string. Return input string in lower case.
    """
    string = str(string)
    # words shall all be lower case
    string = string.lower()
    # replace special characters as blanks -> extract only words
    # modify list as necessary
    string = re.sub(r'[\.\?\+\/\$\[\]\(\)\'\’\`,;!:%"&”]+', '', string)
    # replace dash '-' if it appears between two whitespaces ' - '; do nothing if dash '-' is between two characters
    string = re.sub(r'\s\—\s', ' ', string)
    string = re.sub(r'\s\-\s', ' ', string) 
    # replace linebreaks '\n' as spaces ' '
    string = re.sub(r'\n', ' ', string)
    # replace tabulation '\t' as space ' '
    string = re.sub(r'\t', ' ', string)
    # replace double spaces '  ' as a single space ' '
    string = string.replace('  ', ' ')
    # remove spaces at the start and end
    string = string.strip()
    # return words
    return string

def calculate_electoral_term_progression(date: str, electoral_term: str) -> int:
    """Added data validation due to missing values in 2011 raw csv.
    """
    if (date is None) or (electoral_term is None):
        return None
    if (type(date) != str) or (type(electoral_term) != str):
        return None
    elif ((date is not None) and (date.strip() == '')) or ((electoral_term is not None) and (electoral_term.strip() == '')):
        return None
    else:
        dt_date = datetime.strptime(date, "%Y-%m-%d")
        dt_et_start = datetime.strptime(electoral_term[:10], "%Y-%m-%d")
        dt_et_end = datetime.strptime(electoral_term[11:], "%Y-%m-%d")

        # calculate the length of the electoral term, store as days
        et_length = (dt_et_end-dt_et_start)
        et_length = et_length.days

        # calculate the time in days to the end of the electoral term
        days_to_end_of_term = dt_et_end-dt_date
        days_to_end_of_term = days_to_end_of_term.days

        # calculate the time served of the electoral term at the time of date (speech) in days
        days_serverd_from_total_et = et_length-days_to_end_of_term

        # calculate the progression of the electoral term relative to the date (speech)
        progression = int(round((days_serverd_from_total_et/et_length)*100, 0))

        return progression
    
def list_z_score_per_df_year(df: pd.DataFrame, df_cols: list) -> list:
    """20260113 NOT USED AT THE MOMENT
    Eats a df and a list of column names. Creates a list of values for an easy row concatenation (transposition) into another df.
    Inserts None as value for differences in transposable data and column list.
    Used for transposing/pivoting data into wide format from long lists of z-scores.
    """
    cols_list = [re.search(r'\d+', i)[0] for i in df_cols if re.search(r'\d+', i) is not None]
    df_years_list = [str(i) for i in df['year'].values]
    differences = [i for i in cols_list if i not in df_years_list]
    if len(differences)>0:
        [df_years_list.append(i) for i in differences]
    df_years_list = sorted(df_years_list)

    try:
        values_list_out = []
        for i in df_years_list:
            if i in differences:
                values_list_out.append(None)
            else:
                values_list_out.append(df['z_per_year'].loc[df['year'] == int(i)].array[0])
    except Exception:
        raise
    
    return values_list_out

def extract_words(speech: str):
    """Extracts each word from a speech. Returns the words as a string.
    """
    # words shall all be lower case
    speech = speech.lower()
    # replace special characters as blanks -> extract only words
    # modify list as necessary
    speech = re.sub(r'[\.\?\+\/\$\[\]\(\)\'\’\`,;!:%"&”]+', '', speech)
    # replace dash '-' if it appears after a break but attached to a word; do nothing if dash '-' is between two characters
    speech = re.sub(r'\s\-', ' ', speech) 
    # replace numbers as blanks -> extract only words
    speech = re.sub(r'[0-9]', '', speech)
    # replace linebreaks '\n' as spaces ' '
    speech = re.sub(r'\n', ' ', speech)
    # replace tabulation '\t' as space ' '
    speech = re.sub(r'\t', ' ', speech)
    # replace double spaces '  ' as a single space ' '
    speech = speech.replace('  ', ' ')
    # remove spaces at the start and end
    speech = speech.strip()
    # return words
    return speech

def extract_sentences(speech: str):
    """Extracts sentences, defined as strings starting and ending at punctuation:
    'A quick brown fox, jumped over? A lazy dog.' -> ['a quick brown fox,', 'jumped over?', 'a lazy dog']
    All strings will be returned in lower case.
    """
    sentences = re.split(r'[\.\?\+\-\/,;!]', speech)
    # strip spaces
    sentences = [i.strip() for i in sentences]
    # lower case
    sentences = [i.lower() for i in sentences]
    # keep strings in the list only if their length is over 0 -> they have content.
    sentences = [i for i in sentences if len(i)>0]
    # return the list
    return sentences

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

def linear_extrapolation(y: list, x: list, n=1) -> list:
    """_summary_

    Args:
        y (list): _description_
        x (list): _description_
        n (int, optional): _description_. Defaults to 1.

    Returns:
        list: _description_
    """
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