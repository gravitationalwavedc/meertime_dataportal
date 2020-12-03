# this is an example of how to ingest via graphql

import json
import logging
import requests as r
from requests.packages.urllib3.util.retry import Retry
from argparse import ArgumentParser

logger = logging.getLogger("ingest_via_graphql")
logger.setLevel(logging.INFO)
logger_fh = logging.FileHandler("graphql_ingest.log")
logger_fh.setLevel(logging.INFO)
logger_ch = logging.StreamHandler()
logger_ch.setLevel(logging.ERROR)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger_fh.setFormatter(formatter)
logger_ch.setFormatter(formatter)

logger.addHandler(logger_fh)
logger.addHandler(logger_ch)


target_mutation = """
mutation ($name: String!, $raj: String!, $decj: String!) {
  createTarget(name: $name, raj: $raj, decj: $decj) {
    target {
      name,      
    }
  }
}
"""

target_variables = """
{
    "name": "%s",
    "raj": "%s",
    "decj": "%s"
}
"""


def handle_error_msg(errors):
    if "message" in errors.keys():
        logger.error("Error: %s", errors["message"])
    else:
        logger.error("Error: but no message")


def get_requests_session(graphQL_url):
    retry_strategy = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    adapter = r.adapters.HTTPAdapter(max_retries=retry_strategy)

    session = r.Session()
    session.mount(graphQL_url, adapter)
    return session


def post_to_graphql(vars_values, graphQL_url, token, mutation, vars_mutation, session):

    header = {"Authorization": "JWT %s" % token}

    payload = {"query": mutation, "variables": vars_mutation % vars_values}
    logger.debug(f"Using mutation {mutation}")
    logger.debug(f"Using mutation vars {vars_mutation}")
    logger.debug(f"Using with values {vars_values}")

    logger.debug(f"Complete payload:\n{payload}")

    response = session.post(graphQL_url, headers=header, data=payload, timeout=(15, 15))
    status = response.status_code
    content = json.loads(response.content)

    if status != 200:
        logger.error("status %d", status)
        if "errors" in content.keys():
            errors = content["errors"][0]
            handle_error_msg(errors)
        else:
            logger.error("Non-200 but no error: %s", content)
        return False
    elif "errors" in content.keys():
        errors = content["errors"][0]
        handle_error_msg(errors)
        return False
    else:
        logger.info("Success: %s %s %s %s", vars_values[0], vars_values[1], vars_values[2], content)
        return True


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-T", "--target", nargs=3, help="Create a target, provide name, raj and decj")

    parser.add_argument("-t", "--token", nargs="?", help="JWT token")
    parser.add_argument("-u", "--url", nargs="?", help="GraphQL URL")
    parser.add_argument("-v", "--verbose", action="store_true", default=False, help="Increase verbosity")
    parser.add_argument("-vv", "--very-verbose", action="store_true", default=False, help="Further increase verbosity")
    args = parser.parse_args()

    if args.verbose or args.very_verbose:
        logger.setLevel(logging.DEBUG)
        logger_ch.setLevel(logging.DEBUG)
        if args.very_verbose:
            try:
                import http.client as http_client
            except ImportError:
                # Python 2
                import httplib as http_client
            http_client.HTTPConnection.debuglevel = 1

    token = args.token
    if not token:
        print("Please provide a JWT token")
    graphQL_url = args.url
    if not graphQL_url:
        print("Please provide a GraphQL URL")

    session = get_requests_session(graphQL_url)
    if args.target:
        post_to_graphql(tuple(args.target), graphQL_url, token, target_mutation, target_variables, session)
