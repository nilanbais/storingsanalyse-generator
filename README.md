# storingsanalyse-generator
A repo dedicated to the development of a Notebook that generates the storingsanalyses done by the maintenance engineers.

This documentation also contains the a description of the MetadataStoringsAnalyse class that is used in calculating 
the results for the rapport. It gives an overview of the modules and attrubutes of the class and example of the usage 
of these modules and attributes.

# Project specific metadata
To grant the ability to analyse historical data of a given project, a new object needed to be designed. This object is 
build as presented bellow.
```
{
    "project": projectnaam,
    "start_datum": f"{maand}_{jaar}",
    "contract_info": {
        "tijdsregistratie": True,
        ...,
        "aanwezige_deelinstallaties": [lijst met aanwezige deelinstallaties op het project]
    },
    "poo_codes": {
        "probleem": {
            f"{maand}_{jaar}": {
                code: aantal meldingen,
                ...,
                "Leeg": aantal meldingen
            },
            f"{maand}_{jaar}": {
                ...
            },
        },
        "oorzaak": {
            f"{maand}_{jaar}": {
                code: aantal meldingen,
                ...,
                "Leeg": aantal meldingen
            },
            f"{maand}_{jaar}": {
                ...
            },
        },
        "oplossing": {
            f"{maand}_{jaar}": {
                code: aantal meldingen,
                ...,
                "Leeg": aantal meldingen
            },
            f"{maand}_{jaar}": {
                ...
            },
        },
    },
    "meldingen": {
        f"{maand}_{jaar}": {
            DI_num: aantal meldingen,
            DI_num: aantal meldingen
        }
        f"{maand}_{jaar}": {
            ...
        }
    },
    "storingen": {
        f"{maand}_{jaar}": {
            DI_num: aantal storingen,
            DI_num: aantal storingen
        }
        f"{maand}_{jaar}": {
            ...
        }
    }
}
```
---
---
# Classes
The backend is build using different Python classes, all dedicated to fulfill a specific piece of the process. These classes are summarized bellow and will be explained after that. In this explenation the focus will stay on the endpoints of the classes. Protected attributes and modules will only be explained when this is necessary.

|Class|Toepassing|
|-----|----------|
|QueryMaximoDatabase|Python Class dedicated to the query the IBM Maximo database and saving the received response.|
|MetadataStoringsAnalyse|Python Class for interacting with and manipulation of the metadata (read: historical data + added metadata of a project).|
|PrepNPlot|Python Class used for the preparation and plotting of the project specific data.|
|StagingFileBuilder|Python Class focussed on builing and saving a staging file in which the maintenance engineers can specify the category to which a notification belongs.|
|StoringsAnalyse|Python Class that combines the functionalities of the other classes that need to be applied and makes them available in the User Interface (Jupyter Notebook).|

---
# Class QueryMaximoDatabase

QueryMaximoDatabase is a python class dedicated to the query the IBM Maximo database and saving the received response.

## Initializing a new instance of the class

```
from query_maximo_database import QueryMaximoDatabase

qmdb = QueryMaximoDatabase(api_key)
```
## Class variables
A class variable is a variable defined inside a class. When making a new instance of this class, this new instance will also contain this variable.

- **_default_file_name** - The file name is build up like: date_hours_minutes_query_response_data.json, where date, hours, and minutes are substituted with the date and time of the moment the variable is used.

## Class attributes

- *qmdb*.api_key - the api_key to send with the request.
- *qmdb*.object_structure - the object structure of the response. (???)
- *qmdb*.site_id - a parameter used in the query. Corresponds to the siteid in the Maximo database.
- *qmdb*.response - saved last result (payload) of a query.
- *qmdb*.response_data - json object of the data received from the api-response.
- *qmdb*.url_parameters - a dictionary containing the url parameters used in querying the database.
- *qmdb*.headers - a dictionary containing the header data used in querying the database

## Class modules
### *qmdb*._get_response(query=None) - *protected module*
Sends a request to the database to get a response payload. If the parameter is None, it looks at the internal qmdb.query attribute to use as query.

