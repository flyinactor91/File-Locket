##--Function order: getKeyString , getFileSize , getFolderSize , checkCreds , hashFile , outputMsg , makeZip

import hashlib , os , shutil , zipfile , time

##--Returns a formatted string of dictionary keys--##
def getKeyString(dic , linsep , valsep=''):
	ret = ''
	for key in dic:
		ret += linsep + key
		if valsep: ret += valsep + str(dic[key])
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

##--Returns approx number of bytes in a directory including sub-directories--##
def getFolderSize(dirloc):
	size = 0
	for (path, dirs, files) in os.walk(dirloc):
		for fileName in files:
			size += os.path.getsize(os.path.join(path, fileName))
	return size

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

##--Outputs variable amout of data to error file--##
def criticalError(*errorInfo):
	fout = open('bin/criticalErrors.txt' , 'ab')
	fout.write(time.strftime('%d:%m:%Y-%X'))
	for i in errorInfo: fout.write('\n'+str(i))
	fout.write('\n\n')
	fout.close()
