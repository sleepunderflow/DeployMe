from . import responses, database
from flask import json


def getCommands(request, apikey, id):
  secret = request.args.get('secret','')
  if secret == '' or apikey == '' or id == '':
    return responses.generateError("Missing or invalid credentials", 500)
  item = database.getItem(apikey, id, secret)
  if len(item) != 1:
    return responses.generateError("Not authorised", 500)
  item = item[0]

  commands = []
  commandsDb = database.getCommands(id)

  for command in commandsDb:
    commands.append({"command":command['command'], "flags":command['flags']})

  return getItemCommands(id, commands)


def getItemCommands(id, data):
  commands = commandsPackage(id)
  # keys.items.append(data)
  commands.commands = data
  s = json.dumps( commands, default=lambda x: x.__dict__)
  return s, 200


class commandsPackage:
  def __init__(self, itemID):
    self.result = 'ok'
    self.itemID = itemID
    self.commands = []