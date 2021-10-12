# storingsanalyse-generator
A repo dedicated to the development of a Notebook that generates the storingsanalyses done by the maintenance engineers.

This documentation also contains the a description of the MetadataStoringsAnalyse class that is used in calculating 
the results for the rapport. It gives an overview of the methods and attrubutes of the class and example of the usage 
of these methods and attributes.

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
        aanwezige_deelinstallaties: [Lijst DI_nummers],
        POO_codes: [Lijst POO codes]
    },
    poo_codes: {
        probleem: {
            "{kwartaal}_{jaar}": {
                POO_code: aantal meldingen,
                POO_code: aantal meldingen,
            }
        },
        oorzaak: {
                [structuur als in probleem]
            }
        },
        oplossing: {
                [structuur als in probleem]
            }
        }
    },
    meldingen: {
        "{maand}_{jaar}": {
            DI_num: aantal meldingen,
            DI_num: aantal meldingen
        }
        "{maand}_{jaar}": {
            ...
        }
    },
    storingen: {
        "{maand}_{jaar}": {
            DI_num: aantal storingen,
            DI_num: aantal storingen
        }
        "{maand}_{jaar}": {
            ...
        }
    }
}
```
---
---
# Classes
The backend is build using different Python classes, all dedicated to fulfill a specific piece of the process. These classes are summarized bellow and will be explained after that. In this explenation the focus will stay on the endpoints of the classes. Protected attributes and methods will only be explained when this is necessary.

|Class|Toepassing|
|-----|----------|
|QueryMaximoDatabase|Python Class dedicated to the query the IBM Maximo database and saving the received response.|
|MetadataStoringsAnalyse|Python Class for interacting with and manipulation of the metadata (read: historical data + added metadata of a project).|
|PrepNPlot|Python Class used for the preparation and plotting of the project specific data.|
|StagingFileBuilder|Python Class focussed on builing and saving a staging file in which the maintenance engineers can specify the category to which a notification belongs.|
|StoringsAnalyse|Python Class that combines the functionalities of the other classes that need to be applied and makes them available in the User Interface (Jupyter Notebook).|
|DocumentGenerator|Pyhon Class for generating the documentens (text + appendix).|

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

This class doesn't contain any class variables.

## Class attributes

- *qmdb*.api_key - the api_key to send with the request.
- *qmdb*.object_structure - the object structure of the response. (???)
- *qmdb*.site_id - a parameter used in the query. Corresponds to the siteid in the Maximo database.
- *qmdb*.response - saved last result (payload) of a query.
- *qmdb*.response_data - json object of the data received from the api-response.
- *qmdb*.url_parameters - a dictionary containing the url parameters used in querying the database.
- *qmdb*.headers - a dictionary containing the header data used in querying the database

## Class methods
### *qmdb*._get_response(query=None) - *protected method*
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
### *qmdb*.set_site_id(site_id) - *protected method*
Protected method to create the possibility of setting the site id class attribute after initializing the class-instance. It returns nothing.

#### Parameters
- **site_id** - The site_id you want to set as *qmdb*.site_id.
---
### *qmdb*.set_object_structure(object_structure='MXWO_SND')
Protected method to create the possibility of setting the object structure class attribute after initializing the class-instance. It returns nothing.

This method is executed at initialization of the class instance to set the default value as the object structure.

#### Parameters
- **object_structure** - The object_structure you want to set as *qmdb*.object_structure (default = 'MXWO_SND').
---
---
# Class MetadataStoringsAnalyse
MetadataStoringsAnalyses supplies methods for manipulating the metadata that is used in the storingsanalyses.

## Initializing a new instance of the class
```
from metadata_storingsanalyse import MetadataStoringsAnalyse