#### Parameters
- **query** - A string containing the query that needs to be send to the database (default = None).
---
### *qmdb*.get_response_data(query=None)
Functionality of the *qmdb*.get_response(), but extended with the action of isolating the data from the response.

#### Parameters
- **query** - A string containing the query that needs to be send to the database (default = None).
---
### *qmdb*.save_response_data(filename=_default_file_name, query=None)
Functionality of the *qmdb*.get_response(), but extended with the isolation of the data from the response and saving this data.

#### Parameters
- **filename** - A string to specify a filename when saving the data (default=_default_file_name).
- **query** - A string containing the query that needs to be send to the database (default = None).
---
### *qmdb*._set_site_id(site_id) - *protected module*
Protected module to create the possibility of setting the site id class attribute after initializing the class-instance. It returns nothing.

#### Parameters
- **site_id** - The site_id you want to set as *qmdb*.site_id.
---
### *qmdb*._set_object_structure(object_structure='MXWO_SND')
Protected module to create the possibility of setting the object structure class attribute after initializing the class-instance. It returns nothing.

This module is executed at initialization of the class instance to set the default value as the object structure.

#### Parameters
- **object_structure** - The object_structure you want to set as *qmdb*.object_structure (default = 'MXWO_SND').
---
---
# Class MetadataStoringsAnalyse
MetadataStoringsAnalyses supplies modules for manipulating the metadata that is used in the storingsanalyses.

## Initializing a new instance of the class
```
from metadata_storingsanalyse import MetadataStoringsAnalyse

metadata = MetadataStoringsAnalyse(project)
```
## Class variables
A class variable is a variable defined inside a class. When making a new instance of this class, this new instance will also contain this variable.

- **_filepath_dict** - A dictionary with key: value pairs like {*project name*: *filename metafile of given project*}.

## Class attributes
- *metadata*.filepath - The filepath of the file. Based on the project name that is parsed when initializing a class instance the filepath can be extracted.
- *metadata*.filename - The name of the file. Set in the same process as *metadata*.filepath (set by a protected module of the class)
- *metadata*.tijdsregistratie - Information extracted from the contract_info object in the metadata.
    
## Class modules
All the module names are presented with an instance of the class named *metadata*. 

Only the usable endpoints will be explained in this documentation. The private modules aren't going to be explained.

---
### *metadata*.get_all_data()
Returns the metadata object in the form of a table with a level 0 granularity.
	
|project|start_datum|contract_info|meldingen|storingen|
|-------|-----------|-------------|---------|---------|

---
### *metadata*.project()
Returns the name of hte project.

---
### *metadata*.startdate()
Returns the date at which the contract started.

---
### *metadata*.contract_info()
Returns the contract_info object as included in the metadata object.
```
{
    tijdsregistratie: True,
    ...
}
```
---
### *metadata*.meldingen()
Returns the meldingen object as included in the metadata object.
```
{
    f"{maand}_{jaar}": {
        DI_num: aantal meldingen,
        DI_num: aantal meldingen
    }
    f"{maand}_{jaar}": {
        ...
    }
}
```
---
### *metadata*.storingen()
Returns the storingen object as included in the metadata object.
```
{
    f"{maand}_{jaar}": {
        DI_num: aantal storingen,
        DI_num: aantal storinge
    }
    f"{maand}_{jaar}": {
        ...
    }
}
```
---
### *metadata*.get_di_dict(di, notification_type='meldingen')
Returns a filtered dictionary, only containing specified subsystem numbers.

#### Parameters
- **di** - one number, or a set of numbers to include in the returned dictionary
- **notification_type** - a specification of the dictionary that needs to be filtered ('meldngen' or 'storingen', default = 'meldingen').
---
### *metadata*.sum_values(dictionary, keys=None)
Sums up the values of a dictionary. If a dictionary of dictionaries is given, the module will continue to sum up all the values of the underlying dictionaries.

#### Parameters
- **dictionary** - a dictionary of which the values need to be summed.
- **keys** - one key, or a list of specific keys of which the values need to be summed (default = None).
---
### *metadata*.count_values(dictionary, keys=None)
Counts the values of a dictionary. If a dictionary of dictionaries is given, the module will continue to count all the values of the underlying dictionaries.

