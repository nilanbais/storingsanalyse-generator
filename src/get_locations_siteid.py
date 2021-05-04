import pandas as pd
import json
import requests
import os

while 1:
    if os.getcwd().endswith('storingsanalyse-generator'):
        break
    else:
        os.chdir('..')

# Todo: maak van dit script een herbruikbaar script/module voor het ophalen van een payload op basis van een query
#  en de andere parameters die van belang zijn

""" In the line bellow fill in your API key without < and > """
api_key = 'bWF4YWRtaW46R21iQ1dlbkQyMDE5'  # provided to you by a Maximo Consultant
""" In the line bellow fill in the desired object structure """
obj_struct = 'GMBLOCATIONS'  # name of the Maximo object structure
""" In the line bellow fill in the PO number and the SITEID without the < and > """
query = 'siteid="CT1EN2"'


def get_query_response(query):
    """
    Function to launch the GET request to the Maximo application.
    :param query: The query variable defined in '2. Declare the required
                  variables needed to run and filter your data export result.'
    :return: The respone of the Maximo application.
    """
    api_url = 'https://maximotest.tbi.nl/maximo/oslc/os/' + obj_struct + '?'
    # Set up header dictionary w/ API key according to documentation
    headers = {'maxauth': api_key}
    # Set up the params dictionary according to documentation
    params = {'lean': 1,  # no namespace in JSON
              '_dropnulls': 0,  # don't pass null values
              'Accept': 'application/json',  # set JSON as default output
              'oslc.where': query}
    # Call the API
    response = requests.get(api_url, headers=headers, params=params)

    if response.status_code == 200:
        print('Success!')
    elif response.status_code == 404:
        print('ApiError')

    return response


def get_href_response(href_url):
    """

    :param href_url:
    :return:
    """
    url = href_url
    headers = {'maxauth': api_key}
    url_params = {'lean': 1,
                  '_dropnulls': 0,
                  'Accept': 'application/json'}

    r = requests.get(url, headers=headers, params=url_params)

    response = r.json()

    return response


response_data = get_query_response(query)

json_data = response_data.json()

df = pd.DataFrame(json_data['member'])

new_df = pd.DataFrame()

for value in df['href']:
    response_data = get_href_response(href_url=value)

    new_df = new_df.append(response_data, ignore_index=True)

new_df2 = new_df[['description', 'location']]

new_df2.to_json('res\\location_description_map.json')
