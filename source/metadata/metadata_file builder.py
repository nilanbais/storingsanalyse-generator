"""
Bouwen van de metadata
De metadata is nodig voor het berekeken van de gemiddelde aantal meldingen/storingen per maand en de TOV-tabellen.

De opbouw van de metadata is (vooralsnog) als volgt:

{
    project: projectnaam,
    start_datum: dd-mm-yyy,
    contract_info: {
        tijdsregistratie: True,
        minimale_beschikbaarheid: xx,
        minimale_responsetijd: 04:00:00,
    },
    meldingen: {
        f"{maand}_{jaar}": {
            DI_num: aantal meldingen,
            DI_num: aantal meldingen
        }
        f"{maand}_{jaar}": {
            DI_num: aantal meldingen,
            DI_num: aantal meldingen
        }
    },
    storingen: {
        f"{maand}_{jaar}": {
            DI_num: aantal storingen,
            DI_num: aantal storingen
        }
        f"{maand}_{jaar}": {
            DI_num: aantal storingen,
            DI_num: aantal storingen
        }
    }
}
In deze opbouw worden enkel de deelinstallaties meegenomen met meldingen > 0. Dit geldt ook voor de storingen.
Om DI_num om te zetten naar een omschrijving kan de functie get_breakdown_description() gebruikt worden.

Voor het opslaan van de metadata wordt (voor nu) gekozen voor een .json-type
"""
import json
import pandas as pd
import os
import numpy as np
from datetime import datetime

from pandas import DataFrame

# Changing current working dir to the src folder
while 1:
    if os.getcwd().endswith('src'):
        break
    else:
        os.chdir('..')


# Todo: OPTIE uitzoeken of het nuttig is om hier een class voor te maken.

def get_first_key(dictionary: dict) -> dict:
    return list(dictionary.keys())[0]


def del_empty_keys(dictionary: dict) -> dict:
    """
    The tabs that are read have a pre-defined table. This results in some empty dicts with key names that represent
    future months
    :param dictionary:
    :return: Dict without
    """
    return {key: dictionary[key] for key in dictionary.keys() if dictionary[key] != {}}


def clean_dt_string_month(dt_string: str) -> str:
    month_notation = ['Jan', 'Feb', 'Mrt', 'Apr', 'Mei', 'Jun', 'Jul', 'Aug', 'Sept', 'Okt', 'Nov', 'Dec']
    month_notation = {month_notation[idx]: str(idx + 1) for idx in range(len(month_notation))}

    dt_month, dt_year = month_notation[dt_string.split(' - ')[0]], datetime.strptime(dt_string.split(' - ')[1], '%y')

    dt_string = '0' + dt_month + '_' + datetime.strftime(dt_year, '%Y') if len(dt_month) == 1 \
        else dt_month + '_' + datetime.strftime(dt_year, '%Y')

    return dt_string


def clean_dt_string_q(dt_string: str) -> str:
    return dt_string.replace('-', '_').replace(' ', '')


def clean_inputdata(inputdata: DataFrame, index_first_col_maanden: int, category_column_name: str, time_bin: str = 'month') -> dict:
    """
    Gestandaardiseerde aanpak voor het schoonmaken van de input dataframes uit het rekendocument (excel) van
    Remko van Gorkum.
    :param inputdata:
    :param index_first_col_maanden:
    :param category_column_name:
    :return:
    """
    _inputdata = inputdata.iloc[:-3, :]  # onderste 3 rijen zijn overbodig  EDIT (??is dit altijd zo??)
    dictionary = {}
    for col in _inputdata.iloc[:, index_first_col_maanden:]:
        if _inputdata[col][0].lower() == 'totaal':
            break

        datetime_obj = clean_dt_string_month(_inputdata[col][0]) if time_bin == 'month' else clean_dt_string_q(_inputdata[col][0])
        # initialize empty dict for month
        if datetime_obj not in dictionary:
            dictionary[datetime_obj] = {}  # Creates an empty dict w/ month as key in the dict

        for index, row in _inputdata.iterrows():
            if row[col] is np.nan:
                break
            elif index > 0 and int(row[col]) > 0:
                dictionary[datetime_obj][row[category_column_name]] = row[col]

    # dictionary = del_empty_keys(dictionary)

    return dictionary


# Full path to input file
project = 'Coentunnel-tracé'
file_input = 'metadata//20210505 Storingsdatabase Q1 2021.xlsx'
excel_file = pd.ExcelFile(file_input)

