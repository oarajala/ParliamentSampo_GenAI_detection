# comparison between performance of simplemma and pyvoikko
# rawdata csvs 2015-2025 -> check unlemmatized rows -> lemmatize -> compare missing and quality
# use files in /csv_lemmatized/ directory
# use rows where content_lemmatized_pos is missing
import os
import re
import simplemma
import pyvoikko
import pandas as pd
import numpy as np
from utils import helpers
directory = helpers.get_parent_directory()

csv_files_to_use_list = [i for i in os.listdir(f'{directory}/csv_lemmatized') if re.match(r'speeches_\d+\.csv', i) is not None]
year, max_year = 2015, 2025

# own df for both tools
# save results in own csvs in the /test/ directory

def helper_pyvoikko(cont: str):
    # format output string
    str_out = str()
    # turn input string into a list
    cont = cont.split()
    for i in cont:
        i = pyvoikko.analyse(helpers.clean_string(i))
        if (i is not None) and (len(i)>0) and (i[0].CLASS != 'etunimi'):
            str_out = str_out+' '+i[0].BASEFORM
    if len(str_out) == 0:
        return None
    else:
        return str_out.strip()

def helper_simplemma(cont: str):
    str_out = str()
    cont = cont.split()
    for i in cont:
        str_out = str_out+' '+helpers.clean_string(i)
    if len(str_out) == 0:
        return None
    else:
        return str_out.strip()

#helper_simplemma('s = Arvoisa puhemies! Tämä ”tiedustelukulttuuri” tässä vilahtelee. Ja kun aihe kiinnostaa kollegoita, niin hieman taustaa. En ole teemaa tai sanaa itse keksinyt. Se on asiaa paremmin tuntevien käyttöön ottama, mutta olen itse sitä ruvennut valiokunnassa käyttämään ja eduskunnassa käyttämään, koska minun mielestäni se on hyvä sana, joka kuvaa lainsäädäntöä, luottamusta, viranomaistoimintaa ja kaikkea sitä, mikä tähän kuuluu. Jos — niin kuin tiedän — esimerkiksi edustaja Kiljunen on kiinnostunut kirjallisuudesta tutkijana, niin teoksen nimi on ”Suomalaisen tiedustelukulttuurin jäljillä”, ja se on Maanpuolustuskorkeakoulun julkaisu vuodelta 2020, toimittanut Tommi Koivula, sotataidon laitos. Julkaisu on ladattavissa myös verkosta, ja eduskunnan kirjasto auttaa tarvittaessa erinomaisella tavalla, jos joku haluaa. Olen kirjan lukenut, ja itselleni se oli kyllä hyvin antoisa teos, joka antoi syvyyttä tällaiselle siviilille, poliitikolle, joka sitten mielellään kuulee ja lukee asiantuntijoiden näkemyksiä asioista. Sieltä kumpuaa tämä ”tiedustelukulttuuri”‑sana. [Kimmo Kiljunen: Kiitos vihjeestä!]')

year, max_year = 2015, 2025

while year <= max_year:
    # read the year's contents from a csv
    year_csv = pd.read_csv(f'{directory}/csv_lemmatized/speeches_{year}.csv', sep=';', header=0)
    year_csv['lem_simplemma'] = None
    year_csv['lem_pyvoikko'] = None

    year_csv['lem_simplemma'] = year_csv.apply(lambda x: ' '.join(simplemma.text_lemmatizer(helper_simplemma(x['content']), lang=x['lang'])) if (x['lang'] in {'fi', 'sv'}) else None, axis=1)
    #year_csv['lem_pyvoikko'] = year_csv.apply(lambda x: helper_pyvoikko(x['content']), axis=1)
    year_csv['lem_pyvoikko'] = year_csv.apply(lambda x: helper_pyvoikko(x['content']) if (x['lang']=='fi') else None, axis=1)

    try:
        file_path_write = f'{directory}/test/lem_comparison_{year}.csv'
        year_csv[['content','content_lemmatized','lem_pyvoikko','lem_simplemma']].to_csv(file_path_write, sep=';', header=True, index=False)
    except FileExistsError:
        pass

    year = year+1

