#!/usr/bin/python3
import sys
import hashlib

def createMainHeader():
  pass

itemID = 0
BLOCKSIZE = 65536

hasher = hashlib.sha256()

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

def addEmbeddedTools(client, path):
  tempfile = open('.~injector.temp', 'wb')
  tempfile2 = open('.~injector2.temp','wb')
  header = createIndividualHeader(path, 0)
  with open(path, 'rb') as objectToInject:
    buf = objectToInject.read(BLOCKSIZE)
    while len(buf) > 0:
      buf = encryptItem(buf)
      tempfile2.write(buf)
      header = updateIndividualHeader(buf, header)
      buf = objectToInject.read(BLOCKSIZE)
  tempfile2.close()

  #TODO: header[1], header[1], [2],[4] - static length
  totalLength = 106 + header[1]
  tempfile.write(header[0].to_bytes(2, byteorder='little'))
  tempfile.write(totalLength.to_bytes(4, byteorder='little'))
  fileName = header[2]
  if len(fileName) > 64:
    #TODO correct
    raise ValueError(something)
  else:
    while len(fileName) != 64:
      fileName += '\0'
  tempfile.write(fileName.encode('ascii'))
  tempfile.write(header[3].encode('ascii'))
  tempfile.write(header[4].to_bytes(4, byteorder='little'))
  with open('.~injector2.temp','rb') as tempfile2:
    buf = tempfile2.read(BLOCKSIZE)
    while len(buf) > 0:
      tempfile.write(buf)
      buf = tempfile2.read(BLOCKSIZE)

  print(header)
  tempfile.close()

def main():
  path = sys.argv[1]
  objectToInjectPath = sys.argv[2]

  client = open(path, 'ab')
  addEmbeddedTools(client, objectToInjectPath)

main()