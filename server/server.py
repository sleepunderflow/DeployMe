#!/usr/bin/python3

from flask import Flask
from flask import request
from flask import render_template
from flask import json
app = Flask(__name__)

@app.route("/")
def hello():
    return render_template('index.html')

keys = ['abcd', '1234']

def getDataForItem(apikey, id, secret):
  # Get data from DB
  if apikey == 'abcd' and id == '123' and secret == 'secret':
    return [{'item1': '0x123'}, {'item2': '0x1234'}, {'item3': '0x1235'}]
  else:
    return None

def generateError(message, errorNumber):
  return json.jsonify(
    result="error",
    error=errorNumber,
    message=message), errorNumber

@app.route("/getencryptionkeys/<apikey>/<id>", methods=['GET'])
def getKey(apikey, id):
    error = None
    secret = request.args.get('secret','')
    if secret == '':
      return generateError("Missing or invalid secret", 500)
    data = getDataForItem(apikey, id, secret)
    if data == None:
      return generateError("Not authorised", 500)
    return getItemKeys(apikey, id, data)
# # if request.method == 'GET':
# if request.args.get('type','') != '':
#   return "Key for {0} type {1}".format(apikey, request.args.get('type',''))
#   # request.form['type']
# else:
#   error = 'No key type provided'
# return "Error {}".format(error), 500

def getItemKeys(apikey, id, data):
  keys = keysPackage(apikey, id)
  # keys.items.append(data)
  keys.items = data
  s = json.dumps( keys, default=lambda x: x.__dict__)
  return s, 200


class keysPackage:
  def __init__(self, apikey, itemID):
    self.result = "ok"
    self.items = []
    self.apikey = apikey
    self.itemID = itemID


class MyEncoder(json.JSONEncoder):
  def default(self, o):
    return o.items.__dict__