inputdata_subsystems = pd.read_excel(excel_file, list(filter(lambda x: x.lower() == 'onterechte meldingen totaal', excel_file.sheet_names))[0])
inputdata_poo_codes = pd.read_excel(excel_file, list(filter(lambda x: x.lower() == 'probleem oorzaak oplossing', excel_file.sheet_names))[0])

inputdata_meldingen = pd.read_excel(excel_file, list(filter(lambda x: x.lower() == 'trend maand meldingen', excel_file.sheet_names))[0])
inputdata_storingen = pd.read_excel(excel_file, list(filter(lambda x: x.lower() == 'trend maand storingen', excel_file.sheet_names))[0])

inputdata_poo_probleem = pd.read_excel(excel_file, list(filter(lambda x: x.lower() == 'overzicht probleem', excel_file.sheet_names))[0])
inputdata_poo_oorzaak = pd.read_excel(excel_file, list(filter(lambda x: x.lower() == 'overzicht oorzaak', excel_file.sheet_names))[0])
inputdata_poo_oplossing = pd.read_excel(excel_file, list(filter(lambda x: x.lower() == 'overzicht oplossing', excel_file.sheet_names))[0])

"""
Possible subsystem numbers
"""
possible_subsystems = set()

# Sluis Eefde gebruikt 'SBS subsysteem code'  -  ipv 'SBS sub-systeem code'
column = 'SBS subsysteem code' if project == 'Sluis Eefde' else 'SBS sub-systeem code'
for x in inputdata_subsystems[column][inputdata_subsystems[column].notnull()]:
    possible_subsystems.add(str(x))

"""
meldingen per di_num
di_num = SBS sub-systeem code
"""
meldingen = clean_inputdata(inputdata_meldingen,
                            index_first_col_maanden=4,
                            category_column_name='SBS sub-systeem code',
                            time_bin='month')

"""
storingen per di_num
di_num = SBS sub-systeem code
"""
storingen = clean_inputdata(inputdata_storingen,
                            index_first_col_maanden=4,
                            category_column_name='SBS sub-systeem code',
                            time_bin='month')
"""
POO-codes (Probleem/Oorzaak/Oplossing codes)
"""
poo_probleem = clean_inputdata(inputdata_poo_probleem,
                               index_first_col_maanden=2,
                               category_column_name='Probleem code',
                               time_bin='q')

poo_oorzaak = clean_inputdata(inputdata_poo_oorzaak,
                              index_first_col_maanden=2,
                              category_column_name='Oorzaak code',
                              time_bin='q')

poo_oplossing = clean_inputdata(inputdata_poo_oplossing,
                                index_first_col_maanden=2,
                                category_column_name='Oplossing code',
                                time_bin='q')

poo_codes = {"probleem": poo_probleem,
             "oorzaak": poo_oorzaak,
             "oplossing": poo_oplossing}

poo_code_overzicht = dict()
col_names = ['Probleem', 'Oorzaak', 'Oplossing']
for name in col_names:
    i = inputdata_poo_codes.columns.get_loc(name)
    col_data = inputdata_poo_codes.iloc[:, i].to_dict()
    beschrijving_data = inputdata_poo_codes.iloc[:, i+1].to_dict()

    dict2add = {}
    for idx in range(len(col_data)):
        if col_data[idx] is np.nan:
            break

        if list(col_data.keys())[idx] not in poo_code_overzicht:
            dict2add[col_data[idx]] = beschrijving_data[idx]

    poo_code_overzicht = {**poo_code_overzicht, **dict2add}

"""
Tijdregistratie
"""
tijdsregistratie = "False"

"""
Set-up vna het JSON-Object
"""
contract_info = {"tijdsregistratie": tijdsregistratie,
                 "minimale_beschikbaarheid": "xx",
                 "minimale_responsetijd": "04:00:00",
                 "aanwezige_deelinstallaties": tuple(possible_subsystems),
                 "POO_codes": poo_code_overzicht}

start_datum = get_first_key(meldingen)

json_dict = {"project": project,
             "start_datum": start_datum,
             "contract_info": contract_info,
             "poo_codes": poo_codes,
             "meldingen": meldingen,
             "storingen": storingen}

# with open(f"metadata//metadata_file_{project.lower().replace(' ', '_')}.json", 'w') as output_file:
#     json.dump(json_dict, output_file)
