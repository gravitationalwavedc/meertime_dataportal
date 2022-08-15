#!/usr/bin/python3.9
import os
import sys
import requests
from requests.exceptions import ConnectionError, ConnectTimeout


def get_token(api_end_point):
    username = os.environ.get('API_ADMIN_USER')
    password = os.environ.get('API_ADMIN_PASS')

    if None in (username, password):
        print(f'Cannot get username or password, please make sure you have exported those.')
        sys.exit(1)

    query = \
        """
          mutation TokenAuth($username: String!, $password: String!) {
            tokenAuth(input:{username: $username, password: $password}) {
              token
              payload 
              refreshExpiresIn 
            }
          }
        """

    variables = {
        'username': username,
        "password": password,
    }

    try:
        response = requests.post(url=api_end_point, json={"query": query, "variables": variables})
        json_response = response.json()
        return json_response["data"]["tokenAuth"]["token"]
    except (ConnectionError, ConnectTimeout):
        print(f'API END POINT {api_end_point} is not online, please try later')
        sys.exit(1)
    except Exception as ex:
        print(ex)
        return None
