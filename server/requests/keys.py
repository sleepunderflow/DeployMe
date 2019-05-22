from . import responses, crypto, database
from flask import json

def getKey(request, apikey, id):
  secret = request.args.get('secret','')
  if secret == '' or apikey == '' or id == '':
    return responses.generateError("Missing or invalid credentials", 500)
  item = database.getItem(apikey, id, secret)
  if len(item) != 1:
    return responses.generateError("Not authorised", 500)
  item = item[0]

  keys = []
  keysDb = database.getKeys(id)

  for key in keysDb:
    keys.append(key['key'])

  return getItemKeys(id, item, keys)

def getItemKeys(id, item, keysData):
  keys = keysPackage(id)
  # keys.items.append(data)
  keys.itemKeys = keysData
  keys.mainKey = item['mainKey']
  keys.returnKey = item['returnKey']
  keys.commandKey = item['commandKey']
  s = json.dumps( keys, default=lambda x: x.__dict__)
  return s, 200


class keysPackage:
  def __init__(self, itemID):
    self.result = 'ok'
    self.itemID = itemID
    self.mainKey = ''
    self.returnKey = ''
    self.commandKey = ''
    self.itemKeys = []