print(year_csv[['content', 'content_lemmatized_pos', 'lem_simplemma', 'lem_pyvoikko']].loc[(year_csv['lem_simplemma'].isna()==False)|(year_csv['lem_pyvoikko'].isna()==False)])
print(year_csv[['content', 'content_lemmatized_pos', 'lem_simplemma', 'lem_pyvoikko']].loc[(year_csv['lem_pyvoikko'].isna()==False)])

df = year_csv[['content','lem_simplemma','lem_pyvoikko']].loc[(year_csv['lem_simplemma'].notna()==True)&(year_csv['lem_pyvoikko'].notna()==True)&(year_csv['lem_simplemma'] != year_csv['lem_pyvoikko'])]
df.reset_index(inplace=True)
# v2025 80% lemmatisoinneista eroaa:
(df.shape[0]/year_csv.shape[0])*100
# tallennetaan csv-tiedostoihin erot per vuosi, vertaillaan kummassa (simplemma vs pyvoikko) on enemmän sanoja mitä ei löydy virallisesta sanastosta
# haetaan virallinen sanasto internetistä, tästä on txt olemassa

# luetaan nykysuomen sanalista 2024
df_sanalista = pd.read_csv(f'{directory}/nykysuomensanalista2024.txt', sep='\t', header=0, usecols=['Hakusana','Homonymia','Sanaluokka','Taivutustiedot'])

# lue vertailu-csv:t
df_comparison_com = pd.DataFrame(data=None, columns=['content','content_lemmatized','lem_pyvoikko','lem_simplemma']).astype({'content': str, 'content_lemmatized': str, 'lem_pyvoikko': str, 'lem_simplemma': str})

for csv in [i for i in os.listdir(f'{directory}/test') if re.match(r'lem_comparison_\d+\.csv', i) is not None]:
    df = pd.read_csv(f'{directory}/test/{csv}', sep=';', header=0)
    df_comparison_com = pd.concat([df_comparison_com, df], axis=0, ignore_index=True)

# lem_pyvoikko-sarakkeen sisältö omaan listaan
# -> uniikit sanat setillä
lem_pyvoikko_list = list([' '.join([i for i in df_comparison_com['lem_pyvoikko'].loc[df_comparison_com['lem_pyvoikko'].notna()==True]])])[0].split()
lem_pyvoikko_list = list(set(lem_pyvoikko_list))
# fiksataan tuplaväliviiva '--' jonka pyvoikko luo ajatusviivasta
lem_pyvoikko_list = [i.replace('--', '-') for i in lem_pyvoikko_list]

# lem_simplemma-sarakkeen sisältö omaan listaan
# -> uniikit sanat setillä
lem_simplemma_list = list([' '.join([i for i in df_comparison_com['lem_simplemma'].loc[df_comparison_com['lem_simplemma'].notna()==True]])])[0].split()
lem_simplemma_list = list(set(lem_simplemma_list))

# kuinka monta sanaa löytyy nykysuomen sanalistasta
sanalista = [i for i in [' '.join([i for i in df_sanalista['Hakusana']])]][0].split()

n_diff_pyvoikko = set(lem_pyvoikko_list).difference(set(sanalista))
n_diff_simplemma = set(lem_simplemma_list).difference(set(sanalista))
print(f'pyvoikko ratio of difference: {len(n_diff_pyvoikko)/len(lem_pyvoikko_list)*100} % ({len(n_diff_pyvoikko)}) of {len(lem_pyvoikko_list)} words not found in sanalista')
print(f'simplemma ratio of difference: {len(n_diff_simplemma)/len(lem_simplemma_list)*100} % ({len(n_diff_simplemma)}) of {len(lem_simplemma_list)} words not found in sanalista')

len(n_diff_pyvoikko)
len(n_diff_simplemma)
n_diff_pyvoikko
n_diff_simplemma
len(sanalista)
print(lem_pyvoikko_list)
print(sanalista)

for i, d in df.iterrows():
    #print(d.lem_simplemma)
    #print(d.lem_pyvoikko)
    #print(d.content)
    simp = d.lem_simplemma.split()
    voik = d.lem_pyvoikko.split()
    print(f'i: {i} diff: {set(simp).difference(set(voik))}')

print(df['content'].iloc[19477])
print(df['lem_simplemma'].iloc[19477])
print(df['lem_pyvoikko'].iloc[19477])


a = pyvoikko.analyse('yksityiskohtainen')
a[0].FSTOUTPUT