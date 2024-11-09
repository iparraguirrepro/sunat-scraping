import json
import os
import sys
import asyncio
import time

from playwright.sync_api import sync_playwright
from zipfile import ZipFile

from jrmS00Alias.constants import LABELS, ERROR

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
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=True)
                url = BASE

                context = browser.new_context(
                    user_agent=os.getenv('USER_AGENT')
                )

                page = context.new_page()
                page.goto(url, wait_until='networkidle')

                ruc_input = page.locator('#txtRuc')
                ruc_input.wait_for(state='visible')
                ruc_input.fill(search_data)

                search_button2 = page.query_selector('#divAddRuc #btnBuscarBandAutImp')
                search_button2.click()
                page.wait_for_timeout(2000)

                search_button3 = page.query_selector('#divAcciones #btnBuscarBandAutImp')
                search_button3.click()
                page.wait_for_timeout(4000)

                page.wait_for_load_state('networkidle')

                if page.url != BASE:
                    return {"success": False, "message": "No se encontraron resultados"}

                if read_file:
                    try:
                        with page.expect_download() as download_info:
                            page.query_selector('#divMsg a').click()
                        download = download_info.value

                        file_path = "" + download.suggested_filename
                        download.save_as(file_path)

                        zf = ZipFile(download.suggested_filename, 'r')
                        zf.extractall('unziped')
                        zf.close()

                        os.remove(file_path)

                        new_name = download.suggested_filename.split('.')[0]

                        file_text_path = "./unziped/" + new_name + ".txt"

                        with open(file_text_path, "r") as f:
                            lines = f.readlines()
                            index = 0
                            headers = []
                            for line in lines:
                                if (index == 0):
                                    index = index + 1
                                    headers = line.split('|')
                                    for col in headers:
                                        json_response[LABELS[col]] = ''
                                else:
                                    xl = 0
                                    e_parsed = line.split('|')
                                    for col in e_parsed:
                                        if col == "\n":
                                            json_response["developer"] = "jonatan@iparraguirre.pro"
                                        else:
                                            json_response[LABELS[headers[xl]]] = col
                                        xl = xl + 1
                        f.close()
                        browser.close()
                        os.remove(file_text_path)
                    except:
                        json_response = ERROR
                else:
                    try:
                        detail_headers = page.locator('#divIngManual p')
                        detail_body = page.locator('#divIngManual .col-md-3[style="text-align: center"]')
                        details = detail_body.all_inner_texts()
                        index = 0
                        for line in detail_headers.all_inner_texts():
                            json_response[LABELS[line]] = details[index]
                            index = index + 1
                        browser.close()
                    except:
                        json_response = ERROR
        except:
            time.sleep(3)
            continue
        else:
            scraped = True

    # return json.dumps(json_response, ensure_ascii=False)
    return json_response
