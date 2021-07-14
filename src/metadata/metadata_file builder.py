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


def clean_dt_string(dt_string: str) -> str:
    month_notation = ['Jan', 'Feb', 'Mrt', 'Apr', 'Mei', 'Jun', 'Jul', 'Aug', 'Sept', 'Okt', 'Nov', 'Dec']
    month_notation = {month_notation[idx]: str(idx + 1) for idx in range(len(month_notation))}

    dt_month, dt_year = month_notation[dt_string.split(' - ')[0]], datetime.strptime(dt_string.split(' - ')[1], '%y')

    dt_string = '0' + dt_month + '_' + datetime.strftime(dt_year, '%Y') if len(dt_month) == 1 \
        else dt_month + '_' + datetime.strftime(dt_year, '%Y')

    return dt_string


# Vooraf gedefinieerde json variabele
project = 'Coentunnel-tracé'

contract_info = {"tijdsregistratie": "True",
                 "minimale_beschikbaarheid": "xx",
                 "minimale_responsetijd": "04:00:00"}

# Full path to input file
file_input = 'metadata//20210505 Storingsdatabase Q1 2021.xlsx'
excel_file = pd.ExcelFile(file_input)

# inputdata_meldingen = pd.read_excel(excel_file, excel_file.sheet_names[0])
# inputdata_storingen = pd.read_excel(excel_file, excel_file.sheet_names[1])
inputdata_subsystems = pd.read_excel(excel_file, list(filter(lambda x: x.lower() == 'onterechte meldingen totaal', excel_file.sheet_names))[0])

inputdata_meldingen = pd.read_excel(excel_file, list(filter(lambda x: x.lower() == 'trend maand meldingen', excel_file.sheet_names))[0])
inputdata_storingen = pd.read_excel(excel_file, list(filter(lambda x: x.lower() == 'trend maand storingen', excel_file.sheet_names))[0])

"""
Possible subsystem numbers
"""
possible_subsystems = set()

# Sluis Eefde gebruikt 'SBS subsysteem code'  -  ipv 'SBS sub-systeem code'
col = 'SBS subsysteem code' if project == 'Sluis Eefde' else 'SBS sub-systeem code'
for x in inputdata_subsystems[col][inputdata_subsystems[col].notnull()]:
    possible_subsystems.add(str(x))

contract_info['aanwezige_deelinstallaties'] = tuple(possible_subsystems)

"""
meldingen per di_num
di_num = SBS sub-systeem code
"""
# Todo: aanpassen zodat meldingen zonder di_num ook worden meegenomen.
meldingen_data = inputdata_meldingen.iloc[:-3, :]  # onderste 3 rijen zijn overbodig

# Lege dict voor alle meldingen per maand. maand in meldingen wordt dict (maand) in dict (meldingen).
# maanden worden toegevoegd in notatie [maand]-[jaar]
meldingen = {}

for col in meldingen_data.iloc[:, 4:]:  # mask on df gives only the columns w/ month

    if meldingen_data[col][0] == "Totaal":  # last column after the months in the df
        break
    else:
        dt_obj = clean_dt_string(meldingen_data[col][0])
        # initialize empty dict for month
        if dt_obj not in meldingen:
            meldingen[dt_obj] = {}  # Creates an empty dict w/ month as key in the meldingen dict

        for index, row in meldingen_data.iterrows():
            if row[col] is np.nan:  # If nan is seen => caught up to current date
                break
            elif index > 0 and int(row[col]) > 0:
                meldingen[dt_obj][row['SBS sub-systeem code']] = row[col]

"""
storingen per di_num
di_num = SBS sub-systeem code
"""
storingen_data = inputdata_storingen.iloc[:-3, :]  # onderste 3 rijen zijn overbodig  EDIT (??is dit altijd zo??)

# Lege dict voor alle storingen per maand. maand in storingen wordt dict (maand) in dict (storingen).
# maanden worden toegevoegd in notatie [maand]-[jaar]
storingen = {}

for col in storingen_data.iloc[:, 4:]:  # mask on df gives only the columns w/ month

    if storingen_data[col][0] == "Totaal":  # last column after the months in the df
        break
    else:
        dt_obj = clean_dt_string(storingen_data[col][0])
        # initialize empty dict for month
        if dt_obj not in storingen:
            storingen[dt_obj] = {}  # Creates an empty dict w/ month as key in the storingen dict

        for index, row in storingen_data.iterrows():
            if row[col] is np.nan:  # If nan is seen => caught up to current date
                break
            elif index > 0 and int(row[col]) > 0:
                storingen[dt_obj][row['SBS sub-systeem code']] = row[col]

meldingen = del_empty_keys(meldingen)
storingen = del_empty_keys(storingen)

start_datum = get_first_key(meldingen)

json_dict = {"project": project,
             "start_datum": start_datum,
             "contract_info": contract_info,
             "meldingen": meldingen,
             "storingen": storingen}

with open(f"metadata//metadata_file_{project.lower().replace(' ', '_')}.json", 'w') as output_file:
    json.dump(json_dict, output_file)
