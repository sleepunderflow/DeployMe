from flask import json

''' Return an error message as json '''
def generateError(message, errorNumber):
  return json.jsonify(
    result="error",
    error=errorNumber,
    message=message), errorNumber