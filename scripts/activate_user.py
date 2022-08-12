#!/usr/bin/python
import sys
import getopt

import requests
from requests.exceptions import ConnectionError, ConnectTimeout

# Change this before running against the production server
# API_END_POINT = "https://pulsars.org.au/api/"
API_END_POINT = "http://localhost:8000/graphql/"

USAGE = \
    """
    Usage: activate_user -a '<admin_username>' -p '<password>' -u '<username>'
    
    -a | --admin
        username of the admin user
       
    -p | --pass
        password of the admin user
        
    -u | --user
        username of the user to be activated
    """

USAGE_SHORT = "Usage: activate_user -a '<admin_username>' -p '<password>' -u '<username>'"


def __get_token(username, password):
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
        response = requests.post(url=API_END_POINT, json={"query": query, "variables": variables})
        json_response = response.json()
        return json_response["data"]["tokenAuth"]["token"]
    except (ConnectionError, ConnectTimeout):
        print(f'API END POINT {API_END_POINT} is not online, please try later')
        sys.exit(1)
    except Exception as ex:
        print(ex)
        return None


def activate_user(token, username):
    headers = {"Authorization": f"JWT {token}"}
    query = \
        """
          mutation ActivateUser($username: String!) {
            activateUser(username: $username) {
              ok,
              errors,
            }
          }
        """

    variables = {
        'username': username,
    }

    try:
        response = requests.post(url=API_END_POINT, json={"query": query, "variables": variables}, headers=headers)
        json_response = response.json()

        if json_response["data"]["activateUser"]["ok"]:
            return f'User with username {username} has been activated.'
        else:
            return f'User activation failed for username {username} due to {json_response["data"]["activateUser"]["errors"][0]}'
    except Exception as ex:
        print(ex)
        return f'Exception while activating user for {username}.'


def main(argv):
    admin_user = None
    password = None
    username = None

    try:
        opts, args = getopt.getopt(argv, "ha:p:u:", ["help", "admin=", "pass=", "user="])

        for opt, opt_val in opts:
            if opt in ("-h", "--help"):
                print(USAGE)
            elif opt in ("-a", "--admin"):
                admin_user = opt_val
            elif opt in ("-p", "--pass"):
                password = opt_val
            elif opt in ("-u", "--user"):
                username = opt_val

        if None in [admin_user, password, username]:
            print(USAGE_SHORT)
            sys.exit(1)
    except getopt.GetoptError as ex:
        print(USAGE_SHORT)
        sys.exit(1)

    admin_token = __get_token(admin_user, password)

    if not admin_token:
        print('Could not obtain a token using these credentials... please check them.')
        sys.exit(1)
    else:
        result = activate_user(admin_token, username)
        print(result)


if __name__ == '__main__':
    arguments = sys.argv[1:]
    main(arguments)
