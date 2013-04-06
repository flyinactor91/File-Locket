#!/usr/bin/python

##--Function order:
##--Main functions: sendData , sendFile , getFile , showFiles , delFile , startUp , login , signUp , settings , admin
##--Minor functions: saltHash , getFileSize , findInList , findInDict , getKeyString , hashFile

from socket import *
import hashlib , getpass , os

##--Send a single string of data and recieve a single string of data--##
def sendData(DATA , serverName , serverPort):
	try:
		totalsent = 0
		clientSocket = socket(AF_INET , SOCK_STREAM)
		clientSocket.connect((serverName , serverPort))
		while totalsent < len(DATA):
			sent = clientSocket.send(DATA[totalsent:])
			totalsent = totalsent + sent
		ret = clientSocket.recv(1024)
		clientSocket.close()
		return ret
	except Exception , e:
		print 'Error: ' + str(e)

##--Sends a file (regardless of contents or size) to the server--##
def sendFile(credentials , userSets , serverName , serverPort):
	try:
		fileName = '&&&'
		while fileName.find('&&&') != -1:
			fileName = raw_input('What file would you like to send?: ')
			if fileName.find('&&&') != -1: print "Because of how request data is sent to the server, the file name cannot contain '&&&'"
		fout = open(userSets['senddir'] + fileName , 'rb')
		clientSocket = socket(AF_INET , SOCK_STREAM)
		clientSocket.connect((serverName , serverPort))
		##--Get file name if input points to another dir
		if fileName.find('/') != -1:
			fileName = fileName[fileName.rfind('/')+1:]
		fileLen = str(getFileSize(fout))
		checksum = hashFile(fout , hashlib.sha512())
		DATA = credentials + '&&&' + fileName + '&&&' + checksum + '&&&' + fileLen
		sent = clientSocket.send(DATA)
		#Server checks if sessionID matches and preps file for contents
		rec = clientSocket.recv(1024)
		if rec == 'Connection successful':
			##--Send file contents--##
			outputData = fout.readlines()
			for line in outputData:
				sent = clientSocket.send(line)
				if sent == 0:
					raise RuntimeError('socket connection broken')
			rec = clientSocket.recv(1024)
		print rec
		clientSocket.close()
	except Exception , e:
		print 'Error: ' + str(e)

##--Recieve a file from the server and save to curdir
def getFile(credentials , userSets , serverName , serverPort):
	try:
		clientSocket = socket(AF_INET , SOCK_STREAM)
		clientSocket.connect((serverName , serverPort))
		clientSocket.send(credentials)
		#Server checks if sessionID matches and sends list of files (if any)
		ret = clientSocket.recv(1024)
		print ret
		if ret != 'You have not uploaded any files':
			print ''
			ret = ret.split('\t\n') #Create searchable list from file names
			fileName = raw_input('File: ')
			if findInList(fileName , ret):
				clientSocket.send(fileName)
				fileLen = int(clientSocket.recv(1024))
				fin = file(userSets['destdir'] + fileName , 'wb')
				finLen = 0 #current length of recieving file
				clientSocket.send('send')
				##--Recieve file of variable length--##
				while finLen < fileLen:
					line = clientSocket.recv(1024)
					fin.write(line)
					finLen = getFileSize(fin)
				fin.close()
				clientSocket.send('success')
				print 'File recieved'
			else:
				print 'Error: Not an available file'
		clientSocket.close()
	except Exception , e:
		print 'Error: ' + str(e)

##--Displays a list of files stored on the server--##
def showFiles(credentials , serverName , serverPort):
	try:
		clientSocket = socket(AF_INET , SOCK_STREAM)
		clientSocket.connect((serverName , serverPort))
		clientSocket.send(credentials)
		#Server checks if sessionID matches and sends list of files (if any)
		ret = clientSocket.recv(1024)
		print ret
		clientSocket.close()
	except Exception , e:
		print 'Error: ' + str(e)