metadata = MetadataStoringsAnalyse(project)
```
## Class variables
A class variable is a variable defined inside a class. When making a new instance of this class, this new instance will also contain this variable.

- **_filepath_dict** - A dictionary with key: value pairs like {*project name*: *filename metafile of given project*}.
- **_quarters** - A dictionary with key: value pairs like {*quarter name*: *list of corresponding months*}.

## Class attributes
- *metadata*.filepath - The filepath of the file. Based on the project name that is parsed when initializing a class instance the filepath can be extracted.
- *metadata*.tijdsregistratie - Information extracted from the contract_info object in the metadata.
- *metadata*._quarter - Internal storage for remembering the quarter of the analysis that is being executed.
- *metadata*._year - Internal storage for remembering the year of the analysis that is being executed.
- *metadata*.unsaved_updated_meta - space to hold the updated metadata before it is saved to longtime storage.
    
## Class methods
All the method names are presented with an instance of the class named *metadata*. 

Only the usable endpoints will be explained in this documentation. The private methods aren't going to be explained.

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
        DI_num: aantal storingen
    }
    f"{maand}_{jaar}": {
        ...
    }
}
```
---
### *metadata*.poo_data()
Returns the poo_codes object as included in the metadata object.
```
{
    probleem: {
        "{kwartaal}_{jaar}": {
            POO_code: aantal meldingen,
            POO_code: aantal meldingen,
        }
    },
    oorzaak: {
            [structuur als in probleem]
        }
    },
    oplossing: {
            [structuur als in probleem]
        }
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
Sums up the values of a dictionary. If a dictionary of dictionaries is given, the method will continue to sum up all the values of the underlying dictionaries.

#### Parameters
- **dictionary** - a dictionary of which the values need to be summed.
- **keys** - one key, or a list of specific keys of which the values need to be summed (default = None).
---
### *metadata*.count_values(dictionary, keys=None)
Counts the values of a dictionary. If a dictionary of dictionaries is given, the method will continue to count all the values of the underlying dictionaries.

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
### *metadata*.avg_quarterly(dictionary)
Returns the calculated quarterly average of the values of the dictionary.

#### Parameters
- **dictionary** - a dictionary of which the quarterly average needs to be calculated.
---
### *metadata*.avg_yearly(dictionary, exclude_year=None)
Returns the calculated yearly average of the values of the dictionary.

#### Parameters
- **dictionary** - a dictionary of which the monthly average needs to be calculated.
- **exclude_year** - one year, or a list of years that need to be excluded from the calculation (default = None).
---
### *metadata*.get_month_list(notification_type='meldingen', exclude_month=None, exclude_quarter=None, exclude_year=None)
Returns a list of all the keys of a given dictionary that do not contain the specified months or years that need to be excluded.

#### Parameters
- **notification_type** - a specification of the dictionary that needs to be filtered ('meldngen' or 'storingen', default = 'meldingen').
- **exclude_month** - one month, or a list of months that need to be excluded (default = None).
- **exclude_quarter** - one quarter, or a list of quarters that need to be excluded (default = None).  
- **exclude_year** - one year, or a list of years that need to be excluded (default = None).
---
### *metadata*.filter_dictionary_keys(dictionary, keys)
Returns a dict filtered to only contain the specified keys.

#### Parameters
- **dictionary** - the dictionary that needs to be filtered.
- **keys** - the specified keys on which the dictionary needs to be filtered.
---
### *metadata*._quarter_to_month_number(quarters)
Returns a list containing the months corresponding to the given quarters.

#### Parameters
- **quarters** - a quarter, or a list of quarters of which the corresponding months need to be returned.
---
### *metadata*._order_frequency_table(freq_table)
Returns an ordered dict, ordered by the size of the values in the dictionary.

#### Parameters
- **freq_table** - the frequency_table that needs to be ordered.
---
### *metadata*.make_ddict_frequency_table(dictionary)
Returns a frequency table of the values of the input dictionary.

#### Parameters
- **dictionary** - the input dictionary of which a frrequency table is made.
---
### *metadata*.poo_avg_table(poo_dictionary, poo_type)
Return returns a table with the averages of the frequencies of the POO codes.

#### Parameters
- **poo_dictionary** - the full dictionary corresponding to a poo_type in the matadata object.
- **poo_types** - one of the poo_types (probleem, oorzaak, oplossing) of which the averages table needs to be created.
---
### *metadata*.return_poo_type_string(poo_type)
Returns the poo_type string 'probleem code', 'oorzaak code', or 'oplossing code' based on the poo_type.

#### Parameters
- **poo_type** - one of the poo_types (probleem, oorzaak, oplossing).
---
### *metadata*.return_poo_code_letter(poo_type)
Returns the poo_type letter 'P', 'C', or 'S' based on the poo_type.

#### Parameters
- **poo_type** - one of the poo_types (probleem, oorzaak, oplossing).
---
### *metadata*.return_poo_code_list(poo_type)
Returns all the available codes corresponding to a poo_type.

#### Parameters
- **poo_type** - one of the poo_types (probleem, oorzaak, oplossing).
---
### *metadata*.return_ntype_meta_object(ntype)
Returns a dictionary containing only the specified notification type (ntype).

#### Parameters
- **ntype** - the notification type (available ntypes in the method are: 'meldingen' and 'storingen')
---
### *metadata*.update_poo_data(staging_file_data)
Returns a dictionary that is extended with the new prepared poo data extracted from the database in the process of building the analysis.

#### Parameters
- **staging_file_data** - a pandas.DataFrame containing the prepared data for the analysis.
---
### *metadata*.update_ntype_data(staging_file_data, ntype)
Returns a dictionary that is extended with the new prepared notification type data extracted from the database in the process of building the analysis.

#### Parameters
- **staging_file_data** - a pandas.DataFrame containing the prepared data for the analysis.
- **ntype** - the notification type (available ntypes in the method are: 'meldingen' and 'storingen')
---
### *metadta*.update_meta(staging_file_data)
Method that updates the poo data, meldingen and storingen, and saves the result in the attribute *metadta*.unsaved_updated_meta.

#### Parameters
- **staging_file_data** - a pandas.DataFrame containing the prepared data for the analysis.
---
---
# Class PrepNPlot
PrepNPlot contains methods for the preparation and plotting of the data obtained from the metadata.

## Initializing a new instance of the class
The methode of initializing a new class instance, as shown bellow, can be used with this class but it isn't necessary. 
Because of the way the StoringsAnalyse-class is build, a new instance of StoringsAnalyse inherits the attributes and 
methods from PrepNPlot. This makes these attributes and methods available as if they are part of the StoringsAnalyse-class.

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

## Class methods
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
### *pp*._month_num_to_name(month_num)
Returns the writen out month name of the corresonding month number.

#### Parameters
- **monnth_num** - A single month number, or a list of month numbers.
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
Method that counts the times a value has been seen in a bin. 

#### Parameters
- **input_dict** - The input dictionary (result of *pp*._prep_second_step()).
---
### *pp*.filter_prep_output(list_of_lists, available_categories)
This method filers the prep_output to return a modified copy of the list_of_lists (LOL) and the list of
corresponding available categories, where all the categories of which all the values in the LOL are '0'
are filtered out. Both the objects NEED TO BE sorted and stay in that order.

IMPORTANT

The list with the available categories needs to be sorted. The function build_output_first_step takes
the available categories and sorts them when using them. This means that the list of lists created is
in the order of the sorted available categories.

#### Parameters
- **list_of_lists** - the list of lists to the values corresponding to the available categories.
- **available_categories** - a list of all the available categories in the list_of_lists.
---
### *pp*.prep(input_object, time_range, available_categories, category_key=None, time_key=None, bin_size=False)
Method that combines the different preparation stages described above, with *pp*._prep_end_step() as last method applied

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
MetadataStoringsAnalyses supplies methods for manipulating the metadata that is used in the storingsanalyses.

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

## Class methods
### *sfb*.read_sf_data()
Method for reading the data from the input file and returning this data.

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
Combines the main functionality of the class, so it can be executed with one call of a method.

---
---
# Class StoringsAnalyse
Python Class that combines the functionalities of the other classes that need to be applied and makes them available in the User Interface (Jupyter Notebook).

## Initializing a new instance of the class
How to create a new instance of the class is shown bellow. In this creation, the specification of the staging_file_name is optional (default = None). 
```
from storingsanalyse import StoringsAnalyse

