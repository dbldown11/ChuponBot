import json
import os
import requests

from classes.Log import Log
from functions.constants import LOG_CRITICAL


def get_seedinfo(url, seed_desc = None) -> dict:
    """
    Retrieves flag, hash, and other info for an existing FF6WC seed

    Parameters
    ----------
    url : str
        A string containing a url for an FF6WC seed

    seed_desc : str (optional)
        A description of the seed

    Returns
    -------
    dict:
        json data
    """
    logger = Log()

    #api_url = "https://ff6wc.com/api/seed/" + os.getenv("ff6wc_api_key") + "/" + url.split("/")[-1]
    api_url = "https://dev.ff6worldscollide.com/api/seed/" + "doubledown" + "/" + url.split("/")[-1]

    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", api_url, headers=headers)
    print(response.content)
    data = response.json()
    if 'url' not in data:
        msg = f'API returned {data} for the following URL:\n{url}'
        logger.show(msg, LOG_CRITICAL)
        return AttributeError
    return data
