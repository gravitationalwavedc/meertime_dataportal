import os
import json
import copy

from dataportal.tests.testing_utils import (
    CYPRESS_FIXTURE_DIR,
    TEST_DATA_DIR,
    setup_query_test,
)
from dataportal.tests.test_frontend_queries import (
    FOLD_SUMMARY_QUERY,
    FOLD_QUERY,
    FOLD_DETAIL_QUERY,
    PLOT_CONTAINER_QUERY,
    SINGLE_OBSERVATION_QUERY,
    SEARCH_QUERY,
    SEARCH_DETAIL_QUERY,
    SESSION_QUERY,
    SESSION_LIST_QUERY,
)

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
from django.db import connections


class Command(BaseCommand):
    help = 'Regenerates the test json files for the frontend tests.'

    def handle(self, *args, **kwargs):
        # Set up the test environment
        temp_db_name = "test_meertime"

        # Create new database and delete old one if it exists
        with connections['default'].cursor() as cursor:
            cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{temp_db_name}'")
            db_exists = cursor.fetchone()
            if db_exists:
                # Delete old one
                cursor.execute(f'DROP DATABASE {temp_db_name}')
                self.stdout.write(self.style.SUCCESS(f'Dropped existing database {temp_db_name}'))
            # Make new one
            cursor.execute(f'CREATE DATABASE {temp_db_name}')
            self.stdout.write(self.style.SUCCESS(f'Created temporary database {temp_db_name}'))
        settings.DATABASES["default"]["NAME"] = temp_db_name
        self.stdout.write(self.style.SUCCESS(f'Using database {temp_db_name}'))
        call_command('migrate', database="default")
        self.stdout.write(self.style.SUCCESS(f'Migrated {temp_db_name}'))

        client, user, telescope, project, ephemeris, template, \
            pipeline_run, obs, cal = setup_query_test()
        self.stdout.write(self.style.SUCCESS("Setup temp data"))
        client.authenticate(user)
        response = client.execute(FOLD_SUMMARY_QUERY)

        with open(
            os.path.join(TEST_DATA_DIR, "pulsarFoldSummary.json"),
            'w'
        ) as json_file:
            json.dump(response.data, json_file, indent=2)

        response = client.execute(FOLD_QUERY.format(band="All"))
        with open(
            os.path.join(CYPRESS_FIXTURE_DIR, "foldQuery.json"),
            'w'
        ) as json_file:
            json.dump({"data": response.data}, json_file, indent=2)

        response = client.execute(FOLD_QUERY.format(band="UHF"))
        with open(
            os.path.join(CYPRESS_FIXTURE_DIR, "foldQueryFewer.json"),
            'w'
        ) as json_file:
            json.dump({"data": response.data}, json_file, indent=2)

        response = client.execute(FOLD_DETAIL_QUERY)
        with open(
            os.path.join(CYPRESS_FIXTURE_DIR, "foldDetailQuery.json"),
            'w'
        ) as json_file:
            json.dump({"data": response.data}, json_file, indent=2)
        with open(
            os.path.join(CYPRESS_FIXTURE_DIR, "foldDetailQueryNoEphem.json"),
            'w'
        ) as json_file:
            response_copy = copy.deepcopy(response.data)
            test_out = copy.copy({"data": response_copy})
            del test_out["data"]["pulsarFoldResult"]["residualEphemeris"]
            json.dump(test_out, json_file, indent=2)

        response = client.execute(PLOT_CONTAINER_QUERY)
        with open(
            os.path.join(CYPRESS_FIXTURE_DIR, "plotContainerQuery.json"),
            'w'
        ) as json_file:
            json.dump({"data": response.data}, json_file, indent=2)

        response = client.execute(SINGLE_OBSERVATION_QUERY)
        with open(
            os.path.join(TEST_DATA_DIR, "singleObservationQuery.json"),
            "w"
        ) as json_file:
            json.dump({"data": response.data}, json_file, indent=2)
        with open(
            os.path.join(CYPRESS_FIXTURE_DIR, "singleObservationQuery.json"),
            'w'
        ) as json_file:
            response_copy = copy.deepcopy(response.data)
            test_out = copy.deepcopy({"data": response_copy})
            test_out["data"]["pulsarFoldResult"]["edges"][0]["node"]["images"]["edges"] = [
                {
                    "node": {
                        "image": "MeerKAT/SCI-20180516-MB-05/J0125-2327/2023-04-29-06:47:34/2/raw_profile_ftp.png",
                        "cleaned": False,
                        "imageType": "PROFILE",
                        "resolution": "HIGH",
                        "url":
                        "/media/MeerKAT/SCI-20180516-MB-05/J0125-2327/2023-04-29-06%3A47%3A34/2/raw_profile_ftp.png"
                    }
                },
                {
                    "node": {
                        "image": "MeerKAT/SCI-20180516-MB-05/J0125-2327/2023-04-29-06:47:34/2/cleaned_profile_ftp.png",
                        "cleaned": True,
                        "imageType": "PROFILE",
                        "resolution": "HIGH",
                        "url":
                        "/media/MeerKAT/SCI-20180516-MB-05/J0125-2327/2023-04-29-06%3A47%3A34/2/cleaned_profile_ftp.png"
                    }
                },
                {
                    "node": {
                        "image": "MeerKAT/SCI-20180516-MB-05/J0125-2327/2023-04-29-06:47:34/2/raw_profile_fts.png",
                        "cleaned": False,
                        "imageType": "PROFILE_POL",
                        "resolution": "HIGH",
                        "url":
                        "/media/MeerKAT/SCI-20180516-MB-05/J0125-2327/2023-04-29-06%3A47%3A34/2/raw_profile_fts.png"
                    }
                },
                {
                    "node": {
                        "image": "MeerKAT/SCI-20180516-MB-05/J0125-2327/2023-04-29-06:47:34/2/cleaned_profile_fts.png",
                        "cleaned": True,
                        "imageType": "PROFILE_POL",
                        "resolution": "HIGH",
                        "url":
                        "/media/MeerKAT/SCI-20180516-MB-05/J0125-2327/2023-04-29-06%3A47%3A34/2/cleaned_profile_fts.png"
                    }
                },
                {
                    "node": {
                        "image": "MeerKAT/SCI-20180516-MB-05/J0125-2327/2023-04-29-06:47:34/2/raw_phase_time.png",
                        "cleaned": False,
                        "imageType": "PHASE_TIME",
                        "resolution": "HIGH",
                        "url":
                        "/media/MeerKAT/SCI-20180516-MB-05/J0125-2327/2023-04-29-06%3A47%3A34/2/raw_phase_time.png"
                    }
                },
                {
                    "node": {
                        "image": "MeerKAT/SCI-20180516-MB-05/J0125-2327/2023-04-29-06:47:34/2/cleaned_phase_time.png",
                        "cleaned": True,
                        "imageType": "PHASE_TIME",
                        "resolution": "HIGH",
                        "url":
                        "/media/MeerKAT/SCI-20180516-MB-05/J0125-2327/2023-04-29-06%3A47%3A34/2/cleaned_phase_time.png"
                    }
                },
                {
                    "node": {
                        "image": "MeerKAT/SCI-20180516-MB-05/J0125-2327/2023-04-29-06:47:34/2/raw_phase_freq.png",
                        "cleaned": False,
                        "imageType": "PHASE_FREQ",
                        "resolution": "HIGH",
                        "url":
                        "/media/MeerKAT/SCI-20180516-MB-05/J0125-2327/2023-04-29-06%3A47%3A34/2/raw_phase_freq.png"
                    }
                },
                {
                    "node": {
                        "image": "MeerKAT/SCI-20180516-MB-05/J0125-2327/2023-04-29-06:47:34/2/cleaned_phase_freq.png",
                        "cleaned": True,
                        "imageType": "PHASE_FREQ",
                        "resolution": "HIGH",
                        "url":
                        "/media/MeerKAT/SCI-20180516-MB-05/J0125-2327/2023-04-29-06%3A47%3A34/2/cleaned_phase_freq.png"
                    }
                },
                {
                    "node": {
                        "image": "MeerKAT/SCI-20180516-MB-05/J0125-2327/2023-04-29-06:47:34/2/raw_bandpass.png",
                        "cleaned": False,
                        "imageType": "BANDPASS",
                        "resolution": "HIGH",
                        "url": "/media/MeerKAT/SCI-20180516-MB-05/J0125-2327/2023-04-29-06%3A47%3A34/2/raw_bandpass.png"
                    }
                },
                {
                    "node": {
                        "image": "MeerKAT/SCI-20180516-MB-05/J0125-2327/2023-04-29-06:47:34/2/cleaned_bandpass.png",
                        "cleaned": True,
                        "imageType": "BANDPASS",
                        "resolution": "HIGH",
                        "url":
                        "/media/MeerKAT/SCI-20180516-MB-05/J0125-2327/2023-04-29-06%3A47%3A34/2/cleaned_bandpass.png"
                    }
                },
                {
                    "node": {
                        "image": "MeerKAT/SCI-20180516-MB-05/J0125-2327/2023-04-29-06:47:34/2/raw_SNR_cumulative.png",
                        "cleaned": False,
                        "imageType": "SNR_CUMUL",
                        "resolution": "HIGH",
                        "url":
                        "/media/MeerKAT/SCI-20180516-MB-05/J0125-2327/2023-04-29-06%3A47%3A34/2/raw_SNR_cumulative.png"
                    }
                },
                {
                    "node": {
                        "image":
                        "MeerKAT/SCI-20180516-MB-05/J0125-2327/2023-04-29-06:47:34/2/cleaned_SNR_cumulative.png",
                        "cleaned": True,
                        "imageType": "SNR_CUMUL",
                        "resolution": "HIGH",
                        "url": "/media/MeerKAT/SCI-20180516-MB-05/J0125-2327/" +
                            "2023-04-29-06%3A47%3A34/2/cleaned_SNR_cumulative.png"
                    }
                },
                {
                    "node": {
                        "image": "MeerKAT/SCI-20180516-MB-05/J0125-2327/2023-04-29-06:47:34/2/raw_SNR_single.png",
                        "cleaned": False,
                        "imageType": "SNR_SINGLE",
                        "resolution": "HIGH",
                        "url":
                        "/media/MeerKAT/SCI-20180516-MB-05/J0125-2327/2023-04-29-06%3A47%3A34/2/raw_SNR_single.png"
                    }
                },
                {
                    "node": {
                        "image": "MeerKAT/SCI-20180516-MB-05/J0125-2327/2023-04-29-06:47:34/2/cleaned_SNR_single.png",
                        "cleaned": True,
                        "imageType": "SNR_SINGLE",
                        "resolution": "HIGH",
                        "url":
                        "/media/MeerKAT/SCI-20180516-MB-05/J0125-2327/2023-04-29-06%3A47%3A34/2/cleaned_SNR_single.png"
                    }
                }
            ]
            json.dump(test_out, json_file, indent=2)
        with open(
            os.path.join(CYPRESS_FIXTURE_DIR, "singleObservationQueryNoImages.json"),
            'w'
        ) as json_file:
            response_no_image = copy.deepcopy(response.data)
            test_no_image = copy.deepcopy({"data": response_no_image})
            json.dump(test_no_image, json_file, indent=2)

        response = client.execute(SEARCH_QUERY)
        with open(
            os.path.join(CYPRESS_FIXTURE_DIR, "searchQuery.json"),
            'w'
        ) as json_file:
            json.dump({"data": response.data}, json_file, indent=2)

        response = client.execute(SEARCH_DETAIL_QUERY)
        with open(
            os.path.join(CYPRESS_FIXTURE_DIR, "searchDetailQuery.json"),
            'w'
        ) as json_file:
            json.dump({"data": response.data}, json_file, indent=2)

        response = client.execute(SESSION_QUERY.format(cal=cal.id))
        with open(
            os.path.join(CYPRESS_FIXTURE_DIR, "sessionQuery.json"),
            'w'
        ) as json_file:
            json.dump({"data": response.data}, json_file, indent=2)

        response = client.execute(SESSION_LIST_QUERY)
        with open(
            os.path.join(CYPRESS_FIXTURE_DIR, "sessionListQuery.json"),
            'w'
        ) as json_file:
            json.dump({"data": response.data}, json_file, indent=2)
