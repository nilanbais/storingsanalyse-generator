"""
This script is for the development of the functions to use on the metadata.
Building some sort of layer on top op the standardized lay-out of the metadata makes working with the data in
a Jupyter Notebook easier and more organized.

The functions are written for a json metadata file generated by the metadata_file builder
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


Fucnties/Modules die geschreven moeten worden, zijn:
    -   [x] het opvragen van het gemiddelde aantal meldingen per maand, per jaar
    -   [x] het opvragen van het aantal meldingen in een gegeven maand, een gegeven jaar
    -   [x] module voor het filteren van meldingen of storingen op een te kiezen di nummer
    -   [ ] module voor het updaten en opslaan van de nieuw gegenereerde metadata
"""
import json
import pandas as pd
import numpy as np
# Todo: ONDERSTAANDE AANPASSING STERK OVERWEGEN
"""
Aanpassing:
Wanneer de bovenstaande objectstructuur voor meer dan alleen een storingsanalyse wordt toegepast, is het misschien
beter om een splitsing te maken. een dergelijke splitsing zal dan gemaakt moeten worden tussen de metadata
objectstructuur met de modules die een abstracte bewerking doen op de data (count_values & sum_values) en de bewerkingen
die een type specifieke bewerking doen (alles met storingsanalyse specifieke handelingen).
"""
# Todo: class uitbreiden met de isolatie van de mogelijke di nummers die worden gebruikt in het project


# todo: documentatie aanpassen
class MetadataStoringsAnalyse:

    _filepath_dict = {"Coentunnel-tracé": "metadata_file_coentunnel-tracé.json",
                      "Sluis Eefde": "metadata_file_sluis_eefde.json"}

    def __init__(self, project):
        self.filepath = self._get_filepath(project=project)

        self.tijdsregistratie = self.contract_info()["tijdsregistratie"]  # true or false

    def _get_filepath(self, project):
        _filename = [MetadataStoringsAnalyse._filepath_dict[key]
                     for key in MetadataStoringsAnalyse._filepath_dict.keys()
                     if project.lower() in key.lower()]

        if len(_filename) > 1:
            raise ValueError(f"Found too many files using the given project {project}. \nResults: {_filename} ")

        self.filename = _filename[0]

        rel_filepath = "..\\metadata\\" + self.filename
        return rel_filepath

    def _read_json(self):
        with open(self.filepath, 'r') as json_file:
            _data = json.load(json_file)
        return _data

    def get_all_data(self):
        data = pd.json_normalize(data=self._read_json(), max_level=0)
        return data

    def project(self):
        meta = self.get_all_data()
        return meta["project"][0]

    def startdate(self):
        meta = self.get_all_data()
        return meta["start_datum"][0].replace('_', '-')

    def contract_info(self):
        meta = self.get_all_data()
        return meta["contract_info"][0]

    def meldingen(self):
        meta = self.get_all_data()
        return meta["meldingen"][0]

    def storingen(self):
        meta = self.get_all_data()
        return meta["storingen"][0]

    def get_di_dict(self, di, notification_type='meldingen'):
        """
        Module to filter the dict provided by self.meldingen() or self.storingen() on a specific di number.
        :param notification_type: specification which of the two dict to use. dtype=string
        :param di: number of the deelinstallatie (subsystem). dtype=int or string
        :return: filtered dictionary
        """
        dictionary = self.meldingen() if str(notification_type).lower() in ['m', 'melding', 'meldingen'] \
            else self.storingen() if str(notification_type.lower()) in ['s', 'storing', 'storingen'] \
            else False

        if not dictionary:
            raise ValueError(f"Incorrect input value given: {notification_type}. Please choose one of the following notification types: 'meldingen', 'storingen'.")

        di_set = {di}  # {di} makes a set of di. set(di) gave different result

        result_dict = {date_key: dictionary[date_key][sub_system]
                       for date_key in dictionary.keys()
                       for sub_system in dictionary[date_key].keys() if sub_system in di_set}

        if result_dict == {}:
            print(f"Can't find sub_system '{di_set}' in the metadata.")

        return result_dict

    @staticmethod
    def _check_first_element(dictionary):
        if isinstance(dictionary, dict):
            first_element = [dictionary[key] for key in dictionary.keys()][0]
        elif isinstance(dictionary, list):
            first_element = [dictionary[key] for key in range(len(dictionary))]
        else:
            first_element = np.nan

        return first_element

    def _sum_all_values(self, dictionary):
        """
        Takes a dictionary and sums up all the values found in the dictionary.
        If given a dictionary of dictionaries, it will return the sum of all the values of the underlying
        dictionaries.
        :param dictionary:
        :return:
        """
        first_element = self._check_first_element(dictionary=dictionary)
        if isinstance(first_element, dict):
            return sum([self._sum_all_values(dictionary[key]) for key in dictionary.keys()])

        return sum([dictionary[key] for key in dictionary.keys()])

    def sum_values(self, dictionary, keys=None):

        if keys is None:
            return self._sum_all_values(dictionary)

        # check if keys is a list. If not, change it to list
        keys = [keys] if not isinstance(keys, list) else keys

        first_element = self._check_first_element(dictionary=dictionary)

        # if first element is int while keys are given
        if isinstance(first_element, int):
            dictionary = {key: dictionary[key] for key in keys}
            return sum([self._sum_all_values(dictionary)])

        # return sum of specific keys from dict
        return sum([self._sum_all_values(dictionary[key]) for key in dictionary.keys() if key in keys])

    def _count_all_values(self, dictionary):
        """
        Takes a dictionary and counts the number of keys found in the dictionary.
        If given a dictionary of dictionaries, it will returns number of keys found in the top layer of the
        dictionary.
        :param dictionary:
        :return:
        """
        first_element = self._check_first_element(dictionary=dictionary)

        if isinstance(first_element, dict):
            return len([self._count_all_values(dictionary[key]) for key in dictionary.keys()])

        return len([dictionary[key] for key in dictionary.keys()])

    def count_values(self, dictionary, keys=None):
        if keys is None:
            return self._count_all_values(dictionary)
        # check if keys is a list. If not, change it to list
        keys = [k for k in keys] if not isinstance(keys, list) else keys
        # return sum of specific keys from dict
        return len([self._count_all_values(dictionary[key]) for key in dictionary.keys() if key in keys])

    def avg_monthly(self, dictionary, keys=None):
        summed_values = self.sum_values(dictionary=dictionary, keys=keys)
        counted = self.count_values(dictionary=dictionary, keys=keys)
        return summed_values / counted

    @staticmethod
    def _sort_keys_by_year(dictionary, exclude_year=None):
        """
        Sorts the keys of the given dictionary by years. It returns a new dictionary with setup
        {year: [keys containing year]}
        :param dictionary:
        :param exclude_year:
        :return: dict with build {year: [keys containing year]}
        """
        result_dict = {}
        for datum in dictionary.keys():
            jaar = datum.split('_')[-1]
            if (exclude_year is not None) and jaar in (exclude_year if isinstance(exclude_year, list) else [exclude_year]):
                continue
            else:
                if jaar in result_dict:
                    result_dict[jaar].append(datum)
                else:
                    result_dict[jaar] = [datum]
        return result_dict

    def avg_yearly(self, dictionary, exclude_year=None):
        """
        Module calulates the yearly average number of notifications.
        :param dictionary:
        :param exclude_year:
        :return:
        """
        sorted_keys = self._sort_keys_by_year(dictionary=dictionary, exclude_year=exclude_year)
        # Bellow gives a list like [avg_year_1, avg_year_2, ... , avg_year_n]
        notifications_per_year = [self.sum_values(dictionary=dictionary, keys=sorted_keys[year]) for year in sorted_keys.keys()]
        if len(notifications_per_year) == 0:
            return int(0)

        return sum(notifications_per_year) / len(notifications_per_year)

    def get_month_list(self, notification_type='meldingen', exclude_month=None, exclude_year=None):
        """
        Returns the list of all the keys that do not contain the specified excluded month or year.
        :param notification_type: specification of the dictionary to get the keys from. default=self.meldingen()
        :param exclude_month: When parsing multiple values, parse them in a list. [excluded_month_1, ... ,excluded_month_n]
        :param exclude_year: same as exclude_month.
        :return:
        """
        dictionary = self.meldingen() if str(notification_type).lower() in ['m', 'melding', 'meldingen'] \
            else self.storingen() if str(notification_type.lower()) in ['s', 'storing', 'storingen'] \
            else False

        if not dictionary:
            raise ValueError(f"Incorrect input value given: {notification_type}. Please choose one of the following notification types: 'meldingen', 'storingen'.")

        _set_months = exclude_month if isinstance(exclude_month, list) \
            else [exclude_month] if exclude_month is not None \
            else []
        _set_years = exclude_year if isinstance(exclude_year, list) \
            else [exclude_year] if exclude_year is not None \
            else []

        if _set_months == [] and _set_years == []:  # no values given to exclude
            return [key for key in dictionary.keys()]
        elif _set_months == [] and _set_years != []:  # no month given
            return [key for key in dictionary.keys() for _sy in _set_years if key.split('_')[-1] not in _sy]
        elif _set_months != [] and _set_years == []:  # no year given
            return [key for key in dictionary.keys() for _sm in _set_months if key.split('_')[0] not in _sm]
        else:  # both year and month given
            return [key for key in dictionary.keys() for _sm in _set_months for _sy in _set_years
                    if (key.split('_')[0] not in _sm and key.split('_')[-1] not in _sy)]


