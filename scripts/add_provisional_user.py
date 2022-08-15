#!/usr/bin/python
import os
import sys
import getopt
from time import sleep

import requests
from get_token import get_token

API_END_POINT = os.environ.get("API_END_POINT")

USAGE = \
    """
    Usage: add_provisional_user -f '<input_file>'
     
    -f | --file
        input file name that contains the email addresses of the provisional users
        Each line in the file should in the following format
            <email_address>,<access_restriction>
            
            where access_restriction can be 'restricted' or 'unrestricted'
    """

USAGE_SHORT = "Usage: add_provisional_user -f '<input_file>'"


def add_provisional_user(token, username, role):
    headers = {"Authorization": f"JWT {token}"}
    query = \
        """
          mutation CreateProvisionalUser($email: String!, $role: String!) {
            createProvisionalUser(email: $email, role: $role) {
              ok,
              emailSent,
              errors,
            }
          }
        """

    variables = {
        'email': username,
        'role': role,
    }

    try:
        response = requests.post(url=API_END_POINT, json={"query": query, "variables": variables}, headers=headers)
        json_response = response.json()

        if json_response["data"]["createProvisionalUser"]["ok"]:
            if not json_response["data"]["createProvisionalUser"]["emailSent"]:
                return f'User with username {username} has been created but mail sending failed'
            else:
                return f'User with username {username} has been created'
        else:
            return f'User creation failed for username {username} due to {json_response["data"]["createProvisionalUser"]["errors"][0]}'
    except Exception as ex:
        print(ex)
        return f'Exception while processing create provisional user for {username}.'


def add_provisional_users(token, user_data):
    results = []
    for data in user_data:
        credentials = data.split(',')
        username = credentials[0].strip()
        role = credentials[1].strip()

        print(f'Creating ({role}) provisional user with the username {username}....')
        result = add_provisional_user(token, username, role)
        print(result)
        results.append(result)
        sleep(1)

    output_file_name = 'provisional_user_result.txt'
    with open(output_file_name, 'w') as fp:
        for item in results:
            # write each item on a new line
            fp.write("%s\n" % item)
        print(f'You can also check the output at {output_file_name}')


def main(argv):
    filename = None

    try:
        opts, args = getopt.getopt(argv, "hf:", ["help", "file="])

        for opt, opt_val in opts:
            if opt in ("-h", "--help"):
                print(USAGE)
            elif opt in ("-f", "--file"):
                filename = opt_val

        if not filename:
            print(USAGE_SHORT)
            sys.exit(1)
    except getopt.GetoptError as ex:
        print(USAGE_SHORT)
        sys.exit(1)

    if not os.path.exists(filename):
        print("File does not exist.")
        sys.exit(2)
    else:
        with open(filename) as f:
            lines = [line.strip() for line in f.readlines()]

    if not lines or not len(lines):
        print("Empty file")
        sys.exit(0)

    admin_token = get_token(API_END_POINT)

    if not admin_token:
        print('Could not obtain a token using these credentials... please check them.')
        sys.exit(1)

    else:

        add_provisional_users(admin_token, lines)


if __name__ == '__main__':
    arguments = sys.argv[1:]
    main(arguments)
