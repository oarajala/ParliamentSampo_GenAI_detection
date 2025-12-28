# ParliamentSampo_GenAI_detection
Attempts at detecting the use of GenAI from speeches stored in ParliamentSampo (Parlamenttisampo).

## Quickstart
First run create_data/create_data.py. This will create two new directories in the programme directory: csv_rawdata and csv_lemmatization_added. The script will retrieve transcribed speeches from Parlamenttisampo from the year 2015 onward into the former directory, add lemmatization into to the files and store these enriched files into the latter directory. Files will be stored in csv format.

Csv files:
- encoding: utf-8
- separator: , (comma)
- header: yes, line index 0