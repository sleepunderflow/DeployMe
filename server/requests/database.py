import sqlalchemy as db

engine = None
connection = None
metadata = None
items = None
keys = None
commands = None
users = None

''' Fill in the global variables, connect to a db '''
def setup():
  global engine, connection, metadata, items, keys, commands, users
  engine = db.create_engine('sqlite:///DeployMe.db')
  connection = engine.connect()
  metadata = db.MetaData()
  items = db.Table('items', metadata, autoload=True, autoload_with=engine)
  keys = db.Table('keys', metadata, autoload=True, autoload_with=engine)
  commands = db.Table('commands', metadata, autoload=True, autoload_with=engine)
  users = db.Table('users', metadata, autoload=True, autoload_with=engine)
  metadata.create_all(engine)

def addUser(newUUID):
  global db, connection, users
  query = db.insert(users).values(apiKey=newUUID) 
  ResultProxy = connection.execute(query)


def getUser(apiKey):
  global db, connection, users
  query = db.select([users]).where(users.columns.apiKey == apiKey)
  ResultProxy = connection.execute(query)
  ResultSet = ResultProxy.fetchall()
  return ResultSet

# For debug - dump everything

# def printEverything():
#   global db, connection, users, keys, items, commands
#   end = 'Users: '
#   query = db.select([users])
#   ResultProxy = connection.execute(query)
#   ResultSet = ResultProxy.fetchall()
#   end += str(ResultSet)
#   query = db.select([keys])
#   ResultProxy = connection.execute(query)
#   ResultSet = ResultProxy.fetchall()
#   end += '\nKEYS: ' + str(ResultSet)
#   query = db.select([items])
#   ResultProxy = connection.execute(query)
#   ResultSet = ResultProxy.fetchall()
#   end += '\nITEMS: ' + str(ResultSet)
#   query = db.select([commands])
#   ResultProxy = connection.execute(query)
#   ResultSet = ResultProxy.fetchall()
#   end += '\nCOMMANDS: ' + str(ResultSet)
#   return (end)

''' Add an item to a database and return an itemID '''
def addItem(itemID, ownerApiKey, accessApiKey, secret, mainKey, returnKey, commandKey):
  global db, connection, items
  query = db.insert(items).values(itemID=itemID, ownerApiKey=ownerApiKey, accessApiKey=accessApiKey, \
    secret=secret, mainKey=mainKey, returnKey=returnKey, commandKey=commandKey) 
  ResultProxy = connection.execute(query)

  query = db.select([items]).where(db.and_(items.columns.ownerApiKey == ownerApiKey,  \
    items.columns.accessApiKey==accessApiKey, items.columns.secret==secret,  \
      items.columns.mainKey==mainKey, items.columns.returnKey==returnKey, \
        items.columns.commandKey==commandKey))
  ResultProxy = connection.execute(query)
  ResultSet = ResultProxy.fetchall()
  return ResultSet[0]['itemID']

''' Check if there already is an item in a database with the same item ID or accessApiKey '''
def checkIfAvailable(itemID, accessApiKey):
  query = db.select([items]).where( \
    db.or_(items.columns.accessApiKey==accessApiKey, items.columns.itemID==itemID))
  ResultProxy = connection.execute(query)
  ResultSet = ResultProxy.fetchall()
  return len(ResultSet) == 0

def addKeys(keysToAdd):
  global db, connection, keys
  query = db.insert(keys)
  resultProxy = connection.execute(query, keysToAdd)

def addCommands(commandsToAdd):
  global db, connection, commands
  query = db.insert(commands)
  resultProxy = connection.execute(query, commandsToAdd)

def getItem(apikey, itemID, secret):
  query = db.select([items]).where(db.and_(items.columns.accessApiKey==apikey, \
    items.columns.secret==secret, items.columns.itemID == itemID))
  ResultProxy = connection.execute(query)
  ResultSet = ResultProxy.fetchall()
  return ResultSet

def getKeys(itemID):
  query = db.select([keys]).where(items.keys.itemID==itemID)
  ResultProxy = connection.execute(query)
  ResultSet = ResultProxy.fetchall()
  return ResultSet

def getCommands(itemID):
  query = db.select([commands]).where(commands.keys.itemID==itemID)
  ResultProxy = connection.execute(query)
  ResultSet = ResultProxy.fetchall()
  return ResultSet