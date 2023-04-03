import json
import os
import requests

from classes.Log import Log
from functions.constants import LOG_CRITICAL


def get_flags(flags_id) -> dict:
    """
    Retrieves flagstring for a given flags_id

    Parameters
    ----------
    flags_id : str
        A string containing a flag_id for an existing seed

    Returns
    -------
    str:
        An ff6wc flagstring
    """
    logger = Log()

    #api_url = "https://ff6wc.com/api/flags/" + os.getenv("ff6wc_api_key") + "/" + flags_id
    api_url = "https://dev.ff6worldscollide.com/api/flags/" + "doubledown" + "/" + flags_id

    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("GET", api_url, headers=headers)
    data = response.json()
    print(data)
    if 'url' not in data:
        msg = f'API returned {data} for the following URL:\n{url}'
        logger.show(msg, LOG_CRITICAL)
        return AttributeError
    return data['flags']
