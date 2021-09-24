"""
Class voor het bevragen van de maximo database
"""
import os

import requests
import json
from typing import Union

import pandas as pd


# todo: api_get_request OSLC request maximo o.i.d.
class QueryMaximoDatabase:

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.object_structure = None  # set by _set_object_structure
        self.set_object_structure()  # sets default value of object structure

        self.site_id = None

        self.response = None
        self._dump_list = None  # when not None it's a list of lists
        self.response_data = None  # json object of the _dump_list

        self.url_parameters = {'lean': 1,  # no namespace in JSON
                               '_dropnulls': 0,  # don't pass null values
                               'Accept': 'application/json'}  # set JSON as default output

        self.parameters = None

        # Set up header dictionary w/ API key according to documentation
        self.headers = {'maxauth': self.api_key}

    def set_site_id(self, site_id: str) -> None:
        self.site_id = site_id

    def set_object_structure(self, object_structure: str = 'MXWO_SND') -> None:
        self.object_structure = object_structure

    def _get_response(self, query: Union[str, None] = None) -> str:
        """
        Function to launch the GET request to the Maximo application.
        :param query: The query variable defined in '2. Declare the required
                      variables needed to run and filter your data export result.'
        :return: The respone of the Maximo application.
        """
        print('checking self.query and query (param)')
        if query is None:
            raise ValueError("You're trying to make a request without a query. Set a query before making a request.")

        print('build api-url')
        api_url = 'https://maximotest.tbi.nl/maximo/oslc/os/' + self.object_structure + '?'

        print('making request')

        # Call the API
        response = requests.get(api_url, headers=self.headers, params=self.parameters)

        if response.status_code == 200:
            print('Success!')
        elif response.status_code == 404:
            print('ApiError')

        self.response = response
        return "Done."

    def _get_dump_list(self) -> None:
        json_data = self.response.json()
        _links = pd.DataFrame(data=json_data['member'])
        dump_list = []
        for url in _links['href']:
            r = requests.get(url, headers=self.headers, params=self.parameters)
            raw_response_data = r.json()
            dump_list.append(raw_response_data)

        self._dump_list = dump_list

    def get_response_data(self, query: Union[str, None] = None) -> None:
        try:
            self.parameters = {**self.url_parameters,  # asterisks (**) unpacks each key:value-pair of the dict
                               'oslc.where': query}
            self._get_response(query=query)
            self._get_dump_list()
            self.response_data = json.dumps(self._dump_list)
        except ValueError as e:
            print(f"The following error is given: {e}")


def main():
    qmdb = QueryMaximoDatabase("bWF4YWRtaW46R21iQ1dlbkQyMDE5")
    # query = 'siteid="CT1EN2" and worktype="COR" and reportdate>="2018-01-01T00:00:00-00:00" and reportdate<="2018-03-30T00:00:00-00:00"'
    query = 'siteid="CT1EN2" and worktype="COR" and reportdate>="2021-04-01T00:00:00-00:00" and reportdate<="2021-06-30T00:00:00-00:00"'
    # qmdb._get_response(query=query)
    qmdb.get_response_data(query=query)


if __name__ == "__main__":
    main()
