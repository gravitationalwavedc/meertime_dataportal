import logging
import json
import requests as r
from requests.packages.urllib3.util.retry import Retry
import re

from django.conf import settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.propagate = False


def handle_error_msg(errors):
    """
    convenience function for handling errors in response from requests
    """
    if "message" in errors.keys():
        logger.error("Error: %s", errors["message"])
    else:
        logger.error("Error: but no message")


def get_requests_session(url):
    """
    """
    retry_strategy = Retry(total=2, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    adapter = r.adapters.HTTPAdapter(max_retries=retry_strategy)

    session = r.Session()
    session.mount(url, adapter)
    return session


def post_to_slack(msg, timeout=3.0):
    """
    Post a message to slack channel via webhook.
    
    The method accepts a msg string

    timeout is an option parameters which defaults to three seconds to prevent
    posting to slack from slowing down the ingest too much.
    """
    if settings.SLACK_WEBHOOK:
        session = get_requests_session(settings.SLACK_WEBHOOK)

        header = {"Content-type": "application/json"}
        payload = {"text": msg}

        response = session.post(settings.SLACK_WEBHOOK, headers=header, json=payload, timeout=timeout)
        status = response.status_code
        if status != 200:
            logger.error("status %d", status)
        else:
            logger.debug("Slack posting a success: %s", status)
    else:
        logger.info("Slack webhook not configured")


def post_to_slack_if_meertime(msg, proposal):
    """
    Post to slack but only if observation is a meertime observation
    as determined by the proposal code

    return True if proposal matched the used pattern, False otherwise
    """
    meertime_pattern = re.compile("SCI\S*MB\S*")
    if meertime_pattern.match(proposal):
        post_to_slack(msg)
        return True
    else:
        logging.debug("Not posting to slack as observation is not meertime")
        return False
