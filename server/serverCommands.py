#!/usr/bin/python

##--Returns True if string is a valid key in given dictionary--##
def dictFindB(string , dic):
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
	if dictFindB(userName , dic):
		if dic[userName][1] == sessionID:
			return 'Y'
		else:
			print '\tseesionID failed'
			return 'Error: SessionID does not match. You may have logged into another device more recently. For security reasons, please logout and login again.'
	else:
		print '\tusername failed'
		return 'Error: Username does not exist'