sa = StoringsAnalyse(project, api_key, rapport_type, quarter, year, staging_file_name = None)
```
StoringsAnalyse is a child class of PrepNPlot, meaning it inherits all the attributes and methods from it's parent class (PrepNPlot).
It will be explicitly mentioned when an attribute or method is overridden by an attribute or method of StoringsAnalyse.

## Class variables
A class variable is a variable defined inside a class. When making a new instance of this class, this new instance will also contain this variable.

- **_ld_map_path** - The file path to the file 'location_destination_map.json'. This file is used internally in this class to gather the descriptions belonging to the different SBS and LBS numbers.
- **_default_file_name_maximo** - The default filename used when saving the raw data received from the maximo server.

## Class attributes
- *sa*.metadata - Instance of MetadataStoringsAnalyse().
- *sa*.project - Name of the given project, obtained from the metadata.  
- *sa*.project_start_date - Start date of the given project, obtained from the metadata.
- *sa*.quarter - Quarter of the current analysis.  
- *sa*.year - Year of the current analysis.
- *sa*.prev_quarter - The previous quarter, seen from the current quarter.
- *sa*.prev_year - The previous year, seen from the current year.
- *sa*.metadata._quarter - The attribute is set for internal use of the quarter in the MetadataStoringsAnalyse().
- *sa*.metadata._year - The attribute is set for internal use of the year in the MetadataStoringsAnalyse().
- *sa*.analysis_time_range - The timerange of the analysis.
- *sa*.analysis_start_date - The start date of the analysis.
- *sa*.analysis_end_date - The end date of the analysis.
- *sa*._maximo - Instance of QueryMaximoDatabase().
- *sa*.response_data - copy of the value of QueryMaximoDatabase.response_data in StoringsAnalyse.
- *sa*.filename_saved_response_data - The filename of the saved maximo response data (default = None and is set by method *sa*.save_maximo_response_data()).
- *sa*.staging_file_name - Name of the staging file.
- *sa*.meldingen - All the notifications obtained through the use of class QueryMaximoDatabase (default = None and is set by *sa*.split_staging_file()).
- *sa*.storingen - All the notifications with type 'storing' obtained through the use of class QueryMaximoDatabase (default = None and is set by *sa*.split_staging_file()).
- *sa*.staging_file_path - Path to the staging file (default = None and is set by *sa*.init_staging_file()).
- *sa*.staging_file_data - Data from the staging file (default = None and is set by *sa*.init_staging_file()).
- *sa*.rapport_type - Specification if the rapport is a quarterly analysis or a yearly analysis.
- *sa*.graphs - An attribute to hold all the graphs that are created.

IMPORTANT - note that *sa*.metadata.meldingen() and *sa*.meldingen give two different results. Same goes for *sa*.metadata.storingen() and *sa*.storingen.

## Class methods
### *sa*.return_ntype_staging_file_object(ntype)
Returns a pandas.DataFrame object containing records with the specified notification type (ntype).

#### Parameters
- **ntype** - The notification type that is needed to be isolated (options are 'meldingen', 'stroingen', 'onterecht',
  'preventief', 'incident').
---
### *sa*.get_min_max_month(notificaions_groupby_month, min_max)
Returns a list with the names of the month or months that correspond to the maximum or minimum number of notifications.

#### Parameters
- **notifications_groupby_month** - a dictionary of the notifications grouped by the month in which they were reported.
- **min_max** - Specification of if the returned value needs to be the minimum or maximum (using 'min' or 'max').
---
### *sa*.get_time_range()
Method that returns the time range of the current quarter. It returns it in the form of and start and end datetime 
object in a list. 

#### Parameters
None

---
### *sa*._get_time_range(quarter)
Method that returns the time range of a given quarter. the quarter needs to be specified in the form 'Qx', with x being
the number of the quarter.

#### Parameters
- **quarter** - A string representing the one of the four quarters.
---
### *sa*.compare_quarters(curr_quarter, prev_quarter)
Compares the current and previous quarter to see if the previous quarter is at the end of the previous year. This
method returns true when the previous quarter is larger than the current quarter ('Q4' > 'Q1' -> True ).

#### Parameters
- **curr_quarter** - The string notation of the current quarter.
- **prev_quarter** - The string notation of the previous quarter.
---
### *sa*.get_time_range_v2(mode)
Method that returns different time ranges depending on the mode that is specified.

Mode:
  - 'pc' - Mode returns the time range from beginning previous quarter to end of the current quarter.

#### Parameters
- **mode** - Mode for retrieving the time range

---
### *sa*.sbs_patch(project)
Patch for the different notations of the sbs numbers.

---
### *sa*.query_maximo_database(site_id, work_type = 'COR')
Method to query the maximo database. The method builds the query with the use of the site_id and the work type, and 
*sa*.analysis_time_range. The received response will be saved in the attribute *sa*.response_data.

#### Parameters
- **site_id** - id code to specify the site of which the data is needed to be received.
- **work_type** - a short code to specify the type of records that need to be extracted from the database (default = 'COR').
---
### *sa*.save_maximo_response_data(filename = _default_file_name_maximo)
Saves the response data as a .json-file. 

#### Parameters
- **filename** - The filename of the under which the data is stored (default = _default_file_name_maximo).
---
### *sa*.build_query(site_id, report_time, work_type = 'COR')
Returns a string with the correct query that is needed to extract the data from the maximo database.

#### Parameters
- **site_id** - id code to specify the site of which the data is needed to be received.
- **report_time** - A list containing the datetime object of the start date and end date of the analysis.  
- **work_type** - a short code to specify the type of records that need to be extracted from the database (default = 'COR').
---
### *sa*.init_staging_file(staging_file_name = None)
Method for the initialization steps of the staging_file related attributes.

#### Parameters
- **staging_file_name** - name of the staging file that is needed to be importen/read (default = None).
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
### *sa*.update_meta()
Method to extend the metadata with the staging_file data. The staging_file name needs to be known before calling this 
method, otherwise it will raise an error.

---
### *sa*._add_graph_for_export(figure)
Method that adds the given figure to the attribute *sa*.graphs.

### Parameters
- **figure** - The figure object.
---
### *sa*.plot(input_data, plot__type, category_labels, bin_labels, title, show_plot = False)
This method overrides PrepNPlot.plot().
Method that combines the method PrepNPlot.plot() with *sa*._add_graph_for_export()

---
### *sa*.plot_summary(x_labels, data, title, show_plot = False)
This method overrides PrepNPlot.plot_summary().
Method that combines the method PrepNPlot.plot_summary() with *sa*._add_graph_for_export()

---
### *sa*.export_graphs(filename)
Method that create a pdf-file containing the graphs added to *sa*.graphs

#### Parameters
- **filename** - The filename of the saved file.
---
---
# Class DocumentGenerator
Python class on top of StoringsAnalyse, dedicated to generating the text document and appendix.

## Initializing a new instance of the class
How to create a new instance of the class is shown bellow. In this creation, the specification of the staging_file_name 
is optional (default = None).
```
from document_generator import DocumentGenerator

