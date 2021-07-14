"""
Class voor het preppen en plotten van de grafieken.

Het idee van de class is dat er een object met een standaard datasturctuur als input gebruikt wordt. Op basis van
deze datastructuur en een aantal gespecificeerde parameters moeten de verschillende grafieken geplot kunnen worden.

"""
import pandas as pd

import matplotlib.pyplot as plt

from pandas import DataFrame, Series
from matplotlib.figure import Figure


class PrepNPlot:

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

    # todo: change name to more clear name
    def _prep_middle_step(self, input_object: (DataFrame or dict), time_key: (int or str), categorical_key: (int or str), time_range: str) -> dict:
        """

        :param input_object:
        :return:
        """
        input_object = input_object.to_dict() if isinstance(input_object, DataFrame) else input_object
        """
        1. look at which months need to be combined to match the asked time_range (bins of years/quarters/months)
            Bellow is an example for quarter bins.
                {'Q4_2020': ['10_2020', '11_2020', '12_2020'],
                 'Q1_2021': ['01_2021', '02_2021', '03_2021']}
        2. substitute the months for the categorical data seen in that month and how many instances have coutned.
        3. add up the counts of each category within one time bin.
        4. return
        """
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

    print(first)