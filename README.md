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
# Class MetadataStoringsAnalyse
MetadataStoringsAnalyses supplies modules for manipulating the metadata that is used in the storingsanalyses.

## Initializing a new instance of the class
```
from metadata_storingsanalyse import MetadataStoringsAnalyse

metadata = MetadataStoringsAnalyse(path_to_metadata)
```

## Class attributes
- metadata.filepath
  
    - The filepath of the file

- metadata.filename

    - The filename of the file

- metadata.tijdsregistratie

    - Information extracted from the contract_info object in the metadata
    
## Modules

All the module names are presented with an instance of the class named *metdata*. 

Only the usable endpoints will be explained in this documentation. The private modules aren't going to be explained.

---
### *metdata*.get_all_data()

Returns the metadata object in the form of a table with a level 0 granularity.
	
|project|start_datum|contract_info|meldingen|storingen|
|-------|-----------|-------------|---------|---------|

---
### *metdata*.project()

Returns the name of hte project.

---
### *metdata*.startdate()

Returns the date at which the contract started.

---
### *metdata*.contract_info()

Returns the contract_info object as included in the metadata object. 
```
{
    tijdsregistratie: True,
    ...
}
```

---
### *metdata*.meldingen()

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
### *metdata*.storingen()

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
### *metdata*.get_di_dict(di, notification_type='meldingen')

Returns a filtered dictionary, only containing specified subsystem numbers.

#### Parameters
- **di** - one number, or a set of numbers to include in the returned dictionary

- **notification_type** - a specification of the dictionary that needs to be filtered ('meldngen' or 'storingen', default = 'meldingen'). 

---
### *metdata*.sum_values(dictionary, keys=None)

Sums up the values of a dictionary. If a dictionary of dictionaries is given, the module will continue to sum up all the values of the underlying dictionaries.

#### Parameters
- **dictionary** - a dictionary of which the values need to be summed.

- **keys** - one key, or a list of specific keys of which the values need to be summed (default = None). 

---
### *metdata*.count_values(dictionary, keys=None)

Counts the values of a dictionary. If a dictionary of dictionaries is given, the module will continue to count all the values of the underlying dictionaries.

#### Parameters
- **dictionary** - a dictionary of which the values need to be counted.

- **keys** - one key, or a list of specific keys of which the values need to be counted (default = None).

---
### *metdata*.avg_monthly(dictionary, keys=None)

Returns the calculated monthly average of the values of the dictionary.

#### Parameters
- **dictionary** - a dictionary of which the monthly average needs to be calculated.

- **keys** - one key, or a list of specific keys which need to be taken into account when calculating the monthly average (default = None).

---
### *metdata*.avg_yearly(dictionary, exclude_year=None)

Returns the calculated yearly average of the values of the dictionary.

#### Parameters
- **dictionary** - a dictionary of which the monthly average needs to be calculated.

- **exclude_year** - one year, or a list of years that need to be excluded from the calculation (default = None).

---
### *metdata*.get_month_list(notification_type='meldingen', exclude_month=None, exclude_year=None)

Returns a list of all the keys of a given dictionary that do not contain the specified months or years that need to be excluded.

#### Parameters

- **notification_type** - a specification of the dictionary that needs to be filtered ('meldngen' or 'storingen', default = 'meldingen').

- **exclude_month** - one month, or a list of months that need to be excluded (default = None).

- **exclude_year** - one year, or a list of years that need to be excluded (default = None).
