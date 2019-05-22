#!/usr/bin/python3

from flask import Flask
from flask import request
from flask import render_template
from flask import json

from requests import *

database.setup()

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')


@app.route("/getencryptionkeys/<apikey>/<id>", methods=['GET'])
def getKey(apikey, id):
    return keys.getKey(request, apikey, id)


@app.route("/getcommands/<apikey>/<id>", methods=['GET'])
def getCommands(apikey, id):
    return commands.getCommands(request, apikey, id)


@app.route("/registernewobject/<apikey>", methods=['POST'])
def registerNewObject(apikey):
  return adddata.registerNewObject(request, apikey)

@app.route("/management/addnewuser/<apikey>", methods=['GET'])
def addnewuser(apikey):
  return adddata.addUser(apikey)

# For debug - dump DB

# @app.route("/management/printeverything", methods=['GET'])
# def printeverything():
#   result = database.printEverything()
#   return result


