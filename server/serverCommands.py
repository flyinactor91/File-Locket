#!/usr/bin/python

##--Function order: findInDict , findInList , getKeyString , getFileSize , checkCreds , hashFile , outputMsg

import hashlib

##--Returns True if string is a valid key in given dictionary--##
def findInDict(string , dic):
	try:
		for key in dic:
			if key == string: return True
		return False
	except:
		return False

##--Returns True if value is found in given list--##
def findInList(item , listObj):
	try:
		for i in listObj:
			if i == item: return True
		return False
	except:
		return False

##--Returns a formatted string of dictionary keys--##
def getKeyString(dic , strsep):
	ret = ''
	for key in dic:
		ret += strsep + key
	return ret

##--Returns a formatted string of numbered list elements (for versioning)--##
def getNumListString(lst):
	ret = ''
	for num in range(len(lst)):
		ret += '\n' + str(num+1) + '.  ' + str(lst[num])
	return ret

##--Returns the length of a file--##
def getFileSize(fileObj):
	curpos = fileObj.tell()
	fileObj.seek(0,2)
	ret = fileObj.tell()
	fileObj.seek(curpos)
	return ret

##--Checks if userName and sessionID are both valid--##
def checkCreds(userName , sessionID , dic , foutput):
	if findInDict(userName , dic):
		if dic[userName][1] == sessionID:
			return 'Y'
		else:
			outputMsg(foutput , '\tseesionID failed')
			return 'Error: SessionID does not match. You may have logged into another device more recently. For security reasons, please logout and login again.'
	else:
		outputMsg(foutput , '\tusername failed')
		return 'Error: Username does not exist'

##--Returns checksum for given file using given hash--##
##Ex:  hashfile(open(fileName, 'rb'), hashlib.sha256())   must be in r mode
def hashFile(afile , hasher , blocksize=65536):
    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    return hasher.digest()

##--Writes a string to a file if one is open or the console if one is not--##
def outputMsg(afile , msg):
	try:
		afile.write(msg+'\n')
	except:
		print msg
