# ParliamentSampo_GenAI_detection
Attempts at detecting the use of GenAI from speeches stored in ParliamentSampo (Parlamenttisampo).
2026-04-14: Note that this is an unfinished project. The project was abandoned once the analysis notebooks (project folder) could not reveal tangible evidence about the utilisation of LLMs in drafting speeches for plenary sessions in the Finnish Parliament. The project files are left in this repository as they currently are, and simply cloning this repo and pressing Play will not work. The repo is left here mostly as a future reference for myself.

## Project structure
```
project
-project -> scripts are here; named in order they are intended to be run
--01_create_data.py
--02_prep_and_clean_data.py
--03_analysis.py
--03b_analysis_person.ipynb
--03c_analysis_all_persons.ipynb
--03d_analysis_word_freqs_nonlemma.ipynb
--03e_analysis_word_freqs_lemma.ipynb
--03f_analysis_word_freqs_lemma_filtered.ipynb
-utils
--helpers.py -> helper functions
-csv_rawdata -> created in the scripts; raw data csvs from ParlamenttiSampo saved for quick access
--speeches_2000.csv
--...
-csv_lemmatized -> created in the scripts; enriched raw data csvs: added data includes lemmatization and election cycle progress
--speeches_2000.csv
--...
-csv_analysis -> created in the scripts; analysis-ready csvs
--word_frequency_per_year_2000.csv
--word_frequency_all_years_csv.
--...
-ai_release_timeline.csv -> dates of some major generative AI releases
```
Csv files:
- encoding: utf-8
- separator: ; (semicolon) 
- header: yes, line index 0

## Quickstart
.py files in the /project/ directory are named 01_, 02_, ... etc. and are inteded to be run in this order. The files create directories as necessary.

### project/01_create_data.py
Note that retrieving metadata for each row in each csv is done in a loop. Retrieving metadata and adding lemmatization for all files takes several hours. It is best to try this for one year at a time or to create as little data as possible. 
### project/02_prep_and_clean_data.py
Note that counting word frequencies for each year is done in a loop and takes a while.
### project/02b_prep_and_clean_data.py
Note that counting word frequencies for each year is done in a loop and takes a while. Creates the data for the project/03f_analysis_word_freqs_nonlemma_filtered.ipynb notebook. The CSVs prepared by this file are stored in the folder /csv_analysis/filtered/ . This filters the data by "speech_type" category, keeping only the following categories: 'Esittelypuheenvuoro', 'Ryhmäpuheenvuoro', 'Varsinainen puheenvuoro'. These are considered "prepared" speeches, or speeches where a Member of Parliament prepares the speech beforehand and therefore could realistically use an LLM to write the speech. 
### project/03_analysis.py 
A work test file for quick peeks into the data.
### project/03b_analysis_person.ipynb
Checking changes in speech (mainly word frequencies, also fluctuations in minimum and maximum lenghts of speeches by word count) at the speaker level. Analysis limited to speakers who were present in the data in all years 2015-2025.
### project/03c_analysis_all_persons.ipynb
Checking changes in speech (mainly word frequencies, also fluctuations in minimum and maximum lenghts of speeches by word count) at the speaker level. Analysis NOT limited to speakers who were present in the data in all years 2015-2025.
### project/03d_analysis_word_freqs_nonlemma.ipynb
Checking changes in speech (mainly word frequencies, also fluctuations in minimum and maximum lenghts of speeches by word count). The analysis is done at the population level without regard to persons, party levels or anything like that. Used NON-LEMMATISED data from years 2015-2025.
### project/03e_analysis_word_freqs_lemma.ipynb
Checking changes in speech (mainly word frequencies, also fluctuations in minimum and maximum lenghts of speeches by word count). The analysis is done at the population level without regard to persons, party levels or anything like that. Used LEMMATISED data from years 2015-2025.
### project/03f_analysis_word_freqs_nonlemma_filtered.ipynb
Checking changes in speech (mainly word frequencies, also fluctuations in minimum and maximum lenghts of speeches by word count). The analysis is done at the population level without regard to persons, party levels or anything like that. Used LEMMATISED data from years 2015-2025, filtered by speech_type. Check project/02b_prep_and_clean_data.py above for more information.