if __name__ == '__main__':
    import os
    while 1:
        if os.getcwd().endswith('storingsanalyse-generator'):
            break
        else:
            os.chdir('..')

    project = 'coentunnel'
    metadata = MetadataStoringsAnalyse(project)

    meldingen = metadata.meldingen()
    storingen = metadata.storingen()

    m = metadata.sum_values(meldingen)
    s = metadata.sum_values(storingen)  # sum of all values found in the dicts of dicts

    data2019 = [key for key in storingen.keys() if '2019' in key]
    oktober = [key for key in meldingen.keys() if "10" in key[:3]]

    aantal_storingen_2019 = metadata.sum_values(dictionary=storingen, keys=data2019)  # 166
    aantal_meldingen_maart_2018 = metadata.sum_values(dictionary=meldingen, keys='03_2018')  # 27
    lijst_meldingen_oktober = [metadata.sum_values(dictionary=meldingen, keys=key) for key in oktober]

    meling_ = metadata.count_values(dictionary=meldingen, keys='03_2018')
    storingen_2019 = metadata.count_values(dictionary=storingen, keys=data2019)

    avg_oktober = metadata.avg_monthly(dictionary=meldingen, keys=oktober)
    avg_2019 = metadata.avg_monthly(dictionary=storingen, keys=data2019)

    data_61_mod = metadata.get_di_dict(notification_type='meldingen', di='61')

    avg_mod = metadata.avg_yearly(dictionary=meldingen, exclude_year=['2020'])

    maand_lijst = metadata.get_month_list(exclude_month='02', exclude_year='2019')

    meldingen_per_di_avg = metadata.avg_yearly(dictionary=metadata.get_di_dict(di='46A-08'), exclude_year='2020')

