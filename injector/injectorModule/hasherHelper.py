import hashlib

def hexdigest(hasher):
  return hasher.hexdigest()

def newHasher():
  return hashlib.sha256()

def update(hasher, data):
  hasher.update(data)