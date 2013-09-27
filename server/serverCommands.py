##--Michael duPont
##--v2.0.0 [2013-09-27]
##--Function order: sendFile , getKeyString , getNumListString , getFileSize , getFolderSize , checkCreds , hashFile , outputMsg , makeZip , criticalError

import hashlib , os , shutil , zipfile , time



##--Send a given file through a given socket and return appropriate message--##
def sendFile(connectionSocket , fileLoc , socketRecvBuffer):
	##--Get file contents--##
	fout = open(fileLoc , 'rb')
	outputData = fout.readlines()
	fout.close()
	
	##--Send client file length and checksum
	fileLen = str(os.path.getsize(fileLoc))
	checksum = hashFile(fileLoc , hashlib.sha256())
	connectionSocket.send(fileLen + '&&&' + checksum)
	
	##--Recieve fileBuffer and ClientRecvBuffer
	rec = connectionSocket.recv(socketRecvBuffer)
	if rec.find('&&&') != -1:
		fileBuffer = int(rec.split('&&&')[0])
		clientRecvBuffer = int(rec.split('&&&')[1])
		curBuffer = 0
		
		##--Send file contents--##
		for line in outputData:
			while len(line) > 0:
				
				##--Send only what doesn't exceed what the client can recieve at one time--##
				if len(line) > clientRecvBuffer:
					curBuffer += connectionSocket.send(line[:clientRecvBuffer])
					line = line[clientRecvBuffer:]
				else:
					curBuffer += connectionSocket.send(line)
					line = ''
				
				##--Waits for client to send 'cont' before continuing--##
				if curBuffer >= fileBuffer:
					rec = connectionSocket.recv(socketRecvBuffer)
					if rec != 'cont': return 'Error: recieve mid stream'
					curBuffer = 0
		rec = connectionSocket.recv(socketRecvBuffer)
		if rec == 'success': return 'success'
		else: return 'Error: recieve end stream'
	else:
		return 'Error: recieve pre stream'
	

##--Returns a formatted string of dictionary keys and --##
def getKeyString(dic , linsep , valsep=''):
	ret = ''
	for key in dic:
		ret += linsep + key
		if valsep: ret += valsep + str(dic[key])
	return ret

##--Returns a formatted string of numbered list elements--##
def getNumListString(lst , versions = False):
	if versions: ret = '\nVer yyyy-mm-dd hh:mm:ssZ\n'
	else: ret = ''
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
##Ex:  hashFile(fileName , hashlib.sha256())
##Note: You CANNOT CANNOT CANNOT give hasher a default value. Hasher object would be carried over each function call spitting out inconsistent values
def hashFile(fileLoc , hasher , blocksize=65536):
	fileObj = open(fileLoc , 'rb')
	buf = fileObj.read(blocksize)
	while len(buf) > 0:
		hasher.update(buf)
		buf = fileObj.read(blocksize)
	fileObj.close()
	return hasher.hexdigest()

##--Writes a string to a file if one is open or the console if one is not--##
def outputMsg(fileObj , msg):
	try: fileObj.write(msg+'\n')
	except: print msg

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
	fout.write(time.strftime('%Y-%m-%d---%X'))
	for i in errorInfo: fout.write('\n'+str(i))
	fout.write('\n\n')
	fout.close()
