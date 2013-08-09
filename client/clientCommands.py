##--Michael duPont
##--v1.3.0 [2013-08-07]
##--Function order:
##--Main functions: sendData , sendFile , recvFile , viewFileAndSend , startUp
##--Minor functions: saltHash , getFileSize , getKeyString , hashFile , saveStorage , getUnPw , compareVersions , getInput , ProgressBar

from socket import *
import hashlib , getpass , os , pickle , sys

##--Server connection settings--##
serverName = 'localhost'  	#  Change to IP address of server computer
serverPort = 60145			#  Should match that int set on server
defaultTimeout = 5			#  Timeout used for normal connection conditions
socketRecvBuffer = 1024		#  2**x
fileBuffer = 500000			#  Amount of bits for server to recv and process at a time. View dev notes

##--Send a single string of data and recieve a single string of data--##
def sendData(DATA):
	try:
		totalsent = 0
		clientSocket = socket(AF_INET , SOCK_STREAM)
		clientSocket.connect((serverName , serverPort))
		clientSocket.settimeout(defaultTimeout)
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
		if fileName.find('&&&') != -1: return "Because of how request data is sent to the server, the file name cannot contain '&&&'"
		else:
			fileLoc = userSets['senddir'] + fileName
			fileLen = int(os.path.getsize(fileLoc))
			if fileLen == 0: return 'Server will not accept empty files'
			if fileName.find('/') != -1: fileName = fileName[fileName.rfind('/')+1:]
			fout = open(fileLoc , 'rb')
			outputData = fout.readlines()
			fout.close()
			checksum = hashFile(fileLoc , hashlib.sha256())
			DATA = credentials + '&&&' + fileName + '&&&' + checksum + '&&&' + str(fileLen)
			clientSocket = socket(AF_INET , SOCK_STREAM)
			clientSocket.connect((serverName , serverPort))
			clientSocket.settimeout(defaultTimeout)
			sent = clientSocket.send(DATA)  #Server verifies checksum has changed and preps file for contents
			rec = clientSocket.recv(socketRecvBuffer)
			if rec.find('&&&') != -1:  #Send file contents
				startProgress('Upload')
				fileBuffer = int(rec.split('&&&')[0])
				serverRecvBuffer = int(rec.split('&&&')[1])
				curBuffer = 0
				for line in outputData:
					while len(line) > 0:
						if len(line) > serverRecvBuffer:
							curBuffer += clientSocket.send(line[:serverRecvBuffer])
							line = line[serverRecvBuffer:]
						else:
							curBuffer += clientSocket.send(line)
							line = ''
						if curBuffer >= fileBuffer:
							recvLen = clientSocket.recv(socketRecvBuffer)
							if not recvLen.isdigit():
								clientSocket.close()
								endProgress()
								return recvLen
							progress(int(float(recvLen) / fileLen * 100))
							curBuffer = 0
				endProgress()
				rec = clientSocket.recv(socketRecvBuffer)
			clientSocket.close()
			return rec
	except Exception , e:
		return 'Error: ' + str(e)[str(e).find(']')+1:]

