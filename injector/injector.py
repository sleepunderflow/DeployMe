#!/usr/bin/python3
import sys
import hashlib
import ntpath

itemID = 0
BLOCKSIZE = 65536
hasher = hashlib.sha256()

itemsToInject = []

def writeEmbeddedTools(client):
  mainHeader = createMainHeader()
  client.write(mainHeader['totalSize'].to_bytes(4, 'little'))
  client.write(mainHeader['numberOfItems'].to_bytes(2, 'little'))
  client.write(mainHeader['fileHash'].encode('ascii'))
  tempfile = open('.~injector.temp', 'rb')
  buf = tempfile.read(BLOCKSIZE)
  while len(buf) > 0:
    client.write(buf)
    buf = tempfile.read(BLOCKSIZE)
  tempfile.close()

def path_leaf(path):
  head, tail = ntpath.split(path)
  return tail or ntpath.basename(head)

class itemToInject:
  def itemToInject():
    self.name = ""
    self.path = ""
    self.permissions = ""

  def setPath(self, path):
    self.path = path
    self.name = path_leaf(path)

  def setPermissions(self, permissions):
    self.permissions = permissions

  def print(self):
    print("Name = {0}, Path = {1}, Permissions = {2}".format(self.name, self.path, self.permissions))

  def validate(self):
    if self.name == '' or self.name == '\n':
      raise ValueError("Name not set")
    if self.path == '' or self.path == '\n':
      raise ValueError("Path not set")

def createMainHeader():
  global hasher
  tempfile = open('.~injector.temp', 'rb')
  hasher = hashlib.sha256()
  buf = tempfile.read(BLOCKSIZE)
  totalSize = 38
  numberOfItems = len(itemsToInject)
  while len(buf) > 0:
    totalSize += len(buf)
    hasher.update(buf)
    buf = tempfile.read(BLOCKSIZE)
  tempfile.close()
  fileHash = hasher.hexdigest()
  return {'totalSize':totalSize, 'fileHash':fileHash, 'numberOfItems':numberOfItems}


def createIndividualHeader(name, permissions):
  global itemID
  global hasher
  hasher = hashlib.sha256()
  currentItemID = itemID
  itemID += 1
  return currentItemID, 0, name, '', permissions

def encryptItem(item):
  return item

def updateIndividualHeader(item, header):
  global hasher
  fileHash = header[3]
  hasher.update(item)
  fileHash = hasher.hexdigest()
  return header[0], header[1] + len(item), header[2], fileHash, header[4]

def addEmbeddedTools(item):
  item.validate()
  path = item.path
  name = item.name
  permissions = item.permissions

  tempfile = open('.~injector.temp', 'ab')
  tempfile2 = open('.~injector2.temp','wb')
  header = createIndividualHeader(name, permissions)
  with open(path, 'rb') as objectToInject:
    buf = objectToInject.read(BLOCKSIZE)
    while len(buf) > 0:
      header = updateIndividualHeader(buf, header)
      buf = encryptItem(buf)
      tempfile2.write(buf)
      buf = objectToInject.read(BLOCKSIZE)
  tempfile2.close()

  totalLength = 105 + header[1]
  tempfile.write(header[0].to_bytes(2, byteorder='little'))
  tempfile.write(totalLength.to_bytes(4, byteorder='little'))
  fileName = header[2]
  if len(fileName) > 64:
    #TODO correct
    raise ValueError("Length of the given file name is greater than 64")
  else:
    while len(fileName) != 64:
      fileName += '\0'
  tempfile.write(fileName.encode('ascii'))
  tempfile.write(header[3].encode('ascii'))
  tempfile.write(header[4].encode('ascii'))
  with open('.~injector2.temp','rb') as tempfile2:
    buf = tempfile2.read(BLOCKSIZE)
    while len(buf) > 0:
      tempfile.write(buf)
      buf = tempfile2.read(BLOCKSIZE)

  print(header)
  tempfile.close()

def main():
  tempfile = open('.~injector.temp', 'wb')
  tempfile2 = open('.~injector2.temp','wb')
  tempfile.close()
  tempfile2.close()

  path = sys.argv[1]
  configFile = open('config.conf', 'r')
  for line in configFile:
    parseConfigFile(line)
  for i in itemsToInject:
    i.print()

  client = open(path, 'ab')
  for item in itemsToInject:
    addEmbeddedTools(item)
  writeEmbeddedTools(client)

def parseConfigFile(line):
  global itemsToInject
  if line == '' or line == '\n':
    pass
  elif line == '[Item]\n':
    itemsToInject.append(itemToInject())
  else:
    pos = line.find('=')
    key = line[0:pos]
    pos = line.find('"', pos)
    pos += 1
    pos2 = line.find('"', pos)
    while line[pos2-1] == '\\':
      pos2 += 1
      pos2 = line.find('"', pos2)
    value = line[pos:pos2]

    if key == 'path':
      itemsToInject[-1].setPath(value)
    elif key == 'permissions':
      itemsToInject[-1].setPermissions(value)
    else:
      raise ValueError("Wrong configuration line {0}".format(line))

main()