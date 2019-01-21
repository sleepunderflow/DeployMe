#!/usr/bin/python3
import hashlib
import ntpath
import os
import sys

itemID = 0
BLOCKSIZE = 65536
hasher = hashlib.sha256()

filesToInject = []
nameToItems = {}
currentlyBeingParsed = None

originalClientLength = -1
internalStructureSize = 24

areItemsInjected = False
areItemsEncrypted = False


def resetHasher():
    global hasher
    hasher = hashlib.sha256()


def strToBool(text):
    '''Tries to convert a string to True/False. If incorrect throws an exception.'''

    if text.upper() == 'TRUE':
        return True
    if text.upper() == 'FALSE':
        return False
    raise ValueError("Value expected to be true/false, got {0}".format(text))


def path_leaf(path):
    '''Returns the file name given a path.'''

    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


class fileToInject:
    '''Class representing a single file that is meant to be injected to the resulting binary.'''

    def __init__(self, ID):
        '''Constructor for the class. Sets default values for item.'''

        self.ID = ID
        self.name = ""
        self.path = ""
        self.permissions = "755"
        self.setDefaultFlags()
        self.hash = ""
        # set length to a header size
        self.length = 107

    def setDefaultFlags(self):
        '''Sets default flags for the file. For details check the documentation.'''

        self.flags = 0
        self.flags |= 1  # remove-after-use = true

    def setPath(self, path):
        '''Sets a path of a file to inject and a filename that will be included in the resulting binary.'''

        self.path = path
        self.name = path_leaf(path)

    def setPermissions(self, permissions):
        '''
        Sets the permissions of the file that will be set after extraction.

        The format for the permission field is the same as for chmod under unix 
        (numerical representation). It is 3 characters, each being between 0 and 7.
        '''

        allowedPermissionCharacters = "01234567"
        if len(permissions) != 3 \
                or permissions[0] not in allowedPermissionCharacters \
                or permissions[1] not in allowedPermissionCharacters \
                or permissions[2] not in allowedPermissionCharacters:
            raise ValueError(
                "Incorrect file permission format. Expected format is the numeric format used by chmod (for example 755). Got {0}".format(permissions))
        self.permissions = permissions

    def setItemNameForCommands(self, name):
        '''Sets the name for the injected item to be used later with generating commands.'''

        if name in nameToItems:
            raise ValueError("Item of the name {0} already exits".format(name))
        nameToItems[name] = self.ID

    def updateFlags(self, flag, value):
        '''Tries to set a flag bit to a given value.'''

        if flag == 'remove-after-use':
            if not strToBool(value):
                self.flags &= ~ 1

    def print(self):
        '''Display the most important fields in the class.'''

        print("ID = {4}, Name = {0}, Path = {1}, Permissions = {2}, Flags = {3}".format(
            self.name, self.path, self.permissions, self.flags, self.ID))

    def validate(self):
        '''Check if the required fields are set. If not raise an exception.'''

        if self.name == '' or self.name == '\n':
            raise ValueError("Name not set")
        if self.path == '' or self.path == '\n':
            raise ValueError("Path not set")

    def initializeHeader(self):
        resetHasher()
        self.validate()

    def updateHeader(self, item):
        '''Given a chunk of file, update a hash and a length of an item.'''

        global hasher
        hasher.update(item)
        self.hash = hasher.hexdigest()
        self.length += len(item)

    def generateHeader(self):
        '''Run after setting up everything. Generates bytes data for a item header. Returns a dict.'''

        if len(self.name) > 64:
            raise ValueError(
                "Length of the given file name is greater than 64")
        else:
            while len(self.name) != 64:
                self.name += '\0'
        return {'ID': self.ID.to_bytes(2, byteorder='little'),
                'length': self.length.to_bytes(4, byteorder='little'),
                'flags': self.flags.to_bytes(2, byteorder='little'),
                'fileName': self.name.encode('ascii'),
                'itemHash': self.hash.encode('ascii'),
                'permissions': self.permissions.encode('ascii')}

    def parseConfig(self, key, value):
        '''Parse a single line of a configuration. Details in a documentation.'''

        if key == 'path':
            self.setPath(value)
        elif key == 'permissions':
            self.setPermissions(value)
        elif key == 'name':
            self.setItemNameForCommands(value)
        elif key in ['remove-after-use']:
            self.updateFlags(key, value)
        else:
            raise ValueError(
                "Wrong configuration options for an [Item] {0}:{1}".format(key, value))


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
    client.write(header['numberOfItems'].to_bytes(2, 'little'))
    client.write(header['fileHash'].encode('ascii'))


def createMainHeader():
    '''calculate a hash of a final injected part, generate main header fields.'''

    global hasher, filesToInject
    resetHasher()

    numberOfItems = len(filesToInject)

    injectedFiles = open('.~injector-finalInjectedFiles.temp', 'rb')

    # size of a main header based on the specs. Required for a correct size calculations.
    totalSize = 38

    buf = injectedFiles.read(BLOCKSIZE)
    while len(buf) > 0:
        totalSize += len(buf)
        hasher.update(buf)
        buf = injectedFiles.read(BLOCKSIZE)
    injectedFiles.close()

    fileHash = hasher.hexdigest()

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
    target.write(header['length'])
    target.write(header['flags'])
    target.write(header['fileName'])
    target.write(header['itemHash'])
    target.write(header['permissions'])


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

    elif line == '[Item]':
        areItemsInjected = True
        print("Configuring new item. ID: {0}".format(itemID))
        filesToInject.append(fileToInject(itemID))
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

        currentlyBeingParsed.parseConfig(key, value)


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
        flags |= 1
    if areItemsEncrypted:
        flags |= 2

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
