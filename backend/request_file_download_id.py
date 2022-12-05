import datetime
import json
import logging

import jwt
import requests
from django.conf import settings


def request_file_download_ids(paths):
    """
    Requests a list of file download ids from the job controller for the provided list of file paths

    If a file download id is generated successfully for all paths, the result will be a tuple of:-
        True, [id, id, id, id, id]

    If any download id fails to be generated, the result will be a tuple of:-
        False, str (Reason for the failure)

    On success, the list of ids is guaranteed to be the same size and order as the provided paths parameter

    :param paths: The list of paths to generate download identifies for

    :return: tuple(result -> bool, details)
    """

    # Create the jwt token
    jwt_enc = jwt.encode(
        {
            'userId': 321,
            'exp': datetime.datetime.now() + datetime.timedelta(minutes=5)
        },
        settings.JOB_CONTROLLER_JWT_SECRET,
        algorithm='HS256'
    )

    # Generate the post payload
    data = {
        'paths': paths,
        'cluster': 'meertime',
        'bundle': 'da39a3ee5e6b4b0d3255bfef95601890afd80709',
    }

    try:
        # Initiate the request to the job controller
        result = requests.request(
            "POST", f"{settings.GWCLOUD_JOB_CONTROLLER_API_URL}/file/",
            data=json.dumps(data),
            headers={
                "Authorization": jwt_enc
            }
        )

        # Check that the request was successful
        if result.status_code != 200:
            # todo: Spruce the exception handling up a bit
            # Oops
            msg = f"Error getting job file download urls, got error code: " \
                  f"{result.status_code}\n\n{result.headers}\n\n{result.content}"
            logging.error(msg)
            raise Exception(msg)

        # Parse the response from the job controller
        result = json.loads(result.content)

        # Return the file ids
        return True, result['fileIds']
    except Exception:
        return False, "Error getting job file download url"


def request_file_download_id(path):
    """
    Requests a file download id from the job controller for the provided file path
    :param path: The path to the file to download
    """
    success, results = request_file_download_ids([path])

    # Return the first result if the request was successful otherwise return the result as it contains an error message
    return success, results[0] if success else results
