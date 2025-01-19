from flask import Flask, jsonify, request
from dotenv import load_dotenv

from consultaUnificadaLibre.consulta import validateDocument
from jrmS00Alias.jrmS00Alias import run

load_dotenv()

app = Flask(__name__)

@app.route('/jrmS00Alias/<ruc>', methods=['GET'])
def jrmS00Alias(ruc):
    scrapResponse = run(ruc, True)
    return jsonify(scrapResponse)


@app.route('/consultaUnificadaLibre', methods=['GET'])
def consultaUnificadaLibre():
    ruc = request.args.get('ruc')
    total = request.args.get('total')
    date = request.args.get('date')
    serie = request.args.get('serie')
    number = request.args.get('number')
    scrapResponse = validateDocument(ruc, serie, number, total, date)
    return jsonify(scrapResponse)

@app.route('/jrmS00Alias/longitudes/<ruc>', methods=['GET'])
def jrmS00AliasChar(ruc):
    scrapResponse = run(ruc, False)
    return jsonify(scrapResponse)


app.run(host="0.0.0.0", port="8080", debug=True, use_reloader=True)
