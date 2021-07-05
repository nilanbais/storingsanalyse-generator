"""
Class for building the staging file.

Because the use of a staging file is a temporary solution, we build the Staging File Builder with a robust
architecture. It's gonna be deleted in a future update.

This script is used to generate a staging_file in which the maintenance engineers have to set a value manually.
A dictionary is used for the mapping of the attribute names based on the names of the columns in the staging_file and
the report
"""
import json
import os
import string
from datetime import datetime as dt

import numpy as np
import pandas as pd

# from mapped_attribute_names import workorder_attribute_names as wan, asset_attribute_names as aan, dt_attributes
# from mapped_attribute_names import staging_file_columns1 as new_col_order

"""
This file contains a dictionary of the names as given to the columns and the corresponding attribute name as used
in the Maximo Database. In theory this as to make it easier to change to code generating the report straight from
the source without the use of a staging_file in which the maintenance engineers have to manually set the value of
a column.
Attribute names are NOT given in a table.column lay-out (only the column name is given)
"""

# MAN (Mapped Attribute Names)
"""
Alle velden waar geen comment bij staan om een tabel te specificeren, behoren tot de Workorder tabel
"""
# workorder_attribute_names
wan = {"werkorder": "wonum",
         "status": "status",
         "rapport datum": "reportdate",
         "werkorder beschrijving": "description",
         "asset nummer": "assetnum",
         "asset nummer 2": "assetnum2",
         "probleem code": "problemcode",
         "beschrijving probleem": "gmbctschcodering8",
         "oorzaak code": "fr1code",
         "beschrijving oorzaak": "gmbctschcodering9",
         "oplos code": "fr2code",
         "oplossing beschrijving": "gmb_solution",
         "uitgevoerde werkzaamheden": "gmbctschcodering17",
         "tijdstip monteur ter plaatse": "gmbctschcodering24",
         "streefdatum start": "targstartdate",
         "geplande start": "schedstart",
         "werkelijke start": "actstart",
         "tijdstip einde werkzaamheden": "actfinish",
         "tijdstip afmelding": "gmbctschcodering35",
         "tijdstip validatie": "gmbctschcodering33",
         "funcitoneel herstel": "gmbctschcodering36",
         "definitief herstel": "gmbctschcodering37",
         "is financieel nadeel": "gmbisfinnadeel",
         "gmblocation3": "gmblocation3",
         "gemeld asset": "gmb_gemeldasset",
         "vestiging": "siteid"
         }

# asset_attribute_names
aan = {"sbs": "gmblocation",
         "asset beschrijving": "description",
         "locatie": "location",
         # "sbs2": "gmblocation2",
         # "asset beschrijving 2": "description",
         # "locatie 2": "location2"
         }

"""
van onderstaande is de eerste gesorteerd per 1 of 2 
de tweede is gesorteerd per data (assetnum 1&2, sbs 1&2 enz.)
"""
staging_file_columns1 = ['werkorder', 'status', 'rapport datum', 'werkorder beschrijving',
                         'asset nummer', 'asset beschrijving', 'sbs', 'sbs omschrijving', 'locatie', 'locatie omschrijving',
                         'asset nummer 2', 'asset beschrijving 2', 'sbs 2', 'sbs 2 omschrijving', 'locatie 2', 'locatie 2 omschrijving',
                         'probleem code', 'beschrijving probleem', 'oorzaak code', 'beschrijving oorzaak', 'oplos code', 'oplossing beschrijving', 'uitgevoerde werkzaamheden',
                         'tijdstip monteur ter plaatse', 'streefdatum start', 'geplande start', 'werkelijke start',
                         'tijdstip einde werkzaamheden', 'tijdstip afmelding', 'tijdstip validatie',
                         'funcitoneel herstel', 'definitief herstel', 'is financieel nadeel', 'gmblocation3',
                         'gemeld asset', 'vestiging']

staging_file_columns2 = ['werkorder', 'status', 'rapport datum', 'werkorder beschrijving',
                         'asset nummer', 'asset beschrijving', 'asset nummer 2', 'asset beschrijving 2',
                         'sbs', 'sbs omschrijving', 'sbs 2', 'sbs 2 omschrijving',
                         'locatie', 'locatie omschrijving', 'locatie 2', 'locatie 2 omschrijving',
                         'probleem code', 'beschrijving probleem', 'oorzaak code', 'beschrijving oorzaak', 'oplos code',
                         'oplossing beschrijving', 'uitgevoerde werkzaamheden', 'tijdstip monteur ter plaatse',
                         'streefdatum start', 'geplande start', 'werkelijke start', 'tijdstip einde werkzaamheden',
                         'tijdstip afmelding', 'tijdstip validatie', 'funcitoneel herstel', 'definitief herstel',
                         'is financieel nadeel', 'gmblocation3', 'gemeld asset', 'vestiging']

