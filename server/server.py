#!/usr/bin/python3

''' 
This is the last moment to turn around and escape the horror
which is this code, I tried to make it nice and relatively secure
but it didn't quite work out.
'''

from flask import Flask
from flask import request
from flask import render_template
from flask import json

from requests import *

'''
Seriously, last chance
'''

database.setup()

'''
You have been warned
'''

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