#### Parameters
- **dictionary** - a dictionary of which the values need to be counted.
- **keys** - one key, or a list of specific keys of which the values need to be counted (default = None).
---
### *metadata*.avg_monthly(dictionary, keys=None)
Returns the calculated monthly average of the values of the dictionary.

#### Parameters
- **dictionary** - a dictionary of which the monthly average needs to be calculated.
- **keys** - one key, or a list of specific keys which need to be taken into account when calculating the monthly average (default = None).
---
### *metadata*.avg_yearly(dictionary, exclude_year=None)
Returns the calculated yearly average of the values of the dictionary.

#### Parameters
- **dictionary** - a dictionary of which the monthly average needs to be calculated.
- **exclude_year** - one year, or a list of years that need to be excluded from the calculation (default = None).
---
### *metadata*.get_month_list(notification_type='meldingen', exclude_month=None, exclude_year=None)
Returns a list of all the keys of a given dictionary that do not contain the specified months or years that need to be excluded.

#### Parameters
- **notification_type** - a specification of the dictionary that needs to be filtered ('meldngen' or 'storingen', default = 'meldingen').
- **exclude_month** - one month, or a list of months that need to be excluded (default = None).
- **exclude_year** - one year, or a list of years that need to be excluded (default = None).
---
---
# Class PrepNPlot
PrepNPlot contains modules for the preparation and plotting of the data obtained from the metadata.

## Initializing a new instance of the class
The methode of initializing a new class instance, as shown bellow, can be used with this class but it isn't necessary. 
Because of the way the StoringsAnalyse-class is build, a new instance of StoringsAnalyse inherits the attributes and 
modules from PrepNPlot. This makes these attributes and modules available as if they are part of the StoringsAnalyse-class.

```
from prepnplot import PrepNPlot

pp = PrepNPlot()
```
## Class variables
A class variable is a variable defined inside a class. When making a new instance of this class, this new instance will also contain this variable.

- **_quarters** - A set containing the term used for each quarter of the year ('Q1', 'Q2', 'Q3', 'Q4') with the corresponding months of the quarter.
- **_maand_dict** - A dictionary containing the month numbers as keys and written out name of the months as a value of the keys. One value per key.
- **_separator_set** - A set of the most common used separators.

## Class attributes
- *pp*.last_seen_bin_names - used to cashe the bin_names. Also makes it available to use this data outside of the class-instance.
- *pp*.quarter_sequence - A LinkedList that is used to return the previous or upcoming quarter. 

## Class modules
### *pp*.replace_seperator(string, inserting_seperator='-')
Returns the string were the seperator is substituted with the given seperator.

#### Parameters
- **string** - The string in which the separator needs to be substituted.
- **inserting_separator** - The seperator that is substitutes into the string (default='-')
---
### *pp*._get_bins(bin_size, time_range)
Returns a data structure like is shown bellow, with the given bin size over the given time range.

Note that this function doesn't support a bin size of a month. This is because in almost all the cases the data is already available in a structure that is ordered by month.
```
{'bin_1': [list of months belonging to the bin],
 'bin_2': [list of months belonging to the bin]}
```
#### Parameters
- **bin_size** - The bin size (either 'quarter' or 'year').
- **time_range** - A list with a start_date and an end_date (`[start_date, end_date]`). The dates used to define the time range NEED to have a month and year.
---
### *pp*._prep_time_range(time_range)
Returns list of datetime objects (`list([datetime, datetime])`) when given a list of strings (`list([str, str])`).

#### Parameters
- **time_range** - The time_range as a list of strings.
---
### *pp*._prep_time_range_base(time_range)
Returns a list with all the months between the start and end of the input time range.

#### Parameters
- **time_range** - The time_range as a list of datetime objects.
---
### *pp*._months_in_year_bin()
Returns a set of the months, build from the values of the _quarters dictionary.

---
### *pp*.prettify_time_label(label)
Returns a prettified string in which the separator is removed and the month number is substituted for the
written out month name ('03_2018' -> 'Maart 2018' and 'Q4_2020' -> 'Q4 2020')

