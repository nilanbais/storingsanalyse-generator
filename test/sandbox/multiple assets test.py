import json
import os
import string
from datetime import datetime as dt

import numpy as np
import pandas as pd

from mapped_attribute_names import workorder_attribute_names as wan, asset_attribute_names as aan, dt_attributes,\
    locations_attibute_names as lan



def switch_key_val(dictionary):
    """
    Switches the key: val to val: key of the given dictionary
    :param dictionary:
    :return:
    """
    return {dictionary[key]: key for key in dictionary.keys()}


def get_sub_to_leftjoin(dataset, column, attributes_to_extract):
    """
    This function returns a specific set of attributes of a still-to-unfold nested json.
    :param dataset: pd.DataFrame without any nan values
    :param column: specific column with the nested json
    :param attributes_to_extract: attributes to extract from the nested json (has to be a subset of the attributes
    of the neste json. else function won't work.
    :return: pd.DataFrame with the specific attributes and the corresponding indexes
    """
    # List of indexes of the specific rows that hadn't had a np.nan value
    indexes = []
    # Initializing empty df
    unfolded_json = pd.DataFrame()
    # Iterate over the rows of the df
    for index, row in dataset.iterrows():
        # Appending the specific index to add to the result later (before returning)
        indexes.append(index)
        # Unfolding the nested json in two steps (one step gave an error)
        unfolded_row = pd.json_normalize(row[column])
        unfolded_json = unfolded_json.append(unfolded_row)

    # Copying the attributes that need to be returned from the unfolded_json df
    # copy() to isolate data in a new df + SettingWithCopy warning
    result = unfolded_json[[x for x in attributes_to_extract]].copy()
    # Adding the specific indexes of the input dataset and setting it as df index
    result.loc[:, 'index'] = indexes
    # result.set_index(keys='index', inplace=True)

    return result


def clean_dt_object(dt_object):
    """
    Het kan zijn dat de %z voor de tijdzone niet wordt herkend in andere os (mac-os/linux). op de jupyter server is
    dt_object = dt_object.split('+')[0] toegevoegd om dit op te lossen.
    :param dt_object:
    :return:
    """
    try:
        raw_dt_object = dt.strptime(dt_object, '%Y-%m-%dT%H:%M:%S%z')
        clean_object = raw_dt_object.replace(tzinfo=None)
        clean_object = dt.strftime(clean_object, '%d-%m-%y %H:%M:%S')
    except ValueError:
        clean_object = dt_object
    finally:
        return clean_object


def get_month_number(dt_object):
    """
    Automation of extracting the number of the month in the dt_object that has been adjusted by clean_dt_object() and
    has the form dd-mm-yy hours:min:sec
    :param dt_object:
    :return:
    """
    try:
        raw_dt_object = dt.strptime(dt_object, '%d-%m-%y %H:%M:%S')
        month_num = raw_dt_object.month
    except ValueError:
        month_num = ''
    finally:
        return month_num


def update_description(map_dict, suffix):
    """
    Updates the description with the specufied suffix in the mapped dict used to assign readable column names
    in the staging file.
    :param map_dict:
    :param suffix:
    :return:
    """
    for key in map_dict.keys():
        if map_dict[key] == 'description':
            map_dict[key] = map_dict[key] + suffix


# Data inlezen
test_file = 'raw_json_payload(modified).json'
input_data_file = test_file
with open(input_data_file, 'r') as input_file:
    data = json.load(input_file)

# Omschrijvingen tabel inlezen
resource_file = 'location_description_map.json'
rel_path = f'..\\..\\res\\{resource_file}'
with open(rel_path, 'r') as r:
    resource_data = json.load(r)

# DataFrame van de data maken en de kolomnamen isoleren in var
data_df = pd.DataFrame(data)
data_attributes = data_df.columns

# Adding index to data_df for the upcoming join
data_df['index'] = data_df.index

# Creating list variables of the different attributes that need to be extracted
wo_attributes = [wan[x] for x in wan.keys()]
asset_attributes = [aan[x] for x in aan.keys()]
location_attributes = [lan[x] for x in lan.keys()]

# Creating the workorder df with an index column
workorder = data_df.loc[:, wo_attributes].copy()
workorder.loc[:, 'index'] = workorder.index
"""
TOELICHTING:
De op te bouwen data set moet voor assetnum, sbs en locatie twee of meerdere waarnden bevatten (hier uitgaande van twee)
Er wordt een lijst met indexen van waar assetnum niet leeg is. We kunnen ervan uitgaan dat asset data is meegegeven 
in de regels waar assetnum niet leeg is.
"""
# Creating raw versions of the df to use as input in the function
raw_asset_df = data_df.loc[data_df['asset'].notna(), ['asset']]
raw_locations_df = data_df.loc[data_df['locations'].notna(), ['locations']]

# Todo: Onderstaande tot functie maken
"""
Elke index in raw_asset_df bevestigd dat er len(raw_asset_df.loc[i, 'asset']) asset nummers aanwezig zijn.
"""
# Initializing an empty df
asset_df = pd.DataFrame()
# Adding a attribute to the list of attributes to extract
asset_attributes.append("assetnum")
# Iterating over the nested json in the asset column
for index, row in raw_asset_df.iterrows():
    # Appointing the first and second asset number to their own value
    asset_num1 = workorder.at[index, wan['asset nummer']] if workorder.at[index, wan['asset nummer']] != "" else np.NaN
    asset_num2 = workorder.at[index, wan['asset nummer 2']] if workorder.at[index, wan['asset nummer 2']] != "" else np.NaN

    # Making a list consisting of the asset numbers that are not nan
    not_nan_asset_nums = [aa for aa in [asset_num1, asset_num2] if not pd.isnull(aa)]

    """
    Because we first filter out all the rows were no asset number is present, we can assume with certainty that each
    row of the raw_asset_df contains at least one nested json (data of one asset number). If more than one asset number 
    is given, the length of row['asset'] will be the same as the amount of asset numbers given.
    """
    # Unfolding the first nested json w/ asset data
    flattened_row = pd.json_normalize(row['asset'][0])

    # Extracting the attributes that need to be extracted and adding the index as col,val to the result df
    result = flattened_row[[x for x in asset_attributes]].copy()
    result.loc[:, 'index'] = index

    # Initializing an empty dataframe with the columns of the asset_attributes too include the datapoints of the second
    # asset number, even if no second number is given
    empty_frame = pd.DataFrame({'gmblocation': [""], 'description': [""], 'location': [""], 'assetnum': [""]})

    # Remove the extracted asset number from the list of not nan asset numbers
    not_nan_asset_nums.remove(flattened_row['assetnum'].values)

    # Check if there is another asset number given
    if len(not_nan_asset_nums) == 0:
        to_add = empty_frame.copy()
        # Adding the index to merge the to_add df to the result df (result of the first nested json)
        to_add.loc[:, 'index'] = index
    else:
        # Unfolding the second nested json w/ asset data
        flattened_row = pd.json_normalize(row['asset'][-1])
        # Extracting the attributes (same as above to gather the result df)
        to_add = flattened_row[[x for x in asset_attributes]].copy()
        to_add.loc[:, 'index'] = index

    # Merging the to_add df to the result df on the added index-column
    asset_row = result.merge(to_add, on='index', suffixes=('_asset1', '_asset2'))

    # Adding the merged row w/ asset data to asset_df
    asset_df = asset_df.append(asset_row)
