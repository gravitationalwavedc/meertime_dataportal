import datetime
import json

import jwt
import requests
from django.conf import settings


def get_fluxcal_archive_path(main_project, jname, utc=None, beam=None):
    """
    Get the path to the cleaned fluxcal archives as it is on Ozstar.
    :param project: String of the project name
    :param jname: String of the pulsar name
    :param utc: String of the utc of the observation
    :param beams: Int Number of beams for the pulsar
    :param band: Int Band number for the observation
    :return: String of the path to the fluxcal archives
    """
    # Example path as expected on Ozstar
    if main_project == "MONSPSR":
        # Molonglo data location in /fred/oz002
        if utc is None:
            return f"/ldunn/meertime_dataportal/data/post/{jname}/"
        else:
            return f"/ldunn/meertime_dataportal/data/post/{jname}/{utc}/"
    else:
        # Meertime data location
        if utc is None and beam is None:
            return f"/timing_processed/{jname}/"
        else:
            return f"/timing_processed/{jname}/{utc}/{beam}/"


def request_file_list(path, recursive):
    """
    Requests the file list for a job
    :param path: The relative path to the job to fetch the file list for
    :param recursive: If the file list should be recursive or not
    """

    # Create the jwt token
    jwt_enc = jwt.encode(
        {"userId": 123, "exp": datetime.datetime.now() + datetime.timedelta(days=30)},
        settings.JOB_CONTROLLER_JWT_SECRET,
        algorithm="HS256",
    )

    # Build the data object
    data = {
        "recursive": recursive,
        "path": path,
        "cluster": "meertime",
        "bundle": "da39a3ee5e6b4b0d3255bfef95601890afd80709",
    }

    try:
        # Initiate the request to the job controller
        result = requests.request(
            "PATCH",
            f"{settings.GWCLOUD_JOB_CONTROLLER_API_URL}/file/",
            data=json.dumps(data),
            headers={"Authorization": jwt_enc},
            timeout=30,  # seconds
        )
        result.raise_for_status()

        # Check that the request was successful
        if result.status_code != 200:
            # Oops
            msg = (
                f"Error getting job file list, got error code: "
                f"{result.status_code}\n\n{result.headers}\n\n{result.content}"
            )
            print(msg)
            raise Exception(msg)

        # Parse the response from the job controller
        result = json.loads(result.content)

        return True, result["files"]
    except requests.Timeout:
        return False, "The request timed out"
    except requests.RequestException as e:
        return False, f"An error occurred: {e}"
    except Exception:
        return False, "Error getting job file list"