#### Parameters
- **label** - The label that needs to be prettified.
---
### *pp*._transform_to_mate_structure(input_object, time_key, categorical_key)
Transforms a DataFrame to the structure of the metadata (like bellow).
```
    {month}_{year}": {
        category_1: count,
        category_2: count,
          ...     :  ... ,
        category_n: count
    }
```
#### Parameters
- **input_object** - The pandas.DataFrame() that needs to be changed.
- **time_key** - The name of the column containing the time.
- **categorical_key** - The name of the column that needs to be categorised and counted.
---
### *pp*.build_output_first_step(input_object, available_categories, bins)
Builds a dictionary with the following structure. Where n in the length of the available categories.
```
            {'key_1':
                {'key_11':
                    {key_111: value_111, key_112: value_112, ..., key_11n: value_11n},
                'key_12':
                    {key_121: value_121, key_122: value_122, ..., key_12n: value_12n},
                'key_13':
                    {key_131: value_131, key_132: value_132, ..., key_13n: value_13n}
                },
            'key_2':
                {'key_21':
                    {key_211: value_211, key_212: value_212, ..., key_21n: value_21n},
                'key_22':
                    {key_221: value_221, key_222: value_222, ..., key_22n: value_22n},
                'key_23':
                    {key_231: value_231, key_232: value_232, ..., key_23n: value_23n}
                     },
            'key_3':
                {'key_31':
                    {key_311: value_311, key_312: value_312, ..., key_31n: value_31n},
                'key_32':
                    {key_321: value_321, key_322: value_322, ..., key_32n: value_32n},
                'key_33':
                    {key_331: value_331, key_332: value_332, ..., key_33n: value_33n}
                     }
            }
```
#### Parameters
- **input_object** - The pandas.DataFrame() that needs to be changed.
- **available_categories** - The names of the available categories.
- **bins** - A result of *pp*._get_bins() as input.
---
### *pp*._prep_first_step(input_object, time_range, available_categories, bin_size=None)
Returns a dictionary with a structure like *pp*.build_output_first_step() builds.

#### Parameters
- **input_object** - A full dataset from which all the specific data is needed to be extracted or a dictionary containing the data.
- **time_range** - The time_range as a list of datetime objects.
- **available_categories** - The names of the available categories.
- **bin_size** - 'quarter' or 'year' (default = None). When None, the dictionary given as output will not contain any bins.
---
### *pp*._prep_second_step(input_dict)
This preparation action that changes the first structure to the later data structure, by adding
up the values of each third level key (key_1x1). Example: the values of key_111, key_121, key_131  of the input_dict would be added up and stored as key_11: value_11 in the
result.
```
        input_dict
            {'key_1':
                {'key_11':
                    {key_111: value_111, key_112: value_112, ..., key_11n: value_11n},
                'key_12':
                    {key_121: value_121, key_122: value_122, ..., key_12n: value_12n},
                'key_13':
                    {key_131: value_131, key_132: value_132, ..., key_13n: value_13n}
                },
            'key_2':
                {'key_21':
                    {key_211: value_211, key_212: value_212, ..., key_21n: value_21n},
                'key_22':
                    {key_221: value_221, key_222: value_222, ..., key_22n: value_22n},
                'key_23':
                    {key_231: value_231, key_232: value_232, ..., key_23n: value_23n}
                     },
            'key_3':
                {'key_31':
                    {key_311: value_311, key_312: value_312, ..., key_31n: value_31n},
                'key_32':
                    {key_321: value_321, key_322: value_322, ..., key_32n: value_32n},
                'key_33':
                    {key_331: value_331, key_332: value_332, ..., key_33n: value_33n}
                     }
            }
```
```
        result:
            {key_1: {key_11: value_11, key_12: value_12, ..., key_1n: value_1n},
             key_2: {key_21: value_21, key_22: value_12, ..., key_2n: value_2n},
             key_3: {key_31: value_31, key_32: value_32, ..., key_3n: value_3n}}
```
#### Parameters
- **input_dict** - The input dictionary (result of *pp*._prep_first_step()).
---
### *pp*._prep_end_step(input_dict, bin_names)
takes input data structure:
```
            {key_1: {key_11: value_11, key_12: value_12, ..., key_1n: value_1n},
             key_2: {key_21: value_21, key_22: value_12, ..., key_2n: value_2n},
             key_3: {key_31: value_31, key_32: value_32, ..., key_3n: value_3n}}
```
with:
- key_x - main level - these keys have to be unique. In a lot of cases the specified time like months or years 
- key_xy - second level - categorical data like the types of notifications of sbs numbers 
- value_xy - second level count - number of times key_xy is seen within time range key_x

