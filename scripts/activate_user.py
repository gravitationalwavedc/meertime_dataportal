#!/usr/bin/python
import os
import sys
import getopt

import requests
from get_token import get_token

API_END_POINT = os.environ.get("API_END_POINT")

USAGE = \
    """
    Usage: activate_user -u '<username>'
        
    -u | --user
        username of the user to be activated
    """

USAGE_SHORT = "Usage: activate_user -u '<username>'"


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
    username = None

    try:
        opts, args = getopt.getopt(argv, "hu:", ["help", "user="])

        for opt, opt_val in opts:
            if opt in ("-h", "--help"):
                print(USAGE)
            elif opt in ("-u", "--user"):
                username = opt_val

        if not username:
            print(USAGE_SHORT)
            sys.exit(1)
    except getopt.GetoptError as ex:
        print(USAGE_SHORT)
        sys.exit(1)

    admin_token = get_token(API_END_POINT)

    if not admin_token:
        print('Could not obtain a token using these credentials... please check them.')
        sys.exit(1)
    else:
        result = activate_user(admin_token, username)
        print(result)


if __name__ == '__main__':
    arguments = sys.argv[1:]
    main(arguments)
