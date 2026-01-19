# ParliamentSampo_GenAI_detection
Attempts at detecting the use of GenAI from speeches stored in ParliamentSampo (Parlamenttisampo).

## Project structure
project
- project -> scripts are here; named in order they are intended to be run
- utils
  - helpers.py -> helper functions
- csv_rawdata -> raw data csvs from ParlamenttiSampo saved for quick access
- csv_lemmatized -> enriched raw data csvs: added data includes lemmatization and election cycle progress
- csv_analysis -> "save point" csvs for analysis phase

Csv files:
- encoding: utf-8
- separator: ; (semicolon) 
- header: yes, line index 0

## Quickstart
.py files in the /project/ directory are named 01_, 02_, ... etc. and are inteded to be run in this order. The files create directories as necessary.

### project/01_create_data.py
Note that retrieving metadata for each row in each csv is done in a loop. Retrieving metadata and adding lemmatization for all files takes several hours. It is best to try this for one year at a time or to create as little data as possible. 
### project/02_pre_and_clean_data.py
Note that counting word frequencies for each year is done in a loop and takes a while.
### project/03_analysis.py
This file is unstructured and a work in progress.
