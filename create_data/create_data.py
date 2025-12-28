# onnistuuko parlamenttisammon datojen haku
# -> suora csv-luku palvelusta
# https://www.ldf.fi/dataset/semparl -> Speeches

import pandas as pd
import requests
import re
import os
import time

# Create necessary directories if they do not exist: "csv_rawdata/" and "csv_lemmatization_added/"
if 'csv_rawdata' not in os.listdir(path='.'):
    os.mkdir(path='./csv_rawdata')
if 'csv_lemmatization_added' not in os.listdir(path='.'):
    os.mkdir(path='./csv_lemmatization_added')

def parent_directory() -> str:
    """Get the parent directory for handling csv files.

    Returns:
        string: the path to the directory where directories for csv files are located
    """
    #create relative path for parent
    relative_parent = os.path.join(os.getcwd(), '.')

    #use abspath for absolute parent path
    return str(os.path.abspath(relative_parent)).replace('\\', '/')

parent_directory_str = parent_directory()

def get_list_of_csv_online():
    """_summary_

    Returns:
        _type_: _description_
    """
    url = 'https://a3s.fi/parliamentsampo/speeches/csv/index.html'

    try:
        response = requests.get(url)
    except Exception as e:
        print(f'Unexpected error trying to access {url}: Status code: {response.status_code}')
        raise

    if response.status_code == 200:
        # save the response as raw html
        res = response.text
        # extract all csv files from the html
        csv_files_list = re.findall(r'speeches_\d+.*?.csv', res, re.IGNORECASE)
        # return only unique items
        return set(csv_files_list)

list_online = get_list_of_csv_online()

# LIMIT FILES TO YEARS 2010->
list_online = [i for i in list_online if re.search(r'\d+', i) is not None and int(re.search(r'\d+', i).group(0)) >= 2010]

def get_csv_file(file_name):
    """Download a csv file and save it locally for quick access.
    output_folder is the directory where the csv is stored.

    Args:
        file_name (_type_): _description_

    Returns:
        _type_: _description_
    """
    output_folder = parent_directory_str+'/csv_rawdata'
    
    try:
        if file_name not in os.listdir(output_folder):
            csv = pd.read_csv(f'https://a3s.fi/parliamentsampo/speeches/csv/{file_name}', sep=',')
            csv.to_csv(f'{output_folder}/{file_name}', header=True, index=False, sep=',')
            return 0
        return 0
    except:
        raise

# retrieve the csv files to save in a local folder for quick access
for i in list_online:
    get_csv_file(i)

# continue from saved csv files:
# - get csv files 1 by 1
# - add 'url' column: this is the address to the speeche's metadata and lemmatized information, if it exists
# -- (afaik the address follows the same format for each dataset <- CHECK THIS)
# - get content_lemmatized and content_lemmatized_pos information for each dataset
# -- own functions for both operations
# - save enriched csv files to their own location

def create_url(sid) -> str:
    """tehdään url ldf-hakuja varten
    params: 
    - sid = str: speech_id
    returns:
    ldf-url
    """
    url = 'http://ldf.fi/semparl/speeches/'
    sid_split = re.split('_', sid)
    
    year = sid_split[0]
    session = sid_split[1]
    speechord = sid_split[2]

    # set len of session to 3, pad zeros in front of it until len is 3
    if len(session) < 3:
        while len(session) < 3:
            session = '0'+session

    # set len of speechord to 3, pad zeros in front of it until len is 3
    if len(speechord) < 3:
        while len(speechord) < 3:
            speechord = '0'+speechord

    return f'{url}s{year}_1_{session}_{speechord}'

# extract lemmatized and lemmatized_pos information from content_full if present
# and store them in respective columns.

def extract_lemmatized(string: str) -> str:
    """_summary_

    Args:
        string (str): _description_

    Returns:
        str: _description_
    """
    if (string is not None) and ('semparl_linguistics:content_lemmatized' in string):
        lem_s = re.search('semparl_linguistics:content_lemmatized', string).end()
        lem_quote_s = re.search('"', string[lem_s:]).end()            
        lem_quote_s = lem_s+lem_quote_s
        lem_quote_e = re.search('"', string[lem_quote_s:]).start()
        lem_quote_e = lem_quote_s+lem_quote_e
        lem_content = string[lem_quote_s:lem_quote_e]
    else:
        lem_content = None

    return lem_content

