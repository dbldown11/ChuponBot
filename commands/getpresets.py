import json
import urllib.request


def getpresets() -> dict:
    """
    Gets a dictionary of presets from Seedbot's json dump

    Parameters
    ----------
    Nothing

    Returns
    -------
    dict:
        A dictionary of dictionaries containing seedbot presets
        Each dict has the following keys: name, creator_id, creator, flags, description, arguments
    """

    with urllib.request.urlopen("https://storage.googleapis.com/seedbot/user_presets.json") as url:
        print('URL request going out')
        data = json.load(url)
        for presetname in list(data):
            #if 'dev' in data[presetname]['arguments']:
            #    data.pop(presetname)
            if len(data[presetname]['name']) > 90:
                data.pop(presetname)
        return data

# print(list(get_presets()))
