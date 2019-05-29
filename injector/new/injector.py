#!/usr/bin/python3
import hashlib
import os
import sys

from injectorModule import *

itemID = 0
BLOCKSIZE = 1024

filesToInject = []
nameToItems = {}
currentlyBeingParsed = None

originalClientLength = -1
internalStructureSize = 24

areItemsInjected = False
areItemsEncrypted = False
requirePrivilegeElevation = False

def writeEmbeddedTools(client):
    '''Append the heades and injected items to a given base binary'''

    mainHeader = createMainHeader()
    writeMainHeader(client, mainHeader)

    # copy content of generated final structure to the base binary in blocks
    injectedFiles = open('.~injector-finalInjectedFiles.temp', 'rb')
    buf = injectedFiles.read(BLOCKSIZE)
    while len(buf) > 0:
        client.write(buf)
        buf = injectedFiles.read(BLOCKSIZE)
    injectedFiles.close()


def writeMainHeader(client, header):
    '''Encode fields of a main header and write it to a client binary'''

    client.write(header['totalSize'].to_bytes(4, 'little'))
    client.write(header['numberOfItems'].to_bytes(4, 'little'))
    client.write(header['fileHash'].encode('ascii'))


def createMainHeader():
    '''calculate a hash of a final injected part, generate main header fields.'''

    global filesToInject
    hasher = hasherHelper.newHasher()

    numberOfItems = len(filesToInject)

    injectedFiles = open('.~injector-finalInjectedFiles.temp', 'rb')

    # size of a main header based on the specs. Required for a correct size calculations.
    totalSize = 74

    buf = injectedFiles.read(BLOCKSIZE)
    while len(buf) > 0:
        totalSize += len(buf)
        hasherHelper.update(hasher, buf)
        buf = injectedFiles.read(BLOCKSIZE)
    injectedFiles.close()

    fileHash = hasherHelper.hexdigest(hasher)

    return {'totalSize': totalSize, 'fileHash': fileHash, 'numberOfItems': numberOfItems}


def encryptItem(item):
    return item


def processOriginalItemToInject(item):
    '''Encrypt the original file to be injected, write the result to a file and update item headers.'''

    singleItem = open('.~injector-singleItem.temp', 'wb')
    item.initializeHeader()
    path = item.path
    with open(path, 'rb') as objectToInject:
        buf = objectToInject.read(BLOCKSIZE)
        while len(buf) > 0:
            item.updateHeader(buf)
            buf = encryptItem(buf)
            singleItem.write(buf)
            buf = objectToInject.read(BLOCKSIZE)
    singleItem.close()


def writeItemHeader(item, target):
    header = item.generateHeader()
    target.write(header['ID'])
    target.write(header['headerLength'])
    target.write(header['payloadLength'])
    target.write(header['flags'])
    target.write(header['fileName'])
    target.write(header['itemHash'])
    target.write(header['additionalData'])


def addEmbeddedTools(item):
    '''Process a file, calculate hash, encrypt and write to a target intermediary file'''

    injectedFiles = open('.~injector-finalInjectedFiles.temp', 'ab')

    processOriginalItemToInject(item)
    writeItemHeader(item, injectedFiles)

    with open('.~injector-singleItem.temp', 'rb') as singleItem:
        buf = singleItem.read(BLOCKSIZE)
        while len(buf) > 0:
            injectedFiles.write(buf)
            buf = singleItem.read(BLOCKSIZE)

    injectedFiles.close()


def parseConfigFile(line):
    '''Parse a line of a configuration file.'''

    global filesToInject, itemID, currentlyBeingParsed, areItemsInjected

    line.strip()
    if line[-1] == '\n':
        line = line[:-1]

    # ignore empty lines
    if line == '':
        pass

    # and comments
    elif line[0] == '#':
        pass

    elif line == '[Item]':
        areItemsInjected = True
        print("Configuring new item. ID: {0}".format(itemID))
        filesToInject.append(item.individualItem.fileToInject(itemID))
        itemID += 1
        currentlyBeingParsed = filesToInject[-1]
    elif line == '[Command]':
        currentlyBeingParsed = None
    else:
        if currentlyBeingParsed == None:
            raise ValueError(
                "Configuration file parsing error! Either not yet supported item being configured or [...] header not specified")
        pos = line.find('=')
        key = line[0:pos]
        value = line[pos+2:-1]

        currentlyBeingParsed.parseConfig(key, value, nameToItems)


def getClientLength(client):
    '''
    Read length of the original client binary. 
    (used as a pointer to the beginning of embedded tools structure)
    '''
    global originalClientLength, internalStructureSize

    buffer = client.read()

    originalClientLength = len(buffer)

    if len(buffer) < internalStructureSize:
        raise ValueError("Empty or too short client binary")


def generateInternalStructureFlags():
    flags = 0
    if areItemsInjected:
        flags |= globalFlags.areItemsInjected
    if areItemsEncrypted:
        flags |= globalFlags.areItemsEncrypted
    if requirePrivilegeElevation:
        flags |= globalFlags.requirePrivilegeElevation

    return flags


def generateInternalStructure():
    '''Generate an internal structure to inject into a client binary (see docs)'''

    header = 0xdeadbeefdeadbeef.to_bytes(8, byteorder='little')

    flags = generateInternalStructureFlags().to_bytes(8, byteorder='little')

    if areItemsInjected:
        injectedDataOffset = originalClientLength.to_bytes(
            8, byteorder='little')
    else:
        injectedDataOffset = int(0).to_bytes(8, byteorder='little')

    return header + flags + injectedDataOffset


def fillInternalStructure(path):
    '''Locate the internal client structure and replace it with generated data'''
    global internalStructureSize

    with open(path, 'rb') as file:
        buffer = file.read()

    # print(buffer)
    location = -1
    for pos in range(0, len(buffer) - internalStructureSize):
        text = buffer[pos:pos+8]
        number = int.from_bytes(text, byteorder='little')
        if number == 0xdeadbeefdeadbeef:
            location = pos
            break
    if location == -1:
        raise ValueError('Byte sequence not found in the source file')

    before = buffer[:location]
    content = generateInternalStructure()
    after = buffer[location+internalStructureSize:]

    buffer = before + bytes(content) + after

    with open(path, 'wb') as file:
        file.write(buffer)


def main():
    # Create those files and make sure they are empty
    tempfile = open('.~injector-finalInjectedFiles.temp', 'wb')
    tempfile2 = open('.~injector-singleItem.temp', 'wb')
    tempfile.close()
    tempfile2.close()

    path = sys.argv[1]
    with open('config.conf', 'r') as configFile:
        for line in configFile:
            parseConfigFile(line)

    for item in filesToInject:
        item.print()
        addEmbeddedTools(item)

    with open(path, 'rb') as client:
        getClientLength(client)

    with open(path, 'ab') as client:
        writeEmbeddedTools(client)

    fillInternalStructure(path)

    os.remove('.~injector-finalInjectedFiles.temp')
    os.remove('.~injector-singleItem.temp')

    print(nameToItems)

main()
