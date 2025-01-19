import json
import logging
import os
import sys
import asyncio
import time
import itertools

from playwright.sync_api import sync_playwright
from zipfile import ZipFile

from jrmS00Alias.constants import LABELS, ERROR

BASE = os.getenv("SCRAP_CONSULTA_URL")


def standardize_key(key):
    key = key.lower()
    key = key.replace(" ", "_")
    key = key.replace(":", "")
    key = key.replace("(", "").replace(")", "")
    return key

def rotate_ua(user_agent_list):
    return itertools.cycle(user_agent_list)


def validateDocument(ruc=None, serie=None, number=None, total=None, date=None):

    print("__START__")

    json_response = {
        "status": True,
    }

    if ruc is None:
        return {"success": False, "message": "Debes ingresar un ruc válido"}

    if len(ruc) != 11:
        return {"success": False, "message": "El RUC debe tener 11 dígitos"}

    if serie is None:
        return {"success": False, "message": "Debes ingresar una serie"}

    if number is None:
        return {"success": False, "message": "Debes ingresar una factura"}

    if total is None:
        return {"success": False, "message": "Debes ingresar un monto valido"}

    if date is None:
        return {"success": False, "message": "Debes ingresar una fecha"}

    scraped = False

    user_agent_list = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
    ]

    while not scraped:
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=True)
                url = BASE
                
                logging.info(url)

                context = browser.new_context(user_agent=os.getenv("USER_AGENT"))

                page = context.new_page()

                print(url)

                page.goto(url, referer = 'https://www.google.com/', wait_until="networkidle")

                numRuc = page.locator("#numRuc")
                numRuc.wait_for(state="visible")
                numRuc.fill(ruc)

                numeroSerie = page.locator("#numeroSerie")
                numeroSerie.wait_for(state="visible")
                numeroSerie.fill(serie)

                numero = page.locator("#numero")
                numero.wait_for(state="visible")
                numero.fill(number)

                fechaEmision = page.locator("#fechaEmision")
                fechaEmision.wait_for(state="visible")
                fechaEmision.fill(date)

                monto = page.locator("#monto")
                monto.wait_for(state="visible")
                monto.fill(monto)

                btnConsultar = page.query_selector("#btnConsultar")
                btnConsultar.click()

                page.wait_for_load_state("networkidle")

                if page.url != BASE:
                    return {"success": False, "message": "No se encontraron resultados"}

                try:
                    resEstado = page.locator("#divResultado #resEstado").text_content()
                    resEstadoRuc = page.locator(
                        "#divResultado #resEstadoRuc"
                    ).text_content()
                    resCondicion = page.locator(
                        "#divResultado #resCondicion"
                    ).text_content()

                    rules = [
                        resEstado == "ACEPTADO",
                        resEstadoRuc == "ACTIVO",
                        resCondicion == "HABIDO",
                    ]
                    if all(rules):
                        json_response = {
                            "status": True,
                            "message": "Documento validado",
                        }
                    else:
                        json_response = ERROR

                    browser.close()
                except:
                    json_response = ERROR
        except:
            time.sleep(3)
            continue
        else:
            scraped = True

    return json_response