returns data stucture:
```
            [[value_11, value_12, ..., value_1n],
             [value_21, value_22, ..., value_2n],
             [value_31, value_32, ..., value_3n]]
```
#### Parameters
- **input_dict** - The input dictionary (result of *pp*._prep_second_step()).
- **bin_names** - List with the unique main level values.
---
### *pp*._prep_end_step_summary(input_dict)
Module that counts the times a value has been seen in a bin. 

#### Parameters
- **input_dict** - The input dictionary (result of *pp*._prep_second_step()).

---
### *pp*.prep(input_object, time_range, available_categories, category_key=None, time_key=None, bin_size=False)
Module that combines the different preparation stages described above, with *pp*._prep_end_step() as last module applied

In case of parsing a pandas.DataFrame() it is necessary to parse a time_key and a category_key.

When no bin_size is parsed, the returned bin_size is 'monthly' (eq. the way it is stored in meta.)

#### Parameters
- **input_object** - A full pandas.DataFrame() or a dictionary containing the data.
- **time_range** - The time_range as a list of datetime objects.
- **available_categories** - The names of the available categories.
- **time_key** - The name of the column containing the time (default = None).
- **category_key** - The name of the column that needs to be categorised and counted (default = None).
- **bin_size** - 'quarter' or 'year' (default = None). When None, the dictionary given as output will not contain any bins (default = False).
---
### *pp*.prep_summary(input_object, time_range, available_categories, category_key=None, time_key=None, bin_size=False)
A variation of *pp*.prep(). The only difference is that *pp*._prep_end_step_summary() is applied as last step of the preparation.

#### Parameters
- **input_object** - A full pandas.DataFrame() or a dictionary containing the data.
- **time_range** - The time_range as a list of datetime objects.
- **available_categories** - The names of the available categories.
- **time_key** - The name of the column containing the time (default = None).
- **category_key** - The name of the column that needs to be categorised and counted (default = None).
- **bin_size** - 'quarter' or 'year' (default = None). When None, the dictionary given as output will not contain any bins (default = False).
---
### *pp*.plot(input_data, plot_type, category_labels, bin_labels)
Takes the result of *pp*.prep(), plots it, and returns a Figure object.

#### Parameters
- **input_data** - The input_data of the plot as a list of lists.
- **plot_type** - 'stacked' for a stacked bar-plot or 'side-by-side' for a plot with the bars plotted side by side.
- **category_labels** - The names of the different categories of the input.
- **bin_labels** - The labels of the bins (also available as attribute *pp*.last_seen_bin_names).
---
### *pp*.plot_summary(x_labels, data)
Takes the result of *pp*.prep_summary(), plots it, and returns a Figure object.

#### Parameters 
- **x_labels** - The names that need to be placed alongside the x-axis of the plot.
- **data** - The input data.
---
---
# Class StagingFileBuilder
MetadataStoringsAnalyses supplies modules for manipulating the metadata that is used in the storingsanalyses.

## Initializing a new instance of the class
```
from stagingfile_class import StagingFileBuilder

sfb = StagingFileBuilder(maximo_export_data_filename)
```

## Class variables
A class variable is a variable defined inside a class. When making a new instance of this class, this new instance will also contain this variable.

- **_ld_map_path** - The file path to the file 'location_destination_map.json'. This file is used internally in this class to gather the descriptions belonging to the different SBS and LBS numbers.
- **_default_file_name** - The file name is build up like: date_hours_minutes_staging_file.xlsx, where date, hours, and minutes are substituted with the date and time of the moment the variable is used.

