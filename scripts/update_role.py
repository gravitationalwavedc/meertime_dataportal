#!/usr/bin/python
import os
import sys
import getopt

import requests
from get_token import get_token

API_END_POINT = os.environ.get("API_END_POINT")

USAGE = \
    """
    Usage: update_role -u '<username> -r '<role>'
        
    -u | --user
        username of the user to be deactivated
        
    -r | --role
        role (restricted/unrestricted) of the user
    """

USAGE_SHORT = "Usage: update_role -u '<username>' -r '<role>'"


def update_role(token, username, role):
    headers = {"Authorization": f"JWT {token}"}
    query = \
        """
          mutation UpdateRole($username: String!, $role: String!) {
            updateRole(username: $username, role: $role) {
              ok,
              errors,
            }
          }
        """

    variables = {
        'username': username,
        'role': role,
    }

    try:
        response = requests.post(url=API_END_POINT, json={"query": query, "variables": variables}, headers=headers)
        json_response = response.json()

        if json_response["data"]["updateRole"]["ok"]:
            return f'Role for the {username} has been updated to {role}.'
        else:
            return f'Updating role for username {username} failed due to {json_response["data"]["updateRole"]["errors"][0]}'
    except Exception as ex:
        print(ex)
        return f'Exception while updating role for the user {username}.'


def main(argv):
    username = None
    role = None

    try:
        opts, args = getopt.getopt(argv, "hu:r:", ["help", "user=", "role="])

        for opt, opt_val in opts:
            if opt in ("-h", "--help"):
                print(USAGE)
            elif opt in ("-u", "--user"):
                username = opt_val
            elif opt in ("-r", "--role"):
                role = opt_val

        if None in (username, role):
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
        result = update_role(admin_token, username, role)
        print(result)


if __name__ == '__main__':
    arguments = sys.argv[1:]
    main(arguments)
