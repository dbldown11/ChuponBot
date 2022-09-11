import json
import os
import requests

from classes.Log import Log
from functions.constants import LOG_CRITICAL


def generate_seed(flags, seed_desc = None) -> dict:
    """
    Generates a seed using the FF6WC API Key and a given flagset

    Parameters
    ----------
    flags : str
        A string containing a valid set of WC flags

    seed_desc : str (optional)
        A description of the seed

    Returns
    -------
    dict:
        json data
    """
    logger = Log()

    url = "https://ff6wc.com/api/generate"
    if seed_desc:
        payload = json.dumps({
            "key": os.getenv("ff6wc_api_key"),
            "flags": flags,
            "description": seed_desc
        })
        headers = {
            'Content-Type': 'application/json'
        }
    else:
        payload = json.dumps({
            "key": os.getenv("ff6wc_api_key"),
            "flags": flags
        })
        headers = {
            'Content-Type': 'application/json'
        }
    response = requests.request("POST", url, headers=headers, data=payload)
    data = response.json()
    if 'url' not in data:
        msg = f'API returned {data} for the following flagstring:\n{flags}'
        logger.show(msg, LOG_CRITICAL)
        return AttributeError
    return data