dg = DocumentGenerator(project, rapport_type, quarter, year, api_key, staging_file_name = None)
```

## Class variables
This class doesn't have any class variables.

## Class attributes
- *dg*.sa - Instance of StornigsAnalyse().
- *dg*.newline - Pre-defined string for a new line.
- *dg*.tab - Pre-defined string for ra tab.
- *dg*._default_export_file_name - The pre-defined file name for the text document.
- *dg*._default_export_file_name_appendix - The pre-defined file name for the appendix.
- *dg*._default_export_location - The pre-defined path to the folder where the documents need to be stored.

## Class methods
### *dg*.build_table_docx(docx_object, header, row_data)
Method that builds a table in the input docx_object, using the headers as column names and the row_data as data to fill
the table.

#### Parameters
- **docx_object** - The docx_object to which all the text is added.
- **headers** - A tuple containing the column names, in order.
- **row_data** - Data of the rows.
---
### *dg*.del_old_export()
Deletes an older file from a previous export.

#### Parameters
None

---
### *dg*.get_aantal_per_maand(ntype)
Returns the amount of notifications for each month of the specified notification type.

#### Parameters
- **ntype** - Notification type. Options are: 'meldingen', 'storingen', 'onterecht', 'preventief', and 'incident'.
---
### *dg*.build_text_aantal_per_maand(input_dict)
Returns a multiline string containing the text that needs to be added.

#### Parameters
- **input_dict** - A dictionary containing the different data that is needed to generate the text.
---
### *dg*.get_quarter_comparison(ntype)
Method to calculate the data needed, adds them to a data dictionary and returns this dictionary.

#### Parameters
- **ntype** - Notification type. Options are: 'meldingen', 'storingen', 'onterecht', 'preventief', and 'incident'.
---
### *dg*.build_quarter_comparison(input_data_dict)
Returns a multiline string containing the text that needs to be added.

#### Parameters
- **input_data_dict** - A dictionary containing the different data that is needed to generate the text.
---
### *dg*.get_aantal_per_subsystem(ntype, threshold)
Method to calculate the data needed, adds them to a data dictionary and returns this dictionary.

#### Parameters
- **ntype** - Notification type. Options are: 'meldingen', 'storingen', 'onterecht', 'preventief', and 'incident'.
- **threshold** - Value of the minimum amount of totifications needed to be added in the text.
---
### *dg*.build_text_aantal_per_subsysteem(input_data_dict)
Returns a multiline string containing the text that needs to be added.

#### Parameters
- **input_data_dict** - A dictionary containing the different data that is needed to generate the text.
---
### *dg*.get_aantal_per_subsysteem(ntype, threshold)
Method to calculate the data needed, adds them to a data dictionary and returns this dictionary.

#### Parameters
- **ntype** - Notification type. Options are: 'meldingen', 'storingen', 'onterecht', 'preventief', and 'incident'.
- **threshold** - Value of the minimum amount of totifications needed to be added in the text.
---
### *dg*.build_text_aantal_per_subsysteem(input_data_dict)
Returns a multiline string containing the text that needs to be added.

#### Parameters
- **input_data_dict** - A dictionary containing the different data that is needed to generate the text.
---
### *dg*.build_conclusie_algemeen_intro()
Returns a multiline string containing the text that needs to be added.

#### Parameters
None

---
### *dg*.get_poo_table_data_md(poo_type)
Retrieves/collects the data for the poo table in a way that is compatible wit the method that builds the markdown 
style table. Method returns a data_dict.

#### Parameters
- **poo_type** - The type of POO data which applies to the text. Options are: 'probleem', 'oorzaak' and 'oplossing'.
---
### *dg*.get_poo_table_data_v2(poo_type)
Retrieves/collects the data for the poo table in a way that is compatible wit the method that builds the docx style 
table.

#### Parameters
- **poo_type** - The type of POO data which applies to the text. Options are: 'probleem', 'oorzaak' and 'oplossing'.
---
### *dg*.build_poo_type_table(input_data, docx_object)
Method that builds a POO table in the input docx_object, using the headers as column names and the row_data as data 
to fill the table.

#### Parameters
- **docx_object** - The docx_object to which all the text is added.
- **input_data** - Data of the rows.
---
### *dg*.get_aantal_per_subsysteem_per_maand(threshold, ntype = 'storingen')
Method to calculate the data needed, adds them to a data dictionary and returns this dictionary.

#### Parameters
- **ntype** - Notification type. Options are: 'meldingen', 'storingen', 'onterecht', 'preventief', and 'incident' 
  (default = 'storingen').
- **threshold** - Value of the minimum amount of totifications needed to be added in the text.
---
### *dg*.build_aantal_per_subsysteem_per_maand(input_data_dict)
Returns a multiline string containing the text that needs to be added.

#### Parameters
- **input_data_dict** - A dictionary containing the different data that is needed to generate the text.
---
### *dg*.get_asset_meeste_ntype_algemeen(threshold, ntype = 'meldingen')
Method to calculate the data needed, adds them to a data dictionary and returns this dictionary.

#### Parameters
- **ntype** - Notification type. Options are: 'meldingen', 'storingen', 'onterecht', 'preventief', and 'incident' 
  (default = 'meldingen').
- **threshold** - Value of the minimum amount of totifications needed to be added in the text.
---
### *dg*.build_asset_meeste_ntype_algemeen(input_data_dict)
Returns a multiline string containing the text that needs to be added.

#### Parameters
- **input_data_dict** - A dictionary containing the different data that is needed to generate the text.
---
### *dg*.get_asset_meeste_ntype_algemeen_v2(threshold, ntype = 'meldingen')
Method to calculate the data needed, adds them to a data dictionary and returns this dictionary.

#### Parameters
- **ntype** - Notification type. Options are: 'meldingen', 'storingen', 'onterecht', 'preventief', and 'incident' 
  (default = 'meldingen').
- **threshold** - Value of the minimum amount of totifications needed to be added in the text.
---
### *dg*.build_asset_meeste_ntype_algemeen_v2(input_data, docx_object)
Method that builds a table in the input docx_object, using the headers as column names and the row_data as data 
to fill the table.

#### Parameters
- **docx_object** - The docx_object to which all the text is added.
- **input_data** - Data of the rows.
---
### *dg*.get_asset_uitwerking_ntypes(threshold, ntype = 'meldingen')
Method to calculate the data needed, adds them to a data dictionary and returns this dictionary.

#### Parameters
- **ntype** - Notification type. Options are: 'meldingen', 'storingen', 'onterecht', 'preventief', and 'incident' 
  (default = 'meldingen').
- **threshold** - Value of the minimum amount of notifications needed to be added in the text.
---
### *dg*.build_asset_uitwerking_ntypes(input_data_dict)
Returns a multiline string containing the text that needs to be added.

#### Parameters
- **input_data_dict** - A dictionary containing the different data that is needed to generate the text.
---
### *dg*.build_asset_uitwerking_ntypes_v2(input_dict, docx_paragraph_object, docx_object)
The version 2 method combines the calculation of the data and writing the data to the docx_object.

#### Parameters
- **input_data_dict** - A dictionary containing the different data that is needed to generate the text. 
- **docx_paragraph_object** - A paragraph object specific to the python-docx package.
- **docx_object** - The docx_object to which all the text is added.

### *dg*.build_asset_conclusie(input_dict)
Method to generate the text.

#### Parameters
- **input_data_dict** - A dictionary containing the different data that is needed to generate the text.

### *dg*.build_full_document(threshold = 3)
Method for building the whole text document.

#### Parameters
- **threshold** - Value of the minimum amount of notifications needed to be added in the text (default = 3).

### *dg*.build_appendix(threshold = 0)
Method for building the appendix document.

#### Parameters
- **threshold** - Value of the minimum amount of notifications needed to be added in the appendix (default = 0).
