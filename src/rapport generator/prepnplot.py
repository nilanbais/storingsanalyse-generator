"""
Class voor het preppen en plotten van de grafieken.

Het idee van de class is dat er een object met een standaard data sturctuur als input gebruikt wordt. Op basis van
deze datastructuur en een aantal gespecificeerde parameters moeten de verschillende grafieken geplot kunnen worden.

Met behulp van deze class wil ik dat het mogelijk wordt een soort ad hoc analyse tool te maken waarbij een soort
sandbox omgeving wordt opgezet, waarin de gebruiker aan verschillende parameters kan 'draaien' om zo een specifiek
inzicht te krijgen (bijv. storingen van twee di nummers enkel in de maanden april en december)



"""
import numpy as np
import matplotlib.pyplot as plt

from datetime import datetime

from pandas import DataFrame
from matplotlib.figure import Figure
from typing import Tuple, Optional, Union, List


class Node:
    def __init__(self, data):
        self.data = data
        self.next = None
        self.prev = None


class LinkedList:
    def __init__(self):
        self.head = None

    def __getitem__(self, index):
        i = 0
        temp = self.head

        if temp.data is None:
            raise Exception("Linked List is empty")

        if isinstance(index, int):
            while temp is not None:
                if i == index:
                    return temp
                temp = temp.next
                i += 1
        elif isinstance(index, str):
            while temp is not None:
                if temp.data == index:
                    return temp
                temp = temp.next

    def traverse(self, starting_point=None):
        if starting_point is None:
            starting_point = self.head
        node = starting_point
        while node is not None and (node.next != starting_point):
            yield node
            node = node.next
        yield node

    def print_list(self, starting_point=None):
        nodes = []
        for node in self.traverse(starting_point):
            nodes.append(str(node.data))
        print(" -> ".join(nodes))

    def get_prev_val(self, value):
        n = self.__getitem__(value)
        return n.prev.data


