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
    project: projectnaam,
    start_datum: dd-mm-yyy,
    contract_info: {
        tijdsregistratie: True,
        ...
    },
    meldingen: {
        f"{maand}_{jaar}": {
            DI_num: aantal meldingen,
            DI_num: aantal meldingen
        }
        f"{maand}_{jaar}": {
            ...
        }
    },
    storingen: {
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
|StagingFileBuilder|Python Class focussed on builing and saving a staging file in which the maintenance engineers can specify the category to which a notification belongs.|
|StoringsAnalyse|Python Class that combines the functionalities of the other classes that need to be applied and makes them available in the User Interface (Jupyter Notebook).|

---
# Class QueryMaximoDatabase

QueryMaximoDatabase is a python class dedicated to the query the IBM Maximo database and saving the received response.

## Initializing a new instance of the class

```
from query_maximo_database import QueryMaximoDatabase

qmdb = QueryMaximoDatabase(api_key, object_structure)
```
## Class variables
A class variable is a variable defined inside a class. When making a new instance of this class, this new instance will also contain this variable.

- **_default_file_name** - The file name is build up like: date_hours_minutes_query_response_data.json, where date, hours, and minutes are substituted with the date and time of the moment the variable is used.. 

## Class attributes

- *qmdb*.api_key - the api_key to send with the request.
- *qmdb*.object_structure - the object structure of the response. (???)
- *qmdb*.query - saved query, if any has been given in the process.
- *qmdb*.response - saved last result (payload) of a query.
- *qmdb*.response_data - json object of the data received from the api-response.

## Class modules
### *qmdb*.get_response(query=None)
Sends a request to the database to get a response payload. If the parameter is None, it looks at the internal qmdb.query attribute to use as query.

#### Parameters
- **query** - A string containing the query that needs to be send to the database (default = None).
---
### *qmdb*.get_response_data(query=None)
Functionality of the *qmdb*.get_response(), but extended with the isolation of the data from the response.

#### Parameters
- **query** - A string containing the query that needs to be send to the database (default = None).
---
### *qmdb*.save_response_data(filename=_default_file_name, query=None)
Functionality of the *qmdb*.get_response(), but extended with the isolation of the data from the response and saving this data.

#### Parameters
- **filename** - A string to specify a filename when saving the data (default=_default_file_name).
- **query** - A string containing the query that needs to be send to the database (default = None).
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