# defining new_col_order
new_col_order = staging_file_columns1

# dt_attributes contains every attribute that contains a datetime object AND ISN'T reportdate
dt_attributes = ['gmbctschcodering24', 'targstartdate', 'schedstart', 'actstart', 'actfinish',
                 'gmbctschcodering35', 'gmbctschcodering33', 'gmbctschcodering36', 'gmbctschcodering37']


# todo: OPTIE Documentatie schrijven voor class
class StagingFileBuilder:

    # Class variables (callable by using class_name.var_name)
    _ld_map_path = "..\\..\\res\\location_description_map.json"  # location_description_map
    _default_file_name = f"{str(dt.now().date()).replace('-', '')}_{str(dt.now().time().hour)}_{str(dt.now().time().minute)}_staging_file.xlsx"

    # Initializing standard variables
    suffixes = ['_asset1', '_asset2']

    def __init__(self, maximo_export_data_filename):
        self.input_file_name = maximo_export_data_filename
        self.export_file_name = None

        self._ld_map = self._read_ld_map()

        self.raw_data = self.read_sf_data()
        self._col_index_type_melding = None

        self.asset_df = pd.DataFrame()
        self.workorder = None
        self.df_staging_file = pd.DataFrame()

    @staticmethod
    def _switch_key_val(dictionary):
        """
        Switches the key: val to val: key of the given dictionary
        :param dictionary:
        :return:
        """
        return {dictionary[key]: key for key in dictionary.keys()}

    @staticmethod
    def _clean_dt_object(dt_object):
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

    @staticmethod
    def _get_month_number(dt_object):
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

    @staticmethod
    def _update_description(map_dict, suffix):
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

    @staticmethod
    def _read_ld_map():
        """
        Module to load the data for the descriptions of the location breakdown structure numbers (LBS) and the system
        breakdown structure numbers (SBS).
        :return:
        """
        with open(os.path.relpath(StagingFileBuilder._ld_map_path), 'r') as file:
            description_data = json.load(file)
        return pd.DataFrame(description_data)

    def _get_breakdown_description(self, sbs_lbs):
        description = [self._ld_map.loc[str(index), 'description']
                       for index in range(self._ld_map.shape[0])
                       if sbs_lbs == self._ld_map.loc[str(index), 'location']]
        return description if len(description) > 0 else [""]  # To cover empty rows

    def get_breakdown_descriptions(self, sbs_lbs_series):
        description_list = [self._get_breakdown_description(sbs_lbs) for sbs_lbs in sbs_lbs_series]
        return description_list

    @staticmethod
    def _del_suffix(dictionary):
        def clean_key(a): return a.replace('_asset1', '') if '1' in a else a.replace('_asset', ' ')

        new_dictionary = {clean_key(key): dictionary[key] for key in dictionary.keys()}
        return new_dictionary

    def read_sf_data(self):
        with open(f"..\\staging file\\{self.input_file_name}", 'r') as input_file:
            data = json.load(input_file)
        return data

    def build_base_df(self):
        """
        Module for building the base dataframe of the staging file. the base dataframe isn't anything more than
        the maximo export data without any nested json
        :return:
        """
        # DataFrame van de data maken en de kolomnamen isoleren in var
        data_df = pd.DataFrame(self.raw_data)

        # Adding index to data_df for the upcoming join
        data_df['index'] = data_df.index

        # Creating list variables of the different attributes that need to be extracted
        asset_attributes = [aan[x] for x in aan.keys()]

        # Creating the workorder df with an index column
        self.workorder = data_df.loc[:, [wan[x] for x in wan.keys()]].copy()
        self.workorder.loc[:, 'index'] = self.workorder.index

        # Creating raw versions of the df to use as input in the function
        raw_asset_df = data_df.loc[data_df['asset'].notna(), ['asset']]

        # Iterating over the nested json in the asset column
        for index, row in raw_asset_df.iterrows():
            # Appointing the first and second asset number to their own value
            asset_num1 = self.workorder.at[index, wan['asset nummer']] if self.workorder.at[index, wan['asset nummer']] != "" else np.NaN
            asset_num2 = self.workorder.at[index, wan['asset nummer 2']] if self.workorder.at[index, wan['asset nummer 2']] != "" else np.NaN

            # Making a list consisting of the asset numbers that are not nan
            not_nan_asset_nums = [aa for aa in [asset_num1, asset_num2] if not pd.isnull(aa)]

            """
            Because we first filter out all the rows were no asset number is present (to build raw_asset_df), we can now say 
            with certainty that each row of the raw_asset_df contains at least one nested json (data of one asset number). If 
            more than one asset number is given, the length of row['asset'] will be the same as the amount of asset numbers given.
            """
            # Unfolding the first nested json w/ asset data
            flattened_row = pd.json_normalize(row['asset'][0])

            # Extracting the attributes that need to be extracted and adding the index as col,val to the result df
            result = flattened_row[[x for x in asset_attributes]].copy()
            result.loc[:, 'index'] = index

            # Initializing an empty dataframe with the columns of the asset_attributes too include the datapoints of the second
            # asset number, even if no second number is given
            # empty_frame = pd.DataFrame({'gmblocation': [""], 'description': [""], 'location': [""], 'assetnum': [""]})
            empty_frame = pd.DataFrame({'gmblocation': [""], 'description': [""], 'location': [""]})

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
            asset_row = result.merge(to_add, on='index',
                                     suffixes=(StagingFileBuilder.suffixes[0],
                                               StagingFileBuilder.suffixes[-1]))  # suffix resp. _asset1, _asset2

            # Adding the merged row w/ asset data to asset_df
            self.asset_df = self.asset_df.append(asset_row)

        return "Done."

    def prep_staging_file_df(self):
        """
        Module for preping the base dataframe to a dataframe that can be exported as staging file.
        It contains getting the descriptions of the sbs/lbs numbers, cleaning some data, and preping column names to
        a uniform form so they can be used to build the staging file.
        :return:
        """
        self.asset_df = self.asset_df.reset_index().drop(columns='level_0')

        # Creating a new version of the asset_attributes map_dict
        new_aan = {}
        for att in self.asset_df.columns:
            split = att.split('_')
            key = [x + "_" + split[-1] for x in aan.keys() if aan[x] == split[0]]
            if len(key) > 0:
                new_aan[key[-1]] = att

        # Creating the map_dict for the sbs/lbs descriptions
        description_attribute_names = {}
        for suffix in StagingFileBuilder.suffixes:
            self.asset_df.loc[:, aan['sbs'] + "_description" + suffix] = self.get_breakdown_descriptions(self.asset_df[aan['sbs'] + suffix])
            self.asset_df.loc[:, aan['locatie'] + "_description" + suffix] = self.get_breakdown_descriptions(self.asset_df[aan['locatie'] + suffix])

            description_attribute_names['sbs' + suffix + ' omschrijving'] = aan['sbs'] + "_description" + suffix
            description_attribute_names['locatie' + suffix + ' omschrijving'] = aan['locatie'] + "_description" + suffix

        # Deleting the suffixes from the keys of the dictionaries
        new_aan = self._del_suffix(new_aan)
        description_attribute_names = self._del_suffix(description_attribute_names)

        # Merging the workorder df, the asset df, and the locations df to one big df that can be used as base for the
        # data that has to be included in the staging_file.xlsx
        self.df_staging_file = self.workorder.copy().merge(self.asset_df, how='left', on='index', suffixes=('', ''))

        # # Updating the values in the map dicts
        # update_description(map_dict=aan, suffix='_asset')

        # Cleaning the df by dropping the added index column and filling the np.nan values with ""
        self.df_staging_file.drop(labels='index', axis=1, inplace=True)
        self.df_staging_file.fillna(value="", inplace=True)

        # Rearranging the df to make it look familiar (like the export the maintenance engineers get from IBM Maximo)
        # col_list = df_staging_file.columns.tolist()
        col_dict = dict(wan, **new_aan, **description_attribute_names)

        self.df_staging_file = self.df_staging_file.loc[:, [col_dict[x] for x in new_col_order]]

        # Adding a column just containing the number of the month AND cleaning the way df['reportdate'] is presented
        datetime_objects = []
        month_nums = []
        for i in self.df_staging_file['reportdate']:
            # Appending the cleaned presentation of the datetime object
            datetime_objects.append(self._clean_dt_object(i))
            # Appending the number of the month
            month_nums.append(self._get_month_number(self._clean_dt_object(i)))

        # Assigning clean dt objects to the report time column
        self.df_staging_file.loc[:, 'reportdate'] = datetime_objects
        # Inserting the number of the month as a new column at the right of the reportdate column
        self.df_staging_file.insert(loc=(self.df_staging_file.columns.get_loc('reportdate') + 1),
                                    column='month_number',
                                    value=month_nums)

        # Cleaning all the other datetime objects
        for att in dt_attributes:
            # Getting list of cleaned dt objects of the att column
            clean_dt_list = [self._clean_dt_object(self.df_staging_file.at[index, att]) for index in
                             range(self.df_staging_file.shape[0])]
            # Changing the old values for the cleaned values
            self.df_staging_file.loc[:, att] = clean_dt_list

        # Switching keys and values of the dict to get a var to rename the columns of df_staging_file
        new_col_names = self._switch_key_val(col_dict)
        # Renaming df_staging_file
        self.df_staging_file = self.df_staging_file.rename(new_col_names, axis='columns')

        # Assigning the index of the new column to a var (will reuse this val in the generation of the staging file)
        # + 2 because of the index that is also printed with the dataframe
        self._col_index_type_melding = self.df_staging_file.columns.get_loc('uitgevoerde werkzaamheden') + 1
        # Adding empty column for the dropdown list
        self.df_staging_file.insert(loc=self._col_index_type_melding,
                                    column='type melding (Storing/Incident/Preventief/Onterecht)',
                                    value=([str()] * len(self.df_staging_file.index))
                                    )

        return "Done."

    def save_staging_file(self):
        """
        Module for saving the staging file. It also adds the dropdown for the list for inserting the different types
        of notifications.
        :return:
        """
        filename = StagingFileBuilder._default_file_name if self.export_file_name is None else self.export_file_name
        export_path = f'..\\staging file\\{filename}'

        letters = list(string.ascii_uppercase)

        # Setting up the writer
        writer = pd.ExcelWriter(export_path, engine='xlsxwriter')

        # Setting up the workbook
        workbook = writer.book

        # Adding the DataFrame to a new sheet called 'Sheet1'
        self.df_staging_file.to_excel(writer, sheet_name='Sheet1', index=False)

        # Assigning the new sheet to a variable form future references
        worksheet = writer.sheets['Sheet1']

        # Adding a backend sheet
        backend = workbook.add_worksheet('Backend')

        # Adding format
        text_format = workbook.add_format({'text_wrap': True})

        # Writing the values of the dropdown list to the backend sheet
        options_list = ['Storing', 'Incident', 'Preventief', 'Onterecht', 'N.V.T.']
        backend.write_column('A1', options_list)

        # Setting up a dynamic variable for the options of data_validation
        options_ref = f'={backend.name}!$A$1:$A${len(options_list)}'

        # Initializing var end_row for later reference
        end_row = self.df_staging_file.shape[0]

        # Iterating over the length of data in the file and adding a dropdown list to the cells
        for i in range(2, end_row + 2):
            worksheet.data_validation(f'{letters[self._col_index_type_melding]}{i}',
                                      options={'validate': 'list', 'source': options_ref})

        # Hiding all unused rows and setting row heights
        worksheet.set_default_row(height=30, hide_unused_rows=True)
        worksheet.set_row(0, 15)

        # Assigning format for textwrapping
        text_wrap_format = workbook.add_format({'text_wrap': True})

        # Adjusting the width of the columns
        for index, column in enumerate(self.df_staging_file):
            # Isolating the column
            series = self.df_staging_file[column]
            # Extracting he max length needed a column
            max_len = max((series.astype(str).map(len).max(), len(str(series.name)))) + 1  # Adding some extra space
            # Assigning threshold value for the max length
            max_len = 66 if max_len > 66 else max_len
            # Setting the new width of the column
            worksheet.set_column(index, index, max_len, cell_format=text_wrap_format)

        # Freezing the column names in the staging file to enhance the comfort of working with the file
        worksheet.freeze_panes(row=1, col=0)

        workbook.close()
        return f"Staging file saved as {filename} in the folder 'staging file'."

    def build_staging_file(self):
        self.build_base_df()
        self.prep_staging_file_df()
        self.export_file_name = self._default_file_name  # freezing name because of the date and time in the name
        self.save_staging_file()


if __name__ == '__main__':

    sfb = StagingFileBuilder(maximo_export_data_filename='raw_json_payload.json')
    sfb.build_base_df()

    sfb.prep_staging_file_df()

    sfb.save_staging_file()
