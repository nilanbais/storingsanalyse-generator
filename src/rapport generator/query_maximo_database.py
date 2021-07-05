"""
Class voor het bevragen van de maximo database
"""
import os

import requests
import json
from datetime import datetime


# Todo: documentatie schrijven voor class
class QueryMaximoDatabase:

    # class variable
    _default_file_name = f"{str(datetime.now().date()).replace('-', '')}_{str(datetime.now().time().hour)}_{str(datetime.now().time().minute)}_query_response_data.json"

    def __init__(self, api_key, object_structure):
        self.api_key = api_key
        self.object_structure = object_structure
        self.query = None

        self.response = None
        self._dump_list = None  # when not None it's a list of lists
        self.response_data = None  # json object of the _dump_list

        self.url_parameters = {'lean': 1,  # no namespace in JSON
                               '_dropnulls': 0,  # don't pass null values
                               'Accept': 'application/json'}  # set JSON as default output

        # Set up the params dictionary according to documentation
        self.parameters = {**self.url_parameters,  # asterisks (**) unpacks each key:value-pair of the dict
                           'oslc.where': self.query}

        # Set up header dictionary w/ API key according to documentation
        self.headers = {'maxauth': self.api_key}

    def get_response(self, query=None):
        """
        Function to launch the GET request to the Maximo application.
        :param query: The query variable defined in '2. Declare the required
                      variables needed to run and filter your data export result.'
        :return: The respone of the Maximo application.
        """
        print('checking self.query and query (param)')
        if self.query is None and query is None:
            raise ValueError("You're trying to make a request without a query. Set a query before making a request.")

        if self.query is None and query is not None:
            self.query = query

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

    def _get_dump_list(self):
        if self.response is None:
            self.get_response()

        json_data = self.response.json()
        _links = [x.values() for x in json_data['member']]
        dump_list = []
        for url in _links:
            r = requests.get(url, headers=self.headers, params=self.parameters)
            raw_response_data = r.json()
            dump_list.append(raw_response_data)

        self._dump_list = dump_list

    def get_response_data(self, query=None):
        try:
            if self.query is None and query is not None:
                self.query = query

            self._get_dump_list()
            self.response_data = json.dumps(self._dump_list)
        except ValueError as e:
            print(f"The following error is given: {e}")
            print('\n')
            print(f"Can't get response data, because no response is present. To get a response, make sure you use a correct query.")

    def save_response_data(self, filename=_default_file_name, query=None):
        if self.response is None:
            print("No result from resonse yet..")
            print("Making request ")
            self.get_response(query)
            self.save_response_data(query)

        if self.response_data is None:
            self.get_response_data(query)
            self.save_response_data(query)

        if self.response_data is not None and self.response is not None:
            with open(filename, 'w') as output_file:
                json.dump(self._dump_list, output_file, indent=6)

            print(f"JSON object saved as {filename} at {os.getcwd()}")


if __name__ == "__main__":
    qmdb = QueryMaximoDatabase("bWF4YWRtaW46R21iQ1dlbkQyMDE5", "MXWO_SND")
    query = 'siteid="CT1EN2" and worktype="COR" and reportdate>="2018-01-01T00:00:00-00:00" and reportdate<="2018-03-30T00:00:00-00:00"'
    qmdb.get_response(query=query)
