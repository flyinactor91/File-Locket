##--Function order:
##--Main functions: sendData , sendFile , recvFile , login , signUp , settings
##--Minor functions: saltHash , getFileSize , getKeyString , hashFile , saveStorage , getUnPw

from socket import *
import hashlib , getpass , os , pickle

##--Server connection settings--##
serverName = 'localhost'  	#  Change to IP address server computer
serverPort = 60145			#  Should match that int set on server
socketRecvBuffer = 1024		#  2**x

socketSets = [serverName , serverPort]

##--Send a single string of data and recieve a single string of data--##
def sendData(DATA):
	try:
		totalsent = 0
		clientSocket = socket(AF_INET , SOCK_STREAM)
		clientSocket.connect((socketSets[0] , socketSets[1]))
		while totalsent < len(DATA):
			sent = clientSocket.send(DATA[totalsent:])
			totalsent = totalsent + sent
		ret = clientSocket.recv(socketRecvBuffer)
		clientSocket.close()
		return ret
	except Exception , e:
		print 'Error: ' + str(e)

##--Sends a file (regardless of contents or size) to the server--##
def sendFile(credentials , fileName , userSets):
	try:
		if fileName.find('&&&') != -1: print "Because of how request data is sent to the server, the file name cannot contain '&&&'"
		else:
			fout = open(userSets['senddir'] + fileName , 'rb')
			fileLen = str(getFileSize(fout))
			if fileLen == 0: print 'Server will not accept empty files'
			else:
				if fileName.find('/') != -1: fileName = fileName[fileName.rfind('/')+1:]
				checksum = hashFile(fout , hashlib.sha512())
				DATA = credentials + '&&&' + fileName + '&&&' + checksum + '&&&' + fileLen
				clientSocket = socket(AF_INET , SOCK_STREAM)
				clientSocket.connect((socketSets[0] , socketSets[1]))
				sent = clientSocket.send(DATA)
				#Server checks if sessionID matches and preps file for contents
				rec = clientSocket.recv(socketRecvBuffer)
				if rec == 'Connection successful':
					##--Send file contents--##
					outputData = fout.readlines()
					for line in outputData:
						sent = clientSocket.send(line)
					rec = clientSocket.recv(socketRecvBuffer)
				print rec
				clientSocket.close()
	except Exception , e:
		print 'Error: ' + str(e)

def recvFile(credentials , fileName , userSets):
	try:
		clientSocket = socket(AF_INET , SOCK_STREAM)
		clientSocket.connect((socketSets[0] , socketSets[1]))
		clientSocket.send(credentials+'&&&'+fileName)
		fileLen = int(clientSocket.recv(socketRecvBuffer))
		if fileName.find('/'): fileName = fileName[fileName.find('/')+1:]
		fin = file(userSets['destdir'] + fileName , 'wb')
		finLen = 0 #current length of recieving file
		clientSocket.send('send')
		##--Recieve file of variable length--##
		while finLen < fileLen:
			line = clientSocket.recv(socketRecvBuffer)
			fin.write(line)
			finLen = getFileSize(fin)
		fin.close()
		clientSocket.send('success')
		print 'File recieved'
		clientSocket.close()
	except Exception , e:
		print 'Error: ' + str(e)

def filesView(credentials , command , userSets):
	ret = sendData('viewfiles&&&'+credentials)
	#Server checks if sessionID matches and sends list of files (if any)
	if ret != 'You have not uploaded any files':
		print ret
		ret = ret.split('\n') #Create searchable list from file names
		fileName = raw_input('\nFile: ')
		if fileName == '#quit': return ''
		else:
			if fileName in ret: ret = sendData(command+'&&&'+credentials+'&&&'+fileName)
			else: ret = 'Error: Not an available file'
		if ret[:4] == '\nVer': return ret , fileName
	return ret

##--Existing users login and recieve valid sessionID--##
def login():
	try:
		userName , password = getUnPw()
		password = saltHash(password , userName) #Encrypt password
		resp = sendData('login' + '&&&' + userName + '&&&' + password)
		if type(resp) == type(None): return '' , False , '' #Checks if sendData raised an exception
		elif resp[:16] == 'Login successful':
			sucBool = True
		else:
			print '\n' + resp + '\n'
			userName = ''
			sucBool = False
		return userName , sucBool , resp[resp.find(':')+1:]
	except Exception , e:
		print 'Error: ' + str(e)
		return '' , False , ''

##--New users create account on server and recieve valid sessionID--##
def signUp():
	try:
		userName , password = getUnPw()
		password = saltHash(password , userName) #Encrypt password
		resp = sendData('signup' + '&&&' + userName + '&&&' + password)
		if type(resp) == type(None): return '' , False , '' #Checks if sendData raised an exception
		elif resp[:17] == 'Signup successful':
			sucBool = True
		else:
			print '\n' + resp + '\n'
			userName = ''
			sucBool = False
		return userName , sucBool , resp[resp.find(':')+1:]
	except Exception , e:
		print 'Error: ' + str(e)
		return '' , False , ''

##--Change user setting dictionary--##
def settings(command , userSets):
	if len(command) == 1: print '\nset [var] (value)\nClear var value with #clear\nVariables that can be set:' + getKeyString(userSets , '\n')
	elif command[1] in userSets:
		if len(command) == 2:
			setVal = userSets[command[1]]
			if setVal == '':
				setVal = 'No value set'
			print command[1] + ':  ' + setVal
		else:
			if command[2] == '#clear':
				command[2] = ''
			elif command[1] == 'senddir' or command[1] == 'destdir':
				if command[2][:1] == '~': command[2] = os.path.expanduser(command[2])
				elif command[2][:3] == 'cwd': command[2] = command[2].replace('cwd' , os.getcwd() , 1)
				if command[2][:len(command[2])] != '/' and command[2] != '': command[2] += '/'
				if not os.path.isdir(command[2]):
					print command[2] + ' is not a directory'
					return userSets
			userSets[command[1]] = command[2]
	else:
		print command[1] + ' is not an available setting'
	return userSets

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
def getKeyString(dic , strsep):
	ret = ''
	for key in dic:
		ret += strsep + key
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
def saveStorage(userName , sessionID , userSets):
	storageFile = open('ClientStorage.pkl', 'wb')
	pickle.dump(userName , storageFile)
	pickle.dump(sessionID , storageFile)
	pickle.dump(userSets , storageFile)
	storageFile.close()

##--Returns valid userName and password--##
def getUnPw():
	userName,password = '',''
	print 'Both username and password must be at least 8 characters long'
	##--Username and password must be 8+ chars and not contain &&& --##
	while len(userName) < 8 or userName.find('&') != -1:
		userName = raw_input('userName : ')
		if len(userName) < 8: print 'Username is not long enough'
		elif userName.find('&') != -1: print 'Due to the way this program talks with the server, your username cannot contain "&"'
	while len(password) < 8 or password.find('&') != -1:
		password = getpass.getpass('Password : ')
		if len(password) < 8: print 'Password is not long enough'
		elif password.find('&') != -1: print 'Due to the way this program talks with the server, your password cannot contain "&"'
	return userName , password
