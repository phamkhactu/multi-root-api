from flask_api import status
from flask import Flask,jsonify
from flask import request, redirect, url_for
from flask_cors import CORS
import logging
logging.basicConfig(level= logging.INFO)
import helpers
import json
import controller

app = Flask(__name__)
CORS(app)


@app.route('/')
def GetStatusService():
    return "start",status.HTTP_200_OK



@app.route("/MultiNew", methods=['POST'])
def multi():
    content = request.get_json()  
    code = helpers.check_valid_input(content)
    if code != 200:
        return {}, code
    return json.dumps(controller.summary(content)).encode('utf8')

app.run(host='0.0.0.0', port=9988)