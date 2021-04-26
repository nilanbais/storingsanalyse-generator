"""
This script is used to generate a staging_file in which the maintenance engineers have to set a value manually.
A dictionary is used for the mapping of the attribute names based on the names of the columns in the staging_file and
the report
"""
import json

import pandas as pd
import xlsxwriter as xlsx
import os
from mapped_attribute_names import workorder_attribute_names as wan, asset_attribute_names as aan, \
    locations_attibute_names as lan, all_attribute_names as man

# Changing current working dir to the src folder
while 1:
    if os.getcwd().endswith('src'):
        break
    else:
        os.chdir('..')

# Data inlezen
input_data_file = 'raw_json_payload.json'
with open(input_data_file, 'r') as input_file:
    data = json.load(input_file)

# DataFrame van de data maken en de kolomnamen isoleren in var
data_df = pd.DataFrame(data)
data_attributes = data_df.columns


wo_attributes = [wan[x] for x in wan.keys()]
asset_attributes = [aan[x] for x in aan.keys()]
location_attributes = [lan[x] for x in lan.keys()]


print([att for att in data_attributes if att not in wo_attributes])
"""
Volgende stap is om te kijken of er nog data uitgepakt moeten worden en hoe dit er vervolgens uit gaat zien.
Let hierbij op of het beter op ruwe json data gedaan kan worden of dat het ook uit een df kan. Maak er één groot df
van.
Vervolgens moet er gekeken worden hoe een staging_file zo snel mogeiljk gegenereerd kan worden uit de opgestelde df
Daarbij natuurlijk belangrik dat de kolom voor het manueel invullen van de data bij de verwante kolommen staat (gemak).
Voeg in deze dataset ook al de maand als geïsoleerde waarde in een kolom toe om de maintenance engineers gerust te 
stellen dat deze wel is meegenomen.
"""



# workbook = xlsx.Workbook('test_w_list.xlsx')
# worksheet = workbook.add_worksheet('main')
#
# worksheet.write_column('D1', ['List data', 'open', 'high', 'close'])
#
# txt = 'Select a value from a drop down list'
#
# worksheet.write('A1', txt)
# worksheet.data_validation('B1', {'validate': 'list', 'source': ['open', 'high', 'close']})
#
# workbook.close()