class PrepNPlot:

    # Class variables (callable by using class_name.var_name)
    _quarters = {'Q1': {'01', '02', '03'},
                 'Q2': {'04', '05', '06'},
                 'Q3': {'07', '08', '09'},
                 'Q4': {'10', '11', '12'}}

    _maand_dict = {"1": "Januari",
                   "2": "Februari",
                   "3": "Maart",
                   "4": "April",
                   "5": "Mei",
                   "6": "Juni",
                   "7": "Juli",
                   "8": "Augustus",
                   "9": "September",
                   "10": "Oktober",
                   "11": "November",
                   "12": "December"}

    _separator_set = {'_', '/', '\\', '.', '-'}

    def __init__(self):
        self.last_seen_bin_names = []

        self.quarter_sequence = self.__build_quarter_linkedlist()

    """
    Managing modules -- Modules that influence the attributes of PrepNPlot.
    """
    # todo: aanpassen naar de beste data strucuur om verschillende figuren vast te leggen
    def __build_quarter_linkedlist(self):
        llist = LinkedList()
        for i in range(len(self._quarters.keys())):
            key = list(self._quarters.keys()).__getitem__(i)
            n = Node(key)
            if i == 0:
                llist.head = n
                n.prev = llist.head
            else:
                prev_n = llist.__getitem__(i-1)
                prev_n.next = n
                n.prev = prev_n
                if i == (len(list(self._quarters.keys())) - 1):
                    n.next = llist.head
                    llist.head.prev = n
                    return llist

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
    def _get_stringformat(string: str) -> str:
        if len(string) == 17:
            return '%d-%m-%y %H:%M:%S'
        elif len(string) == 7:
            return '%m-%Y'
        else:
            raise ValueError(f"Unknown input format of the datetime string. Input string: {string}")

    def replace_separator(self, string: str, inserting_separator: str = '-') -> str:
        if any(s in string for s in self._separator_set):
            for separator in self._separator_set:
                string = string.replace(separator, inserting_separator)
        return string

    def _prep_time_range(self, time_range: [str, str]):
        """
        Returns list of datetime objects when given strings.
        :param time_range:
        :return:
        """
        # todo: als het problemen kan oplossen, dan moet hier nog worden toegevoegd dat er een check komt op
        #  welke index de separator staat.
        new_time_range = []
        for tr in time_range:

            tr = self.replace_separator(string=tr)

            if len(tr) == 6 and tr.index('-', 0, 4) == 1:
                tr = '0' + tr  # changing 3-2020 to 03-2020

            str_format = self._get_stringformat(tr)
            new_time_range.append(datetime.strptime(tr, str_format))

        return new_time_range

    def _get_time_range_base(self, time_range: [datetime, datetime]) -> list:
        """
        Returns a list with all the months between the start and end of the input time range
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

    # todo: aanpassen in documentatie
    def _month_num_to_name(self, month_num: int or list) -> str:
        if isinstance(month_num, list):
            maand = [self._maand_dict[str(num)] for num in month_num for key in self._maand_dict.keys() if str(num) == key]
            return maand[0]
        elif isinstance(month_num, int):

            return self._maand_dict[str(month_num)]

    def prettify_time_label(self, label: str) -> str:
        """
        Return a prettified string in which the separator is removed and the month number is substituted for the
        written out month name ('03_2018' -> 'Maart 2018' and 'Q4_2020' -> 'Q4 2020')
        :param label:
        :return:
        """
        label = self.replace_separator(string=label, inserting_separator='_')  # makes sure '_' is the separator
        bin, year = label.split('_')
        if 'Q' in bin.title():
            return bin.title() + ' ' + year
        return self._month_num_to_name(month_num=int(bin)) + ' ' + year

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

    @staticmethod
    def _transform_to_meta_structure(input_object: DataFrame, time_key: str, categorical_key: str) -> dict:
        """
        Transforms a DataFrame to the structure of the metadata (like bellow).
            {month}_{year}": {
                category_1: count,
                category_2: count,
                  ...     :  ... ,
                category_n: count
            }

        :param input_object:
        :param time_key: The key/column name in which the time is stored
        :param categorical_key: The key/column name in which the categorical data is stored
        :return:
        """
        _input_object = input_object.reset_index()
        result_dict = dict()
        for index in range(len(_input_object[time_key])):

            rapport_time = datetime.strptime(_input_object[time_key][index], '%d-%m-%y %H:%M:%S') \
                if isinstance(_input_object[time_key][index], str) else _input_object[time_key][index]

            month_str = str(rapport_time.month) if rapport_time.month > 9 else '0' + str(rapport_time.month)
            result_dict_key = month_str + '_' + str(rapport_time.year)

            if result_dict_key not in result_dict.keys():
                result_dict[result_dict_key] = {}

            if _input_object[categorical_key][index] not in result_dict[result_dict_key]:
                result_dict[result_dict_key][_input_object[categorical_key][index]] = 1
            else:
                result_dict[result_dict_key][_input_object[categorical_key][index]] += 1

        return result_dict

    @staticmethod
    def build_output_first_step(input_object: dict, available_categories: List[str], bins: Union[dict, None]) -> dict:
        output_dict = dict()
        if bins:
            for bin_key in bins.keys():
                bin_dict = {}  # dictionary that is refeshed for each iteration of bin_key
                for month_key in input_object.keys():
                    if month_key in bins[bin_key]:
                        _temp_dict = input_object[month_key].copy()

                        for key in sorted(available_categories):
                            _temp_dict[key] = 0 if key not in _temp_dict.keys() else _temp_dict[key]  # adding the missing categories to the dict

                        if np.nan in _temp_dict.keys():
                            _temp_dict.pop(np.nan)

                        temp_dict = {key: _temp_dict[key] for key in sorted(_temp_dict.keys())}
                        bin_dict[month_key] = temp_dict
                    else:
                        pass
                if len(bin_dict.keys()) > 0:
                    output_dict[bin_key] = bin_dict
                else:
                    pass
        else:
            for month_key in input_object.keys():
                _temp_dict = input_object[month_key].copy()
                for key in sorted(available_categories):
                    _temp_dict[key] = 0 if key not in _temp_dict.keys() else _temp_dict[key]  # adding the missing categories to the dict

                if np.nan in _temp_dict.keys():
                    print(f'{month_key} nan pop. count = {_temp_dict[np.nan]}')
                    _temp_dict.pop(np.nan)

                temp_dict = {key: _temp_dict[key] for key in sorted(_temp_dict.keys())}
                output_dict[month_key] = temp_dict

        return output_dict

    # todo: change name to more clear name
    def _prep_first_step(self, input_object: Union[Tuple[DataFrame, str, str], dict], time_range: Union[List[datetime], List[str]], available_categories: List[str], bin_size: Optional[str] = None) -> dict:
        """
        Builds a dictionary with the following structure:
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

        :param input_object: a full dataset from which all the specific data is needed to be extracted.
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
            bins = None

        # building the output dict based on the bins dict
        output_dict = self.build_output_first_step(input_object, available_categories, bins)

        return output_dict

    @staticmethod
    def _prep_second_step(input_dict: dict) -> dict:
        """
        This preparation action that changes the first structure to the later data structure, by adding
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

    def _prep_end_step_summary(self, input_dict: dict) -> int:
        """
        Module that counts the times a value has been seen in a bin.
        It is save to assume that the main level of keys are the dict names.
        Input is the output of step two.
        """
        if all([isinstance(value, int) for value in input_dict.values()]):
            return sum(input_dict.values())

        output_dict = input_dict.copy()
        for key, value in input_dict.items():
            if isinstance(value, dict):
                output_dict[key] = self._prep_end_step_summary(value)  # value being the new input dict

        return self._prep_end_step_summary(output_dict)

    def prep(self, input_object: Union[DataFrame, dict], time_range: [datetime, datetime] or [str, str], available_categories: List[str], category_key: Optional[str] = None, time_key: Optional[str] = None, bin_size: Optional[str] = False) -> Tuple[List[str], List[list]]:
        """
        returns the prepped list of lists with the corresponding category labels.
        :param input_object:
        :param time_range:
        :param available_categories:
        :param category_key:
        :param time_key:
        :param bin_size:
        :return:
        """
        # todo: Het kan zijn dat de functie gebruikt wordt en dat er geen time_range gespecificeerd kan worden
        #  (of dat men dat niet wil) dus er moet nog iets komen voor deze situaties

        # todo: Module schrijven voor functionaliteit dat kwartalen van verschillende jaren vergeleken kunnen worden.

        _input_object = (input_object, time_key, category_key) if isinstance(input_object, DataFrame) else input_object

        result_step_one = self._prep_first_step(_input_object, time_range, available_categories, bin_size)

        if not bin_size:  # when no bin_size is given, the month_keys represent the bin_size aka no second step needed
            result_step_two = result_step_one
        else:
            result_step_two = self._prep_second_step(input_dict=result_step_one)

        self.last_seen_bin_names = list(result_step_two.keys())

        """
        onderstaande stap wordt niet gesorteerd op aanwezige categorieën, kijk of dit nog ingebouwd kan worden.
        """
        result_step_three = self._prep_end_step(input_dict=result_step_two, bin_names=self.last_seen_bin_names)

        categories, list_of_lists = self.filter_prep_output(list_of_lists=result_step_three, available_categories=available_categories)

        return categories, list_of_lists

    # todo: documenteren
    def test_prep(self, input_object: Union[DataFrame, dict], time_range: [datetime, datetime] or [str, str], available_categories: List[str], category_key: Optional[str] = None, time_key: Optional[str] = None, bin_size: Optional[str] = False) -> Tuple[List[str], List[list]]:
        # todo: Het kan zijn dat de functie gebruikt wordt en dat er geen time_range gespecificeerd kan worden
        #  (of dat men dat niet wil) dus er moet nog iets komen voor deze situaties

        # todo: filter als laatste stap. In deze stap moeten de keys die in geen enkele lijst van de lijst van
        #  lijsten voorkomt, worden verwijderd uit de dictionary.

        _input_object = (input_object, time_key, category_key) if isinstance(input_object, DataFrame) else input_object

        print(f"_input_object:\n{_input_object}")

        result_step_one = self._prep_first_step(_input_object, time_range, available_categories, bin_size)
        print(f"result step one:\n{result_step_one}")

        if not bin_size:  # when no bin_size is given, the month_keys represent the bin_size aka no second step needed
            result_step_two = result_step_one
        else:
            result_step_two = self._prep_second_step(input_dict=result_step_one)
        print(f"result step two:\n{result_step_two}")

        self.last_seen_bin_names = list(result_step_two.keys())

        result_step_three = self._prep_end_step(input_dict=result_step_two, bin_names=self.last_seen_bin_names)
        print(f"result step three:\n{result_step_three}")

        categories, list_of_lists = self.filter_prep_output(list_of_lists=result_step_three, available_categories=available_categories)
        print(f'result filter step:\n{categories, list_of_lists}')

        print(len(categories), [len(_) for _ in list_of_lists])

        return categories, list_of_lists

    def prep_summary(self, input_object: Union[DataFrame, dict], time_range: [datetime, datetime] or [str, str], available_categories: List[str], category_key: Optional[str] = None, time_key: Optional[str] = None, bin_size: Optional[str] = False) -> dict:
        _input_object = (input_object, time_key, category_key) if isinstance(input_object, DataFrame) else input_object

        result_step_one = self._prep_first_step(_input_object, time_range, available_categories, bin_size)

        if not bin_size:  # when no bin_size is given, the month_keys represent the bin_size aka no second step needed
            result_step_two = result_step_one
        else:
            result_step_two = self._prep_second_step(input_dict=result_step_one)

        self.last_seen_bin_names = list(result_step_two.keys())

        result_step_three = dict()
        for key in self.last_seen_bin_names:
            result_step_three[key] = self._prep_end_step_summary(input_dict=result_step_two[key])

        return result_step_three

    """
    Plot modules -- Modules that focus on setting up the parameters for plotting and plotting of the figure.
    """
    def plot(self, input_data: List[list], plot_type: str, category_labels: list, bin_labels: list, title: str, show_plot: bool = False) -> Figure:
        """
        Takes the result of prep and plots it.
        :param input_data:
        :param plot_type:
        :param category_labels:
        :param bin_labels:
        :param title:
        :param show_plot:
        :return:
        """
        # Starts interactive mode for matplotlib pyplot
        plt.ion()
        x_labels = sorted(category_labels)
        x_locations = np.arange(len(x_labels))  # todo: aanpassen van het automatisch bepalen

        legend_names = list(bin_labels)

        # fig, axis = plt.subplots(figsize=(len(x_labels), 5))
        fig, axis = plt.subplots()

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
                axis.bar(x=x_labels, height=input_data[i], width=bar_width, label=legend_names[i], bottom=prev) if i > 0 else \
                    axis.bar(x=x_labels, height=input_data[i], width=bar_width, label=legend_names[i])

                # prev sets the height of the newly added values like above
                # the added list needs to be added to prev to get the correct height
                prev = [prev[idx] + input_data[i][idx] for idx in range(len(input_data[i]))] if i > 0 else input_data[i]
        else:
            raise ValueError("Please use a valid type as plot_type. Valid types are 'side-by-side' or 'stacked'.")

        # titel en namen van de assen
        axis.set_ylabel('Aantal')
        axis.set_title(title.title())

        # namen langs de assen
        axis.set_xticks(x_locations + bar_width / len(input_data))
        axis.set_xticklabels(x_labels)

        axis.margins(x=0.01, y=0.1)

        axis.set_axisbelow(True)
        axis.grid(axis='y', linestyle='--')

        axis.legend()

        # Stops interactive mode for matplotlib pyplot
        plt.ioff()

        # fig.autofmt_xdate(rotation=45)

        plt.show() if show_plot else plt.close()

        return fig

    @staticmethod
    def plot_summary(x_labels: list, data: list, title: str, show_plot: bool = False) -> Figure:
        """
        Takes the result of prep_summary and plots it.
        :param x_labels:
        :param data:
        :param title:
        :param show_plot:
        :return:
        """
        # Starts interactive mode for matplotlib pyplot
        plt.ion()
        fig, axis = plt.subplots()
        axis.bar(x_labels, data, width=0.3)
        axis.set_ylabel('Aantal')
        axis.set_title(title.title())
        axis.margins(x=.2, y=.2)

        axis.set_axisbelow(True)
        axis.grid(axis='y', linestyle='--')

        # Stops interactive mode for matplotlib pyplot
        plt.ioff()

        if show_plot:
            plt.show()
        else:
            plt.close()

        return fig

    # todo: toevoegen aan documentatie
    @staticmethod
    def filter_prep_output(list_of_lists: List[list], available_categories: List[str]) -> Tuple[List[str], List[list]]:
        """
        This module filers the prep_output to return a modified copy of the list_of_lists (LOL) and the list of
        corresponding available categories, where all the categories of which all the values in the LOL are '0'
        are filtered out. Both the objects NEED TO BE sorted and stay in that order.
        IMPORTANT -----------------------------------------------------------------------------------------------
            The list with the available categories needs to be sorted. The function build_output_first_step takes
            the available categories and sorts them when using them. This means that the list of lists created is
            in the order of the sorted available categories.
        ---------------------------------------------------------------------------------------------------------
        :param list_of_lists:
        :param available_categories:
        :return:
        """
        _data_package = dict()
        for i in range(len(list_of_lists)):
            _data_package[i] = list_of_lists[i]

        result_categories = list()
        result_list_of_lists = [list() for _ in range(len(list_of_lists))]

        for category, items in zip(sorted(available_categories), zip(*_data_package.values())):
            if sum(items) > 0:
                result_categories.append(category)
                for i in range(len(items)):
                    result_list_of_lists[i].append(items[i])

        return result_categories, result_list_of_lists


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

    print(pp.prettify_time_label(x))

    print(z[0].month)
    month_set = [pp._quarters[key] for key in pp._quarters.keys() if pp._check_a_in_b(a=str(z[0].month), b=pp._quarters[key])][0]
    print(month_set)

    pp.quarter_sequence.print_list()
    x = pp.quarter_sequence['Q4']
    print(f"x data = {x.data}")
    print(f"x prev = {x.prev.data}")
    print(f"x next = {x.next.data}")
