import sqlalchemy as db
import uuid
import os

try:
  os.remove('DeployMe.db')
except FileNotFoundError:
  pass

engine = db.create_engine('sqlite:///DeployMe.db')
connection = engine.connect()
metadata = db.MetaData()

items = db.Table('items', metadata,
  db.Column('itemID', db.String(36), primary_key=True),
  db.Column('ownerApiKey', db.String(36), nullable=False),
  db.Column('accessApiKey', db.String(36), nullable=False),
  db.Column('secret', db.String(255), nullable=False),
  db.Column('returnKey', db.String(255), nullable=False),
  db.Column('commandKey', db.String(255), nullable=False)
)

users = db.Table('users', metadata,
  db.Column('userID', db.Integer(), primary_key=True),
  db.Column('apiKey', db.String(36), nullable=False)
)

keys = db.Table('keys', metadata,
  db.Column('keyID', db.Integer(), primary_key=True),
  db.Column('itemID', db.String(36), nullable=False),
  db.Column('key', db.String(255), nullable=False)
)

commands = db.Table('commands', metadata,
  db.Column('commandID', db.Integer(), primary_key=True),
  db.Column('itemID', db.String(36), nullable=False),
  db.Column('command', db.String(255), nullable=False),
  db.Column('flags', db.Integer(), nullable=False)
)

metadata.create_all(engine) #Creates the table

# Add our main base user and print back the API key
main_user_api = uuid.uuid4()
print(main_user_api)

query = db.insert(users).values(userID=1, apiKey=str(main_user_api)) 
ResultProxy = connection.execute(query)
