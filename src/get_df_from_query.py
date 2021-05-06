import pandas as pd
import requests


def get_query_response(query_string, api_key_string, obj_struct_string):
    """
    Function to launch the GET request to the Maximo application.
    :param query_string: The query_string variable defined in '2. Declare the required
                  variables needed to run and filter your data export result.'
    :param api_key_string: 
    :param obj_struct_string: 
    :return: The respone of the Maximo application.
    """
    """
   
    :param query_string: 
    :return: 
    """
    api_url = 'https://maximotest.tbi.nl/maximo/oslc/os/' + obj_struct_string + '?'
    # Set up header dictionary w/ API key according to documentation
    headers = {'maxauth': api_key_string}
    # Set up the params dictionary according to documentation
    params = {'lean': 1,  # no namespace in JSON
              '_dropnulls': 0,  # don't pass null values
              'Accept': 'application/json',  # set JSON as default output
              'oslc.where': query_string}
    # Call the API
    response = requests.get(api_url, headers=headers, params=params)

    if response.status_code == 200:
        print('Success!')
    elif response.status_code == 404:
        print('ApiError')

    return response


def get_href_response(href_url, api_key_string):
    """
    
    :param href_url: 
    :param api_key_string: 
    :return: 
    """
    url = href_url
    headers = {'maxauth': api_key_string}
    url_params = {'lean': 1,
                  '_dropnulls': 0,
                  'Accept': 'application/json'}

    r = requests.get(url, headers=headers, params=url_params)

    response = r.json()

    return response


def get_df_from_query(query_string, api_key_string, obj_struct_string):
    """
    This function combines the different steps for querying the Maximo database.
    :param api_key_string: 
    :param obj_struct_string: 
    :param query_string:
    :return: 
    """
    response_data = get_query_response(api_key_string=api_key_string,
                                       obj_struct_string=obj_struct_string,
                                       query_string=query_string)

    json_data = response_data.json()

    df = pd.DataFrame(json_data['member'])
    
    new_df = pd.DataFrame()
    for href_url in df['href']:
        response_data = get_href_response(href_url=href_url, api_key_string=api_key_string)

        new_df = new_df.append(response_data, ignore_index=True)

    return new_df


if __name__ == '__main__':
    """ In the line bellow fill in your API key without < and > """
    api_key = 'bWF4YWRtaW46R21iQ1dlbkQyMDE5'  # provided to you by a Maximo Consultant
    """ In the line bellow fill in the desired object structure """
    obj_struct = 'GMBLOCATIONS'  # name of the Maximo object structure
    """ In the line bellow fill in the PO number and the SITEID without the < and > """
    query = 'siteid="CT1EN2"'

    data_df = get_df_from_query(query_string=query, api_key_string=api_key, obj_struct_string=obj_struct)
