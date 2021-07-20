"""
Class voor het preppen en plotten van de grafieken.

Het idee van de class is dat er een object met een standaard data sturctuur als input gebruikt wordt. Op basis van
deze datastructuur en een aantal gespecificeerde parameters moeten de verschillende grafieken geplot kunnen worden.

Met behulp van deze class wil ik dat het mogelijk wordt een soort ad hoc analyse tool te maken waarbij een soort
sandbox omgeving wordt opgezet, waarin de gebruiker aan verschillende parameters kan 'draaien' om zo een specifiek
inzicht te krijgen (bijv. storingen van twee di nummers enkel in de maanden april en december)

"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from datetime import datetime

from pandas import DataFrame
from matplotlib.figure import Figure
from typing import Tuple, Optional, Union, List


class PrepNPlot:

    # Class variables (callable by using class_name.var_name)
    _quarters = {'Q1': {'01', '02', '03'},
                 'Q2': {'04', '05', '06'},
                 'Q3': {'07', '08', '09'},
                 'Q4': {'10', '11', '12'}}

    def __init__(self):
        self.graphs = []
        self.last_seen_bin_names = []

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
        # todo: als het problemen kan oplossen, dan moet hier nog worden toegevoegd dat er een check komt op
        #  welke index de seperator staat.
        seperator_set = {'_', '/', '\\', '.'}
        new_time_range = []
        for tr in time_range:

            if any(s in tr for s in seperator_set):
                for seperator in seperator_set:
                    tr = tr.replace(seperator, '-')

            str_format = '%m-%Y' if len(tr) == 7 else '%d-%m-%y %H:%M:%S' if len(tr) == 17 else None
            new_time_range.append(datetime.strptime(tr, str_format))

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

    def _months_in_year_bin(self):
        """
        Returns a set of the months, build from the values of the _quarters dictionary.
        :return:
        """
        month_set = set()
        for index in range(len(self._quarters)):
            month_set = set.union(month_set, self._quarters[list(self._quarters.keys())[index]])
        return month_set

    @staticmethod
    def _check_a_in_b(a: str, b: set) -> bool:
        return True if a in b else False

    def _check_month_in_bin(self, time_to_check: datetime, bin_size: str, specified_q: str = None) -> bool:
        if bin_size == 'quarter':
            month_set = self._quarters[specified_q.title()]
        elif bin_size == 'year':
            month_set = self._months_in_year_bin()
        else:
            raise ValueError("Please use a bin size of 'quarter' or 'year'.")
        month_str = str(time_to_check.month) if time_to_check.month > 9 else '0' + str(time_to_check.month)
        return self._check_a_in_b(a=month_str, b=month_set)

    def _transform_to_meta_structure(self, input_object: DataFrame, time_key: str, categorical_key: str) -> dict:
        """
        Transforms a DataFrame to the structure of the metadata (like bellow).
            {month}_{year}": {
                category_1: count,
                category_2: count,
                  ...     :  ... ,
                category_n: count
            }

        :param input_object:
        :param time_key:
        :param categorical_key:
        :return:
        """
        result_dict = dict()
        for index in range(len(input_object[time_key])):

            rapport_time = datetime.strptime(input_object[time_key][index], '%d-%m-%y %H:%M:%S') \
                if isinstance(input_object[time_key][index], str) else input_object[time_key][index]

            month_str = str(rapport_time.month) if rapport_time.month > 9 else '0' + str(rapport_time.month)
            result_dict_key = month_str + '_' + str(rapport_time.year)

            if result_dict_key not in result_dict.keys():
                result_dict[result_dict_key] = {}

            if input_object[categorical_key][index] not in result_dict[result_dict_key]:
                result_dict[result_dict_key][input_object[categorical_key][index]] = 1
            else:
                result_dict[result_dict_key][input_object[categorical_key][index]] += 1

        return result_dict

    # todo: change name to more clear name
    def _prep_first_step(self, input_object: Union[Tuple[DataFrame, str, str], dict], time_range: Union[List[datetime], List[str]], available_categories: List[str], bin_size: Optional[str] = None) -> dict:
        """

        :param input_object: way to parse data from which all is needed to be extracted.
        :param time_key: The key/column name in which the time is stored
        :param categorical_key: The key/column name in which the categorical data is stored
        :param bin_size: Bin size is a string 'quarter', 'year'
        :param time_range: A list like [start, end] where start and end need to be both datetime objects or strings representing dates.
        :return: Dict with structure that can be used 'as-is' in _prep_end_step()
        """
        """
        If you want to use a dataframe (df) as an input_object, it's mandatory to specify the time_key and 
        the categorical_key, like so: tuple(df, time_key, categorical_key).
        """
        input_object = self._transform_to_meta_structure(*input_object) if isinstance(input_object, tuple) else input_object

        # todo: OPTIE stap 1 uit bovenstaande uitbreiden zodat er ook meerdere tijdranges gegeven kunnen worden, zoals
        #  Q1_2019 en Q1_2020 en dat deze dan ook in één hetzelfde resultaat worden gevoegd
        time_range = time_range if isinstance(time_range[0], datetime) else self._prep_time_range(time_range=time_range)

        if bin_size:  # if no binsize is given it will return a list of all the months within the time_range
            bins = self._get_bins(bin_size=bin_size, time_range=time_range)
        else:
            return input_object  # input after the transformation to meta is the correct dict if no bins are needed

        # building output dict based on the bins dict
        output_dict = dict()
        for bin_key in bins.keys():
            bin_dict = {}  # dictionary that is refeshed for each iteration of bin_key

            for month_key in input_object.keys():
                if month_key in bins[bin_key]:
                    _temp_dict = input_object[month_key].copy()
                    for key in sorted(available_categories):
                        _temp_dict[key] = 0 if key not in _temp_dict.keys() else _temp_dict[key]  # adding the missing categories to the dict
                    bin_dict[month_key] = _temp_dict
                else:
                    pass

            if len(bin_dict.keys()) > 0:
                output_dict[bin_key] = bin_dict
            else:
                pass

        return output_dict

    def _prep_second_step(self, input_dict: dict) -> dict:
        """
        This preperation action that changes the following to the data structure presented after the next, by adding
        up the values of each third level key (key_1x1)
        (example: the values of key_111, key_121, key_131 would be added up and stored as key_11: value_11 in the
        result)

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

        result:
            {key_1: {key_11: value_11, key_12: value_12, ..., key_1n: value_1n},
             key_2: {key_21: value_21, key_22: value_12, ..., key_2n: value_2n},
             key_3: {key_31: value_31, key_32: value_32, ..., key_3n: value_3n}}

        :param input_dict:
        :return:
        """
        output_dict = dict()
        for bin_key in input_dict.keys():
            added_subdict = {}
            for month_key in input_dict[bin_key]:
                for category, count in input_dict[bin_key][month_key].items():
                    if category in added_subdict.keys():
                        added_subdict[category] += count
                    else:
                        added_subdict[category] = count
            output_dict[bin_key] = added_subdict
        return output_dict

    # todo: change name to more clear name
    def _prep_end_step(self, input_dict: dict, bin_names: list) -> list:
        """
        takes input data structure:
            {key_1: {key_11: value_11, key_12: value_12, ..., key_1n: value_1n},
             key_2: {key_21: value_21, key_22: value_12, ..., key_2n: value_2n},
             key_3: {key_31: value_31, key_32: value_32, ..., key_3n: value_3n}}

            with:
                key_x - main level - these keys have to be unique. In a lot of cases the specified time like months or years
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
        :param bin_names: list with the unique main level values.
        :return:
        """
        data = []
        num_main_lvl_keys = len(bin_names)
        for index in range(num_main_lvl_keys):
            if (bin_names.__getitem__(index)) in input_dict.keys():
                data.append(list(input_dict[bin_names.__getitem__(index)].values()))
            else:
                data.append([0 for _ in range(len(self._get_first_element(input_dict)))])

        return data

    def prep(self, input_object: Union[DataFrame, dict], time_range: [datetime, datetime] or [str, str], available_categories: List[str], category_key: Optional[str] = None, time_key: Optional[str] = None, bin_size: Optional[str] = False) -> list:
        # todo: Het kan zijn dat de functie gebruikt wordt en dat er geen time_range gespecificeerd kan worden
        #  (of dat men dat niet wil) dus er moet nog iets komen voor deze situaties

        _input_object = (input_object, time_key, category_key) if isinstance(input_object, DataFrame) else input_object

        result_step_one = self._prep_first_step(_input_object, time_range, available_categories, bin_size)

        if not bin_size:  # when no bin_size is given, the month_keys represent the bin_size aka no second step needed
            result_step_two = result_step_one
        else:
            result_step_two = self._prep_second_step(input_dict=result_step_one)

        self.last_seen_bin_names = list(result_step_two.keys())

        result_step_three = self._prep_end_step(input_dict=result_step_two, bin_names=self.last_seen_bin_names)

        return result_step_three

    """
    Plot modules -- Modules that focus on setting up the parameters for plotting and plotting of the figure.
    """
    def plot(self, input_data: List[list], plot_type: str, category_labels: list, bin_labels: list) -> None:
        x_labels = category_labels
        x_locations = np.arange(len(x_labels))

        legend_names = list(bin_labels)

        fig, axis = plt.subplots(figsize=(len(x_labels), 5))

        bar_width = 0.2

        # voor het bepalen van de afstand vanaf x zodat de bars niet overlappen
        x_generator = (x_locations + (y * bar_width) for y in (0, 1))

        if plot_type == 'side-by-side':
            # Toevoegen van de bars
            for i in range(len(input_data)):
                bar = axis.bar(x=next(x_generator), height=input_data[i], width=bar_width, label=legend_names[i])
        elif plot_type == 'stacked':
            prev = []
            for i in range(len(input_data)):
                # added case for loop l = 0 after if
                axis.bar(x_labels, input_data[i], bar_width, label=legend_names[i], bottom=prev) if i > 0 else \
                    axis.bar(x_labels, input_data[i], bar_width, label=legend_names[i])

                # prev sets the height of the newly added values like above
                # the added list needs to be added to prev to get the correct height
                prev = [prev[idx] + input_data[i][idx] for idx in range(len(input_data[i]))] if i > 0 else input_data[i]
        else:
            raise ValueError("Please use a valid type as plot_type. Valid types are 'side-by-side' or 'stacked'.")

        # titel en namen van de assen
        axis.set_xlabel('Deelinstallatie nummers')
        axis.set_ylabel('Aantal')
        axis.set_title("Aantal storingen per deelinstallatie")

        # namen langs de assen
        axis.set_xticks(x_locations + bar_width / len(input_data))
        axis.set_xticklabels(x_labels)

        axis.margins(x=0.01, y=0.1)

        axis.set_axisbelow(True)
        axis.grid(axis='y', linestyle='--')

        axis.legend()

        # fig.autofmt_xdate(rotation=45)

        plt.show()


if __name__ == '__main__':
    import random

    pp = PrepNPlot()

    test_input = {1: {'Incident': 2, 'Storing': 1, 'Onterecht': 0, 'Preventief': 0},
                  2: {'Incident': 3, 'Storing': 0, 'Onterecht': 0, 'Preventief': 1},
                  3: {'Incident': 2, 'Storing': 0, 'Onterecht': 1, 'Preventief': 0}}

    test_list = [random.randint(0, 10) for _ in range(10)]

    first = pp._prep_end_step(test_input, bin_names=[_ for _ in test_input.keys()])  # unique_values needs to be refactored to num_bins

    x = '10-2017'
    y = '01-2020'
    z = pp._prep_time_range([x, y])

    print(z[0].month)
    month_set = [pp._quarters[key] for key in pp._quarters.keys() if pp._check_a_in_b(a=str(z[0].month), b=pp._quarters[key])][0]
    print(month_set)

