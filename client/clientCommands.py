##--Function order:
##--Main functions: sendData , sendFile , recvFile , startUp
##--Minor functions: saltHash , getFileSize , getKeyString , hashFile , saveStorage , getUnPw

from socket import *
import hashlib , getpass , os , pickle , sys

##--Server connection settings--##
serverName = 'localhost'  	#  Change to IP address server computer
serverPort = 60145			#  Should match that int set on server
socketRecvBuffer = 1024		#  2**x

##--Send a single string of data and recieve a single string of data--##
def sendData(DATA):
	try:
		totalsent = 0
		clientSocket = socket(AF_INET , SOCK_STREAM)
		clientSocket.connect((serverName , serverPort))
		while totalsent < len(DATA):
			sent = clientSocket.send(DATA[totalsent:])
			totalsent = totalsent + sent
		ret = clientSocket.recv(socketRecvBuffer)
		clientSocket.close()
		return ret
	except Exception , e:
		return 'Error: ' + str(e)[str(e).find(']')+1:]

##--Sends a file (regardless of contents or size) to the server--##
def sendFile(credentials , fileName , userSets):
	try:
		if fileName.find('&&&') != -1: print "Because of how request data is sent to the server, the file name cannot contain '&&&'"
		else:
			fout = open(userSets['senddir'] + fileName , 'rb')
			fileLen = getFileSize(fout)
			if fileLen == 0: return 'Server will not accept empty files'
			if fileName.find('/') != -1: fileName = fileName[fileName.rfind('/')+1:]
			checksum = hashFile(fout , hashlib.sha512())
			DATA = credentials + '&&&' + fileName + '&&&' + checksum + '&&&' + str(fileLen)
			clientSocket = socket(AF_INET , SOCK_STREAM)
			clientSocket.connect((serverName , serverPort))
			sent = clientSocket.send(DATA)  #Server verifies checksum has changed and preps file for contents
			rec = clientSocket.recv(socketRecvBuffer)
			if rec == 'success':  #Send file contents
				outputData = fout.readlines()
				for line in outputData: sent = clientSocket.send(line)
				rec = clientSocket.recv(socketRecvBuffer)
			clientSocket.close()
			return rec
	except Exception , e:
		return 'Error: ' + str(e)[str(e).find(']')+1:]

def recvFile(credentials , fileName , userSets):
	try:
		clientSocket = socket(AF_INET , SOCK_STREAM)
		clientSocket.connect((serverName , serverPort))
		clientSocket.send(credentials+'&&&'+fileName)
		fileLen = clientSocket.recv(socketRecvBuffer)
		if not fileLen.isdigit(): return fileLen
		if fileName.find('/'): fileName = fileName[fileName.find('/')+1:]
		fin = file(userSets['destdir'] + fileName , 'wb')
		finLen = 0 #current length of recieving file
		clientSocket.send('send')
		##--Recieve file of variable length--##
		while finLen < int(fileLen):
			line = clientSocket.recv(socketRecvBuffer)
			fin.write(line)
			finLen = getFileSize(fin)
		fin.close()
		clientSocket.send('success')
		clientSocket.close()
		return 'File recieved'
	except Exception , e:
		return 'Error: ' + str(e)[str(e).find(']')+1:]

def viewFileAndSend(credentials , command , userSets):
	ret = sendData('viewfiles&&&'+credentials)
	#Server checks if sessionID matches and sends list of files (if any)
	if ret != 'You have not uploaded any files':
		print ret
		ret = ret.split('\n') #Create searchable list from file names
		fileName = raw_input('\nFile: ')
		if fileName == '#quit': return ''
		if fileName in ret: ret = sendData(command+'&&&'+credentials+'&&&'+fileName)
		else: ret = 'Error: Not an available file'
		if ret[:4] == '\nVer': return ret , fileName
	return ret

##--Users signup or login and recieve valid sessionID if successful--##
def startUp(command):
	try:
		userName , password = getUnPw()
		password = saltHash(password , userName) #Encrypt password
		resp = sendData(command + '&&&' + userName + '&&&' + password).split('&&&')
		if resp[0] == 'success': return userName , True , resp[1]
		else:
			print resp[0] + '\n'
			return '' , False , ''
	except Exception , e:
		print 'Error: ' + str(e)[str(e).find(']')+1:]
		return '' , False , ''

##--Salts and hashes password using userName--##
def saltHash(password , userName):
	salted_password = "All'improvviso" + userName[:len(userName)-4] + password + userName[len(userName)-4:] + 'Amore'
	hashed_password = hashlib.sha512(salted_password).hexdigest()
	return hashed_password

##--Returns the length of a file--##
def getFileSize(fileObj):
	curpos = fileObj.tell()
	fileObj.seek(0,2)
	ret = fileObj.tell()
	fileObj.seek(curpos)
	return ret

##--Returns a formatted string of dictionary keys--##
##--If valsep is included, also formats the key's value--##
def getKeyString(dic , linsep , valsep=''):
	ret = ''
	for key in dic:
		ret += linsep + key
		if valsep: ret += valsep + str(dic[key])
	return ret

##--Returns checksum for given file using given hash--##
##Ex:  hashfile(open(fileName, 'rb'), hashlib.sha256())   #must be in r mode
def hashFile(afile, hasher, blocksize=65536):
	buf = afile.read(blocksize)
	while len(buf) > 0:
		hasher.update(buf)
		buf = afile.read(blocksize)
	afile.seek(0)
	return hasher.digest()

##--Save user settings--##
def saveStorage(*data):
	storageFile = open('ClientStorage.pkl', 'wb')
	for i in data: pickle.dump(i , storageFile)
	storageFile.close()

##--Returns valid userName and password--##
def getUnPw():
	userName,password = '',''
	print 'Both username and password must be at least 8 characters long'
	##--Username and password must be 8+ chars and not contain &&& --##
	while len(userName) < 8 or userName.find('&') != -1:
		userName = raw_input('userName : ')
		if userName == '#quit': sys.exit()
		elif len(userName) < 8: print 'Username is not long enough'
		elif userName.find('&') != -1: print 'Due to the way this program talks with the server, your username cannot contain "&"'
	while len(password) < 8 or password.find('&') != -1:
		password = getpass.getpass('Password : ')
		if password == '#quit': sys.exit()
		elif len(password) < 8: print 'Password is not long enough'
		elif password.find('&') != -1: print 'Due to the way this program talks with the server, your password cannot contain "&"'
	return userName , password
