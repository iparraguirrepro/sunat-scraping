import json
import os
import sys
import asyncio
import time

from playwright.sync_api import sync_playwright

from jcrS00Alias.constants import LABELS, ERROR

BASE = os.getenv('SCRAP_URL')


def standardize_key(key):
    key = key.lower()
    key = key.replace(' ', '_')
    key = key.replace(':', '')
    key = key.replace('(', '').replace(')', '')
    return key


def run(search_data=None, read_file=False):
    json_response = {
        "status": True,
    }

    if search_data is None:
        return {"success": False, "message": "Debes ingresar un ruc válido"}

    if len(search_data) != 11:
        return {"success": False, "message": "El RUC debe tener 11 dígitos"}

    scraped = False
    while not scraped:
        try:
            print('doRequest')
        except:
            time.sleep(3)
            continue
        else:
            scraped = True

    # return json.dumps(json_response, ensure_ascii=False)
    return json_response