def extract_lemmatized_pos(string: str) -> str:
    """_summary_

    Args:
        string (str): _description_

    Returns:
        str: _description_
    """
    if (string is not None) and ('semparl_linguistics:content_lemmatized_pos' in string):
        lem_pos_s = re.search('semparl_linguistics:content_lemmatized_pos', string).end()
        lem_pos_quote_s = re.search('"', string[lem_pos_s:]).end()            
        lem_pos_quote_s = lem_pos_s+lem_pos_quote_s
        lem_pos_quote_e = re.search('"', string[lem_pos_quote_s:]).start()
        lem_pos_quote_e = lem_pos_quote_s+lem_pos_quote_e
        lem_pos_content = string[lem_pos_quote_s:lem_pos_quote_e]
    else:
        lem_pos_content = None
    
    return lem_pos_content

# apply extract_lemmatized() and extract_lemmatized_pos() functions to df

for csv_file in os.listdir(parent_directory_str+'/csv_rawdata'):
    # if file already has been created -> skip everything
    # otherwise get the data and create it
    if csv_file in os.listdir(parent_directory_str+'/csv_lemmatization_added'):
        # do nothing
        print(f'{csv_file} already in directory. Skipping.')
        pass
    else:
        # do everything
        file_path_write = f'{parent_directory_str}/csv_lemmatization_added/{csv_file}'
        file_path_read = f'{parent_directory_str}/csv_rawdata/{csv_file}'
        i_file = pd.read_csv(file_path_read, sep=',', header=0, dtype=str)

        # get length of dataframe for progress monitoring
        i_file_length = i_file.shape[0]
        print(f'{csv_file}: {i_file_length} rows')

        # - add 'url' column: this is the address to the speeche's metadata and lemmatized information, if it exists
        i_file['url'] = i_file['speech_id'].apply(create_url)

        # add 'content_full' column for full content of metadata
        i_file['content_full'] = None

        # only retrieve full text data and metadata in for loop
        # time for progress monitoring
        start_time = time.time()
        for i, d in i_file.iterrows():
            # the url is in d.url -> store in a new variable for readability
            url_str = d.url
            try:
                t = requests.get(url_str)
                if t.status_code == 200:
                    t_t = t.text
                    i_file.loc[i_file['url'] == url_str, 'content_full'] = t_t
                    # a short break out of courtesy, no spamming the page unnecessarily
            except requests.exceptions.ConnectionError as e:
                print(f"Error connecting to the server: {e} ; File name: {csv_file}")
            except requests.exceptions.HTTPError as e:
                print(f"HTTP error occurred: {e}  ; File name: {csv_file}")
            except requests.exceptions.RequestException as e:
                print(f"An error occurred: {e}  ; File name: {csv_file}")
            finally:
                # print info on progress
                print(f'{csv_file}: retrieving data from Parlamenttisampo - {round(((i+1)/i_file_length)*100, 2)}%')
                # courteous wait
                time.sleep(0.3)
        print(f'{csv_file}: retrieved content from Parlamenttisampo in {round(time.time()-start_time, 2)} seconds')

        print(f'{csv_file}: extracting content_lemmatized')
        start_time = time.time()
        try:
            i_file['content_lemmatized'] = i_file['content_full'].apply(extract_lemmatized)
        except Exception as e:
            print(f'{csv_file}: Error at applying extract_lemmatized: {e}')
            pass
        print(f'{csv_file}: extracted content_lemmatized in {round(time.time()-start_time, 2)} seconds')
        
        print(f'{csv_file}: extracting content_lemmatized_pos')
        start_time = time.time()
        try:
            i_file['content_lemmatized_pos'] = i_file['content_full'].apply(extract_lemmatized_pos)
        except:
            print(f'{csv_file}: Error at applying extract_lemmatized_pos: {e}')
        print(f'{csv_file}: extracted content_lemmatized_pos in {round(time.time()-start_time, 2)} seconds')

        # drop unnecessary column 'content_full' from dataframe before saving
        i_file.drop('content_full', axis=1, inplace=True)

        # save enriched file
        try:
            i_file.to_csv(file_path_write, sep=',', header=True, index=False)
        except FileExistsError:
            os.remove(file_path_write)
            i_file.to_csv(file_path_write, sep=',', header=True, index=False)