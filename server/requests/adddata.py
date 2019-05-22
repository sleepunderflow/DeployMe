from . import database, responses, crypto
import uuid
from flask import json
import binascii

''' Add all the structures for a client to a database based on the request '''
def registerNewObject(request, apikey):
  # Check if there is a user with the requred API key already in the database
  result = database.getUser(apikey)
  if len(result) != 1:
    return responses.generateError("wrong API key", 500)

  # Extract data out of the request and generate keys

  # data = request.form['data']
  data = request.get_json(force=True)
  commands = data['commands']
  numberOfKeys = int(data['numberofkeys'])
  mainKey = crypto.generateKeys(1, 256)[0]['key']
  returnKey = crypto.generateKeys(1, 256)[0]['key']
  commandKey = crypto.generateKeys(1, 256)[0]['key']
  ownerApiKey = apikey
  secret = str(uuid.uuid4())

  # Generate new item ID and access API key and verify if they are available
  requestedItemID = ''
  available = False
  while not available:
    accessApiKey = str(uuid.uuid4())
    requestedItemID = str(uuid.uuid4())

    available = database.checkIfAvailable(requestedItemID, accessApiKey)

  itemID = database.addItem(requestedItemID, ownerApiKey, accessApiKey, secret, mainKey, returnKey, commandKey)

  # Check if the itemID retruned from the db is the same as requested
  if requestedItemID != itemID:
    return responses.generateError("something went wrong", 500)

  # generate item keys and fill in objects
  keys = crypto.generateKeys(numberOfKeys, 256)
  for i in range(numberOfKeys):
    keys[i]['itemID'] = itemID

  database.addKeys(keys)

  # Encrypt all the requested commands, add to the structures and add to db
  commandBytes = binascii.unhexlify(commandKey)
  encryptedCommands = []
  if len(commands) > 0:
    for command in commands:
      print(command)
      encryptedCommands.append({"itemID":itemID, \
        "flags":command['flags'], \
          "command":crypto.encrypt(commandBytes, command['command'].encode('utf-8'))})
  
  database.addCommands(encryptedCommands)

  # extract the keys to a single array
  itemKeys = []
  for i in keys: 
    itemKeys.append(i['key'])

  # return json
  return json.dumps( {"result":"ok", "itemID":itemID, "accessApiKey":accessApiKey, \
    "secret":secret, "itemKeys":itemKeys, "returnKey": returnKey, "mainKey":mainKey}, \
       default=lambda x: x.__dict__)


''' Register a new user - only possible ifrequested by the first (main) user '''
def addUser(apikey):
  result = database.getUser(apikey)
  if len(result) != 1:
    return responses.generateError("wrong API key", 500)
  if result[0].userID == 1:
    newUUID = str(uuid.uuid4())
    database.addUser(newUUID)
    return json.dumps( {"result":"ok", "apiKey":apikey, "newApiKey":newUUID}, default=lambda x: x.__dict__)
  else:
    return responses.generateError("not authorised API key", 500)