## Class attributes
- *sfb*.input_file_name - (maximo_export_data_filename) Filename of the file used as input for building the staging file. The file used is the file containing the data from the maximo database, received through a query.
- *sfb*.export_file_name - Filename of the exported staging file.
- *sfb*.raw_data - Internal storage for the raw data obtained from the input file.
- *sfb*.asset_df - pandas.DataFrame() that contains the asset related data.
- *sfb*.workorder - pandas.DataFrame() that contains the workorder related data
- *sfb*.df_staging_file - pandas.DataFrame() that contains the result of merging the *sfb*.asset_df and *sfb*.workorder. 

## Class modules
### *sfb*.read_sf_data()
Module for reading the data from the input file and returning this data.

---
### *sfb*.get_breakdown_descriptions(sbs_lbs_series)
Returns the corresponding descriptions of the inserted series of SBS and/or LBS numbers.

#### parameters
- **sbs_lbs_seres** - pandas.Series() containing SBS or LBS numbers.  When you want to apply this function to a single value, parse this single value as a list.
---
### *sfb*.build_base_df()
Transforms the data in *sfb*.raw_data and builds the pandas.DataFrames *sfb*.asset_df and *sfb*.workorder.

---
### *sfb*.prep_staging_file_df()
Merges *sfb*.asset_df and *sfb*.workorder and stores the result as *sfb*.df_staging_file.

---
### *sfb*.save_staging_file()
Saves the pandas.DataFrame() stored as *sfb*.df_staging_file to a file with the name as specified by **_default_file_name**.

---
### *sfb*.build_staging_file()
Combines the main functionality of the class, so it can be executed with one call of a module.

---
---
# Class StoringsAnalyse
Python Class that combines the functionalities of the other classes that need to be applied and makes them available in the User Interface (Jupyter Notebook).

## Initializing a new instance of the class
```
from storingsanalyse import StoringsAnalyse

sa = StoringsAnalyse(project, api_key, object_structure)
```

## Class variables
A class variable is a variable defined inside a class. When making a new instance of this class, this new instance will also contain this variable.

- **_ld_map_path** - The file path to the file 'location_destination_map.json'. This file is used internally in this class to gather the descriptions belonging to the different SBS and LBS numbers.

## Class attributes
- *sa*.metadata - Instance of MetadataStoringsAnalyse().
- *sa*._maximo - Instance of QueryMaximoDatabase().
- *sa*.response_data - QueryMaximoDatabase().response_data.
- *sa*.filename_saved_response_data - QueryMaximoDatabase()._default_file_name.
- *sa*.staging_file_name - Name of the staging file.
- *sa*.staging_file_path - Path to the staging file.
- *sa*.staging_file_data - Data from the staging file.
- *sa*.meldingen - All the notifications obtained through the use of QueryMaximoDatabase().
- *sa*.storingen - All the notifications with type 'storing' obtained through the use of QueryMaximoDatabase().
- *sa*.project - Name of the given project, obtained from the metadata.
- *sa*.start_date - Start date of the given project, obtained from the metadata.

IMPORTANT - note that *sa*.metadata.meldingen() and *sa*.meldingen give two different results. Same goes for *sa*.metadata.storingen() and *sa*.storingen.

## Class modules
### *sa*.get_maximo_export(query=None)
See *qmdb*.get_response_data(query=None).

---
### *sa*.save_maximo_export(query=None)
See *qmdb*.save_response_data(filename=_default_file_name, query=None).

---
### *sa*.build_staging_file(maximo_export_data_filename)
See *sfb*.build_staging_file().

---
### *sa*.read_staging_file(filename)
Sets *sa*.staging_file_data to a pandas.DataFrame() filled with the data from the staging file.

#### Parameters
- **filename** - The filename of the staging file.
---
### *sa*.split_staging_file()
Splits the staging file in two and sets the correct pandas.Dataframes() to *sa*.meldingen and *sa*.storingen.

---
### *sa*.make_frequency_table(di_series)
Takes a pandas.Series() and returns a frequency table.

---

