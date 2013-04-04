#!/usr/bin/python

import hashlib

##--Returns True if string is a valid key in given dictionary--##
def findInDict(string , dic):
	try:
		for key in dic:
			if key == string: return True
		return False
	except:
		return False

##--Returns a formatted string of dictionary keys--##
def getKeyString(dic):
	ret = ''
	for key in dic:
		ret += '\t\n' + key
	return ret

##--Returns the length of a file--##
def getFileSize(fileObj):
	curpos = fileObj.tell()
	fileObj.seek(0,2)
	ret = fileObj.tell()
	fileObj.seek(curpos)
	return ret

##--Checks if userName and sessionID are both valid--##
def checkCreds(userName , sessionID , dic):
	if findInDict(userName , dic):
		if dic[userName][1] == sessionID:
			return 'Y'
		else:
			print '\tseesionID failed'
			return 'Error: SessionID does not match. You may have logged into another device more recently. For security reasons, please logout and login again.'
	else:
		print '\tusername failed'
		return 'Error: Username does not exist'

##--Returns checksum for given file using given hash--##
##Ex:  hashfile(open(fileName, 'rb'), hashlib.sha256())
def hashfile(afile, hasher, blocksize=65536):
    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    return hasher.digest()
