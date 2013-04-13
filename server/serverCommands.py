#!/usr/bin/python

##--Function order: getKeyString , getFileSize , checkCreds , hashFile , outputMsg , makeZip

import hashlib , os , shutil , zipfile

##--Returns a formatted string of dictionary keys--##
def getKeyString(dic , strsep):
	ret = ''
	for key in dic:
		ret += strsep + key
	return ret

##--Returns a formatted string of numbered list elements (for versioning)--##
def getNumListString(lst):
	ret = '\nVer dd:mm:yyyy-hh:mm:ss\n'
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
	try:
		if dic[userName][1] == sessionID: return 'Y'
		else:
			outputMsg(foutput , '\tsessionID failed')
			return 'Error: SessionID does not match. You may have logged into another device more recently. For security reasons, please logout and login again.'
	except:
		outputMsg(foutput , '\tusername failed')
		return 'Error: Username does not exist'

##--Returns checksum for given file using given hash--##
##Ex:  hashfile(open(fileName, 'rb'), hashlib.sha256())   must be in r mode
def hashFile(fileObj , hasher , blocksize=65536):
    buf = fileObj.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = fileObj.read(blocksize)
    return hasher.digest()

##--Writes a string to a file if one is open or the console if one is not--##
def outputMsg(fileObj , msg):
	try:
		fileObj.write(msg+'\n')
	except:
		print msg

##--Creates zip archive of folder contents--##
##Ex:  makeZip(userName , 'bin/'+userName)
def makeZip(name , dirloc='' , allFiles = False):
	if dirloc != '':
		dirloc += '/'
	cwd = os.getcwd()
	userdir = cwd+'/'+dirloc
	##--Make archive of files only (no folders or hidden files)--##
	if not allFiles:
		zippy = zipfile.ZipFile(cwd+'/'+name+'.zip' , 'w')
		for fileName in os.listdir(userdir):
			if fileName != name+'.zip' and fileName[:1] != '.' and fileName[len(fileName)-1:] != '~':
				zippy.write(dirloc+fileName)
		zippy.close()
	##--Make archive of All folder contents--##
	else:
		shutil.make_archive(name , 'zip' , userdir)
