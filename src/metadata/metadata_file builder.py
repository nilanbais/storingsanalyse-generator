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

# Changing current working dir to the src folder
while 1:
    if os.getcwd().endswith('src'):
        break
    else:
        os.chdir('..')

"""
Onderstaande is gekopieërd uit staging_file_generator.py
"""
# todo: functies in een package zetten voor een centraal beheer van de functies i.p.v. kopiëren en zo
# Omschrijvingen tabel inlezen
rel_path = f'..\\res\\location_description_map.json'
with open(rel_path, 'r') as r:
    description_data = json.load(r)

# Df for the connection between the sbs/lbs numbers and their description
description_df = pd.DataFrame(description_data)


def get_first_key(dictionary):
    return list(dictionary.keys())[0]


# Vooraf gedefinieerde json variabele
project = 'Coentunnel-tracé'
contract_info = {"tijdsregistratie": "True",
                 "minimale_beschikbaarheid": "xx",
                 "minimale_responsetijd": "04:00:00"}


# Full path to input file
file_input = 'metadata//20200715 Storingsdatabase Q2 2020.xlsx'
excel_file = pd.ExcelFile(file_input)

inputdata_meldingen = pd.read_excel(excel_file, excel_file.sheet_names[0])
inputdata_storingen = pd.read_excel(excel_file, excel_file.sheet_names[1])

"""
meldingen per di_num
di_num = SBS sub-systeem code
"""
meldingen_data = inputdata_meldingen.iloc[:-3, :]  # onderste 3 rijen zijn overbodig

# Lege dict voor alle meldingen per maand. maand in meldingen wordt dict (maand) in dict (meldingen).
# maanden worden toegevoegd in notatie [maand]-[jaar]
meldingen = {}

for col in meldingen_data.iloc[:, 4:]:  # mask on df gives only the columns w/ month

    if meldingen_data[col][0] == "Totaal":  # last column after the months in the df
        break
    else:
        print(meldingen_data[col][0])
        # initialize empty dict for month
        if meldingen_data[col][0] not in meldingen:
            # todo: format maand-jaar notatie aanpassen
            meldingen[meldingen_data[col][0]] = {}  # Creates an empty dict w/ month as key in the meldingen dict

        for index, row in meldingen_data.iterrows():
            if row[col] is np.nan:  # If nan is seen => caught up to current date
                break
            elif index > 0 and int(row[col]) > 0:
                meldingen[meldingen_data[col][0]][row['SBS sub-systeem code']] = row[col]

"""
storingen per di_num
di_num = SBS sub-systeem code
"""
storingen_data = inputdata_storingen.iloc[:-3, :]  # onderste 3 rijen zijn overbodig

# Lege dict voor alle storingen per maand. maand in storingen wordt dict (maand) in dict (storingen).
# maanden worden toegevoegd in notatie [maand]-[jaar]
storingen = {}

for col in storingen_data.iloc[:, 4:]:  # mask on df gives only the columns w/ month

    if storingen_data[col][0] == "Totaal":  # last column after the months in the df
        break
    else:
        # initialize empty dict for month
        if storingen_data[col][0] not in storingen:
            # todo: format maand-jaar notatie aanpassen
            storingen[storingen_data[col][0]] = {}  # Creates an empty dict w/ month as key in the storingen dict

        for index, row in storingen_data.iterrows():
            if row[col] is np.nan:  # If nan is seen => caught up to current date
                break
            elif index > 0 and int(row[col]) > 0:
                storingen[storingen_data[col][0]][row['SBS sub-systeem code']] = row[col]

# todo: Uit dict meldingen en dict storingen de lege maanden verwijderen

start_datum = get_first_key(meldingen)

json_dict = {"project": project,
             "start_datum": start_datum,
             "contact_info": contract_info,
             "meldingen": meldingen,
             "storingen": storingen}

with open(f'metadata//{project}_meta.json', 'w') as output_file:
    json.dump(json_dict, output_file)
