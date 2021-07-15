"""
Class voor het preppen en plotten van de grafieken.

Het idee van de class is dat er een object met een standaard data sturctuur als input gebruikt wordt. Op basis van
deze datastructuur en een aantal gespecificeerde parameters moeten de verschillende grafieken geplot kunnen worden.

Met behulp van deze class wil ik dat het mogelijk wordt een soort ad hoc analyse tool te maken waarbij een soort
sandbox omgeving wordt opgezet, waarin de gebruiker aan verschillende parameters kan 'draaien' om zo een specifiek
inzicht te krijgen (bijv. storingen van twee di nummers enkel in de maanden april en december)

"""
import pandas as pd

import matplotlib.pyplot as plt

from datetime import datetime

from pandas import DataFrame, Series
from matplotlib.figure import Figure


class PrepNPlot:

    # Class variables (callable by using class_name.var_name)
    _quarters = {'Q1': {'01', '02', '03'},
                 'Q2': {'04', '05', '06'},
                 'Q3': {'07', '08', '09'},
                 'Q4': {'10', '11', '12'}}

    def __init__(self):
        self.graphs = []

    """
    Managing modules -- Modules that influence the attributes of PrepNPlot.
    """
    # todo: aanpassen naar de beste data strucuut om verschillende figuren vast te leggen
    def add_graph_for_export(self, figure: Figure) -> None:
        self.graphs.append(figure)

    """
    Preperation modules -- Modules that focus on the preperation and transformation of the input data.
    """
    @staticmethod
    def _get_first_element(input_object: dict or list):
        """
        Returns the first element of an iterable.
        :param input_object:
        :return:
        """
        first_index = next(iter(input_object))
        return input_object.__getitem__(first_index)

    @staticmethod
    def _prep_time_range(time_range: [str, str]):
        """
        Returns list of datetime objects when given strings.
        :param time_range:
        :return:
        """
        seperator_set = {'_', '/', '\\', '.'}
        new_time_range = []
        for tr in time_range:

            if any(s in tr for s in seperator_set):
                for seperator in seperator_set:
                    tr = tr.replace(seperator, '-')

            new_time_range.append(datetime.strptime(tr, '%m-%Y'))

        return new_time_range

    def _get_time_range_base(self, time_range: [datetime, datetime]) -> list:
        """

        :param time_range:
        :return:
        """
        start_date = time_range[0]
        end_date = time_range[-1]
        time_range_base = []
        for year in range(int(start_date.year), int(end_date.year) + 1):

            if len(time_range_base) == 0:  # first iteration of year
                for month in range(int(start_date.month), 13):
                    time_range_base.append(str(month) + '_' + str(year)) if len(str(month)) > 1 \
                        else time_range_base.append('0' + str(month) + '_' + str(year))
                continue  # skip the rest of this iteration
            elif year == end_date.year:  # last iteration of year
                for month in range(1, int(end_date.month) + 1):
                    time_range_base.append(str(month) + '_' + str(year)) if len(str(month)) > 1 \
                        else time_range_base.append('0' + str(month) + '_' + str(year))
                continue

            for month in range(1, 13):
                time_range_base.append(str(month) + '_' + str(year)) if len(str(month)) > 1 \
                    else time_range_base.append('0' + str(month) + '_' + str(year))

        return time_range_base

    def _get_bins(self, bin_size: str, time_range: [datetime, datetime]) -> dict:
        """
        Returns a data structure like:
            {'bin_1': [list of months belonging to the specified bin],
             'bin_2': [list of months belonging to the specified bin]}

        Time range needs to consist of a month and a year. If not given, the range will be [oldest know time, youngest knows time] or the module will raise and error.

        :param bin_size:
        :param time_range: time range of the bins (objects need to have a month and year).
        :return:
        """
        binned_dictionary = dict()
        _time_range_base = self._get_time_range_base(time_range=time_range)
        if bin_size == 'quarter':

            years = set([x.split('_')[-1] for x in _time_range_base])
            for year in sorted(years):
                for q in self._quarters.keys():
                    key = q + '_' + year
                    value = [x for x in _time_range_base if (x.split('_')[0] in self._quarters[q] and x.split('_')[-1] == year)]
                    if len(value) > 0:
                        binned_dictionary[key] = value
                    # todo: misschien nog bericht meegeven wanneer het eerste of laatste kwartaal van
                    #  binned_dictionary niet uit 3 maanden bestaat (kan de analyse vertroebelen)
        elif bin_size == 'year':
            years = set([x.split('_')[-1] for x in _time_range_base])
            for year in sorted(years):
                binned_dictionary[year] = [x for x in _time_range_base if x.split('_')[-1] == year]

        return binned_dictionary

    # todo: change name to more clear name
    def _prep_middle_step(self, input_object: (DataFrame or dict), time_key: str, categorical_key: str, time_range: [datetime, datetime] or [str, str], bin_size: str = False) -> dict:
        """

        :param input_object: way to parse data from which all is needed to be extracted.
        :param time_key: The key/column name in which the time is stored
        :param categorical_key: The key/column name in which the categorical data is stored
        :param bin_size: Bin size is a string 'quarter', 'year'
        :param time_range: A list like [start, end] where start and end need to be both datetime objects or strings representing dates.
        :return: Dict with structure that can be used 'as-is' in _prep_end_step()
        """
        input_object = input_object.to_dict() if isinstance(input_object, DataFrame) else input_object
        """
        done 1. look at which months need to be combined to match the asked time_range (bins of years/quarters/months)
            Bellow is an example for quarter bins.
                {'Q4_2020': ['10_2020', '11_2020', '12_2020'],
                 'Q1_2021': ['01_2021', '02_2021', '03_2021']}
        2. substitute the months for the categorical data seen in that month and how many instances have coutned.
        3. add up the counts of each category within one time bin.
        4. return
        """
        time_range = time_range if isinstance(time_range[0], datetime) else self._prep_time_range(time_range=time_range)
        if not bin_size:  # if no binsize is given it will return a list of all the months within the time_range
            bins = self._get_time_range_base(time_range=time_range)
        else:
            bins = self._get_bins(bin_size=bin_size, time_range=time_range)
        # todo: stap 2 schrijven (onderstaande punten horen niet bij elkaar, maar dit kan misschien eigenlijk toch wel)
        # hoe kan je met zekerheid vaststellen wat het format is waarin je tijd genoteerd staat?
        # zorg ook voor de meest algemene count functie.

        pass

    # todo: change name to more clear name
    def _prep_end_step(self, input_dict: dict, unique_values: list) -> list:
        """
        takes input data structure:
            {key_1: {key_11: value_11, key_12: value_12, ..., key_1n: value_1n},
             key_2: {key_21: value_21, key_22: value_12, ..., key_2n: value_2n},
             key_3: {key_31: value_31, key_32: value_32, ..., key_3n: value_3n}}

            with:
                key_x - main level - these keys have unique. In a lot of cases the specified time like months or years
                key_xy - second level - categorical data like the types of notifications of sbs numbers
                value_xy - second level count - number of times key_xy is seen within time range key_x

        returns data stucture:
            [[value_11, value_12, ..., value_1n],
             [value_21, value_22, ..., value_2n],
             [value_31, value_32, ..., value_3n]]

        Because unique_values is specified as input parameter, it's possible to parse an input_dict as follows and
        the result metioned after that.

            possible input:
                {key_1: {key_11: value_11, key_12: value_12, ..., key_1n: value_1n},
                 key_3: {key_31: value_31, key_32: value_32, ..., key_3n: value_3n}}

            gives following output:
                [[value_11, value_12, ..., value_1n],
                 [0, 0, ..., 0],
                 [value_31, value_32, ..., value_3n]]

        :param input_dict: data object with the structure as mentioned above.
        :param unique_values: list with the unique main level values.
        :return:
        """
        data = []
        num_main_lvl_keys = len(unique_values)
        for index in range(num_main_lvl_keys):
            if unique_values.__getitem__(index) in input_dict.keys():
                data.append(list(input_dict[unique_values.__getitem__(index)].values()))
            else:
                data.append([0 for _ in range(len(self._get_first_element(input_dict)))])

        return data

    """
    Plot modules -- Modules that focus on setting up the parameters for plotting and plotting of the figure.
    """


if __name__ == '__main__':
    import random

    pp = PrepNPlot()

    test_input = {1: {'Incident': 2, 'Storing': 1, 'Onterecht': 0, 'Preventief': 0},
                  2: {'Incident': 3, 'Storing': 0, 'Onterecht': 0, 'Preventief': 1},
                  3: {'Incident': 2, 'Storing': 0, 'Onterecht': 1, 'Preventief': 0}}

    test_list = [random.randint(0, 10) for _ in range(10)]

    first = pp._prep_end_step(test_input, unique_values=[_ for _ in test_input.keys()])


    x = '10-2017'
    y = '01-2020'
    z = pp._prep_time_range([x, y])
    print(pp._get_bins(bin_size='quarter', time_range=z))