##--Delete a file saved on the server--##
def delFile(credentials , serverName , serverPort):
	try:
		clientSocket = socket(AF_INET , SOCK_STREAM)
		clientSocket.connect((serverName , serverPort))
		clientSocket.send(credentials)
		#Server checks if sessionID matches and sends list of files (if any)
		ret = clientSocket.recv(1024)
		print ret
		if ret != 'You have not uploaded any files':
			print ''
			ret = ret.split('\t\n') #Create searchable list from file names
			fileName = raw_input('File: ')
			if findInList(fileName , ret):
				clientSocket.send(fileName)
				print clientSocket.recv(1024)
			else:
				print 'Error: Not an available file'
		clientSocket.close()
	except Exception , e:
		print 'Error: ' + str(e)

##--Called if no active user. Invokes login or startup--##
def startUp(serverName , serverPort):
	lin = ''
	while lin != 'L' and lin != 'S':
		lin = raw_input('\nLogin or Sign up? (L/S) : ').upper()
	if lin == 'L': ret = login(serverName , serverPort)
	elif lin == 'S': ret = signUp(serverName , serverPort)
	return ret

##--Existing users login and recieve valid sessionID--##
def login(serverName , serverPort):
	try:
		userName = ''
		password = ''
		##--Username and password must be 8+ chars and not contain &&& --##
		while len(userName) < 8 or userName.find('&&&') != -1:
			userName = raw_input('Username : ')
			if len(userName) < 8: print 'Username is not long enough'
			if userName.find('&&&') != -1: print 'Not an acceptable username'
		while len(password) < 8 or password.find('&&&') != -1:
			password = getpass.getpass('Password : ')
			if len(password) < 8: print 'Password is not long enough'
			if password.find('&&&') != -1: print 'Not an acceptable password'
			
		password = saltHash(password , userName) #Encrypt password
		resp = sendData('login' + '&&&' + userName + '&&&' + password , serverName , serverPort)
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
def signUp(serverName , serverPort):
	try:
		userName = ''
		password = ''
		print 'Both username and password must be at least 8 characters long'
		##--Username and password must be 8+ chars and not contain &&& --##
		while len(userName) < 8 or userName.find('&&&') != -1:
			userName = raw_input('userName : ')
			if len(userName) < 8: print 'Username is not long enough'
			if userName.find('&&&') != -1: print 'Not an acceptable username'
		while len(password) < 8 or password.find('&&&') != -1:
			password = getpass.getpass('Password : ')
			if len(password) < 8: print 'Password is not long enough'
			if password.find('&&&') != -1: print 'Not an acceptable password'
			
		password = saltHash(password , userName) #Encrypt password
		resp = sendData('signup' + '&&&' + userName + '&&&' + password , serverName , serverPort)
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
	if len(command) == 1: print 'set [var] (value)\nClear var value with #clear\n\nVariables that can be set:' + getKeyString(userSets)
	elif findInDict(command[1] , userSets):
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
				if command[2][:len(command[2])] != '/' and command[2] != '': command[2] += '/'
				if not os.path.isdir(command[2]):
					print command[2] + ' is not a directory'
					return userSets
			userSets[command[1]] = command[2]
	else:
		print command[1] + ' is not an available setting'
	return userSets

##--Admin controls require additional password--##
def admin(credentials , serverName , serverPort):
	password = getpass.getpass('Server Password: ')	#Ask for password to send to server
	resp = sendData(credentials + '&&&' + saltHash(password , 'masteradmin') , serverName , serverPort)
	if type(resp) != type(None): print resp
	sucBool = True
	if type(resp) == type(None) or resp[:6] == 'Error:':
		sucBool = False
	return sucBool

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

##--Returns True if value is found in given list--##
def findInList(item , listObj):
	try:
		for i in listObj:
			if i == item: return True
		return False
	except:
		return False

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

##--Returns checksum for given file using given hash--##
##Ex:  hashfile(open(fileName, 'rb'), hashlib.sha256())   #must be in r mode
def hashFile(afile, hasher, blocksize=65536):
	buf = afile.read(blocksize)
	while len(buf) > 0:
		hasher.update(buf)
		buf = afile.read(blocksize)
	afile.seek(0)
	return hasher.digest()
