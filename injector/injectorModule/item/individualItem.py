import ntpath
import hashlib
from .. import hasherHelper

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
        self.additionalData = ""
        self.setDefaultFlags()
        self.hash = ""
        self.length = 0

    def setDefaultFlags(self):
        '''Sets default flags for the file. For details check the documentation.'''

        self.flags = 0
        self.flags |= 1  # remove-after-use = true

    def setPath(self, path):
        '''Sets a path of a file to inject and a filename that will be included in the resulting binary.'''

        self.path = path
        self.name = path_leaf(path)

    # def setPermissions(self, permissions):
    #     '''
    #     Sets the permissions of the file that will be set after extraction.

    #     The format for the permission field is the same as for chmod under unix 
    #     (numerical representation). It is 3 characters, each being between 0 and 7.
    #     '''

    #     allowedPermissionCharacters = "01234567"
    #     if len(permissions) != 3 \
    #             or permissions[0] not in allowedPermissionCharacters \
    #             or permissions[1] not in allowedPermissionCharacters \
    #             or permissions[2] not in allowedPermissionCharacters:
    #         raise ValueError(
    #             "Incorrect file permission format. Expected format is the numeric format used by chmod (for example 755). Got {0}".format(permissions))
    #     self.permissions = permissions

    def setItemNameForCommands(self, name, nameToItems):
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

        print("ID = {3}, Name = {0}, Path = {1}, Flags = {2}".format(
            self.name, self.path, self.flags, self.ID))

    def validate(self):
        '''Check if the required fields are set. If not raise an exception.'''

        if self.name == '' or self.name == '\n':
            raise ValueError("Name not set")
        if self.path == '' or self.path == '\n':
            raise ValueError("Path not set")

    def initializeHeader(self):
        self.hasher = hasherHelper.newHasher()
        self.validate()

    def updateHeader(self, item):
        '''Given a chunk of file, update a hash and a length of an item.'''
        hasherHelper.update(self.hasher, item)
        self.hash = hasherHelper.hexdigest(self.hasher)
        self.length += len(item)

    def generateHeader(self):
        '''Run after setting up everything. Generates bytes data for a item header. Returns a dict.'''

        if len(self.name) > 64:
            raise ValueError(
                "Length of the given file name is greater than 64")
        else:
            while len(self.name) != 64:
                self.name += '\0'
        return {'ID': self.ID.to_bytes(4, byteorder='little'),
                'headerLength': (144+len(self.additionalData)).to_bytes(4, byteorder='little'),
                'payloadLength': self.length.to_bytes(4, byteorder='little'),
                'flags': self.flags.to_bytes(4, byteorder='little'),
                'fileName': self.name.encode('ascii'),
                'itemHash': self.hash.encode('ascii'),
                'additionalData': self.additionalData.encode('ascii')}

    def parseConfig(self, key, value, nameToItems):
        '''Parse a single line of a configuration. Details in a documentation.'''

        if key == 'path':
            self.setPath(value)
        elif key == 'name':
            self.setItemNameForCommands(value, nameToItems)
        elif key in ['remove-after-use']:
            self.updateFlags(key, value)
        else:
            raise ValueError(
                "Wrong configuration options for an [Item] {0}:{1}".format(key, value))