def recvFile(credentials , fileName , userSets):
	try:
		clientSocket = socket(AF_INET , SOCK_STREAM)
		clientSocket.connect((serverName , serverPort))
		clientSocket.settimeout(defaultTimeout)
		clientSocket.send(credentials+'&&&'+fileName)
		rec = clientSocket.recv(socketRecvBuffer).split('&&&')
		fileLen = rec[0]
		if not fileLen.isdigit(): return fileLen
		fileLen = int(fileLen)
		recvChecksum = rec[1]
		if fileName.find('/'): fileName = fileName[fileName.find('/')+1:]
		fileLoc = userSets['destdir'] + fileName
		fin = file(fileLoc , 'wb')
		finLen = 0 #current length of recieving file
		curBuffer = 0
		clientSocket.send(str(fileBuffer)+'&&&'+str(socketRecvBuffer))
		startProgress('Download')
		##--Recieve file of variable length--##
		while finLen < fileLen:
			line = clientSocket.recv(socketRecvBuffer)
			fin.write(line)
			finLen = getFileSize(fin)
			curBuffer += len(line)
			if curBuffer >= fileBuffer:
				clientSocket.send('cont')
				progress(int(float(finLen) / fileLen * 100))
				curBuffer = 0
		fin.close()
		endProgress()
		checksum = hashFile(fileLoc , hashlib.sha256())
		if checksum != recvChecksum:
			clientSocket.send('checksumError')
			return 'File Recieve Error: Checksum did not match. Downloaded file might be corrupted. Try getting again'
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
		if command == 'login': userName , password = getUnPw(True)
		else: userName , password = getUnPw()
		password = saltHash(password , userName) #Encrypt password
		resp = sendData(command + '&&&' + userName + '&&&' + password).split('&&&')
		if resp[0] == 'success': return userName , resp[1]
		else:
			print resp[0] + '\n'
			return '' , ''
	except Exception , e:
		print 'Error: ' + str(e)[str(e).find(']')+1:]
		return '' , ''

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
##Ex:  hashFile(fileName , hashlib.sha256())
##Note: You CANNOT give hasher a default value. Hasher object would be carried over each function call spitting out inconsistent values
def hashFile(fileLoc , hasher , blocksize=65536):
	fileObj = open(fileLoc , 'rb')
	buf = fileObj.read(blocksize)
	while len(buf) > 0:
		hasher.update(buf)
		buf = fileObj.read(blocksize)
	fileObj.close()
	return hasher.hexdigest()

##--Save user settings--##
def saveStorage(*data):
	storageFile = open('ClientStorage.pkl', 'wb')
	for i in data: pickle.dump(i , storageFile)
	storageFile.close()

##--Returns valid userName and password--##
def getUnPw(login = False):
	userName,password = '',''
	print 'Both username and password must be at least 8 characters long'
	##--Username and password must be 8+ chars and not contain &&& --##
	while len(userName) < 8 or userName.find('&') != -1:
		userName = getInput('userName : ')
		if len(userName) < 8: print 'Username is not long enough'
		elif userName.find('&') != -1: print 'Due to the way this program talks with the server, your username cannot contain "&"'
	passMatch = False
	while passMatch == False:
		password = ''
		while len(password) < 8 or password.find('&') != -1:
			password = getpass.getpass('Password : ')
			if password == '#quit': sys.exit()
			elif len(password) < 8: print 'Password is not long enough'
			elif password.find('&') != -1: print 'Due to the way this program talks with the server, your password cannot contain "&"'
		if login: return userName , password
		verify = getpass.getpass('Verify Password : ')
		if password == '#quit': sys.exit()
		elif verify != password: print "Passwords do not match"
		else: passMatch = True
	return userName , password

##--Compares the version values (expressed in a list)--##
##--ex. v1.2.0 compared to v1.2.1 is compareVersions([1,2,0],[1,2,1]) --> -1 --##
def compareVersions(list1 , list2):
	if list1[0] == list2[0]:
		if list1[1] == list2[1]:
			if list1[2] == list2[2]: return 0
			elif list1[2] > list2[2]: return 1
			elif list1[2] < list2[2]: return -1
		elif list1[1] > list2[1]: return 1
		elif list1[1] < list2[1]: return -1
	elif list1[0] > list2[0]: return 1
	elif list1[0] < list2[0]: return -1

##--Checks for #quit to quit program at any point
def getInput(prompt = ''):
	ret = raw_input(prompt)
	if ret == '#quit': sys.exit()
	else: return ret

##--Create, update, and close a single-line progress bar--##
##--Credit to '6502' at 'http://stackoverflow.com/questions/6169217/replace-console-output-in-python'--##
def startProgress(title):
    sys.stdout.write(title + ': [' + ' '*40 + ']' + chr(8)*41)
    sys.stdout.flush()
    globals()['progress_x'] = 0
def progress(x):  #x = percent complete, range(0,100)
    x = x*40//100
    sys.stdout.write('='*(x - globals()['progress_x']))
    sys.stdout.flush()
    globals()['progress_x'] = x
def endProgress():
    sys.stdout.write('='*(40 - globals()['progress_x']))
    sys.stdout.write(']\n')
    sys.stdout.flush()
