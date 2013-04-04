#!/usr/bin/python

##--File Locket (server)
##--Created by Michael duPont (flyinactor91@gmail.com)
##--v1.0.0 [28 03 2013]
##--Python 2.7.3 - Unix

##--Known bugs:
##--	%T in time.strftime is causing error on Win x64

from serverCommands import *
from socket import *
import pickle , os , random , time

##--Main Server Function--##
def main():
	serverPort = 60145
	###The current server password is 'letmein'. To change, run the saltHash function found in client on your new password and paste the output below
	serverPassword = 'c4c98a50cf4abcd72737aff8679dc17b19a42eecb388c13133cd2de6685282578fe9c53320bae4b8b3ea88bf3e0079a35b4570bdfc81cad7cfb498f024b6fea3'
	quitFlag = False
	defaultTimeout = 5
	
	
	##--Check bin and make if unavailable--##
	if not os.path.isdir('bin'):
		os.mkdir('bin')
	##--Load in (via pickle) User and File dictionaries--##
	try:
		storageFile = open('bin/ServerStorage.pkl', 'rb')
		UserStorage = pickle.load(storageFile)
		FileStorage = pickle.load(storageFile)
		storageFile.close()
	except:
		UserStorage = {}
		FileStorage = {}
	
	serverSocket = socket(AF_INET , SOCK_STREAM)
	serverSocket.bind(('' , serverPort))
	serverSocket.listen(10)
	print 'The server is ready to recieve'
	
	##--Main Loop--##
	while not quitFlag:
		
		##--Begin once the server recieves a connection--##
		connectionSocket , addr = serverSocket.accept()
		connectionSocket.settimeout(defaultTimeout)
		stringIn = connectionSocket.recv(1024)
		stringIn = stringIn.split('&&&')
		command = stringIn[0]
		print str(addr) , stringIn[1] , command
		
		##--Command Rec--##
		
		##--Server creates new folder and library entries and returns valid sessionID--##
		if command == 'signup':
			try:
				uName = stringIn[1]
				pWord = stringIn[2]
				if findInDict(uName , UserStorage):
					connectionSocket.send('Error: Username already exists')
					print '\tusername failed'
				else:
					sessionID = str(random.randint(0 , 10**6))
					UserStorage[uName] = [pWord , sessionID]
					FileStorage[uName] = {}
					if not os.path.isdir((os.getcwd())+'/bin/'+uName):
						os.mkdir((os.getcwd())+'/bin/'+uName)
					connectionSocket.send('Signup successful:' + sessionID)
			except Exception , e:
				print '\tError: ' + str(e)
		
		##--Server returns valid sessionID--##
		elif command == 'login':
			try:
				uName = stringIn[1]
				pWord = stringIn[2]
				if findInDict(uName , UserStorage):
					if UserStorage[uName][0] == pWord:
						sessionID = str(random.randint(0 , 10**6))
						UserStorage[uName][1] = sessionID
						connectionSocket.send('Login successful:' + sessionID)
					else:
						connectionSocket.send('Error: Password does not match')
						print '\tpassword failed'
				else:
					connectionSocket.send('Error: Username does not exist')
					print '\tusername failed'
			except Exception , e:
				print '\tError: ' + str(e)
		
		##--Server recieves file and stores in user's folder--##
		elif command == 'sendfile':
			try:
				uName = stringIn[1]
				cont = checkCreds(uName , stringIn[2] , UserStorage)
				if cont == 'Y':
					connectionSocket.send('Connection successful')
					try:
						fileName = stringIn[3]
						fileLen = int(stringIn[4])
						finLen = 0
						fin = file('bin/'+uName+'/'+fileName , 'wb')
						while finLen < fileLen:
								line = connectionSocket.recv(1024)
								fin.write(line)
								finLen = getFileSize(fin)
						fin.close()
						if os.name == 'nt':   ##### %T is causing error on Win x64
							timeString = time.strftime('%d-%b-%Y')
						else:
							timeString = time.strftime('%d-%b-%Y %T')
						checksum = hashfile(open('bin/'+uName+'/'+fileName , 'rb') , hashlib.sha512())
						FileStorage[uName][fileName] = [timeString , checksum]
						connectionSocket.send('File received')
						print '\t' + fileName + '  success'
					except Exception , e:
						connectionSocket.send('File Save Error: ' + str(e))
						print '\t' + fileName + '  Error: ' + str(e)
				else:
					connectionSocket.send(cont)
			except Exception , e:
				print '\tError: ' + str(e)
		
		##--Sends the requested file to the user--##
		elif command == 'getfile':
			try:
				uName = stringIn[1]
				cont = checkCreds(uName , stringIn[2] , UserStorage)
				if cont == 'Y':
					ret = getKeyString(FileStorage[uName])
					if ret == '':
						ret = 'You have not uploaded any files'
						connectionSocket.send(ret)
					else:
						connectionSocket.send(ret)
						connectionSocket.settimeout(30)
						fileName = connectionSocket.recv(1024)
						if findInDict(fileName , FileStorage[uName]):
							connectionSocket.settimeout(defaultTimeout)
							fout = file('bin/'+uName+'/'+fileName , 'rb')
							fileLen = str(getFileSize(fout))
							connectionSocket.send(fileLen)
							rec = connectionSocket.recv(1024)
							if rec == 'send':
								outputData = fout.readlines()
								for line in outputData:
									sent = connectionSocket.send(line)
								rec = connectionSocket.recv(1024)
								print '\t' + fileName + '  ' + rec
							else:
								print '\t' + fileName + '  Error: recieve'
						else:
							print '\t' + fileName + '  Error: not found'
				else:
					connectionSocket.send(cont)
			except Exception , e:
				print '\tError: ' + str(e)
		
		##--Sends a list of the user's stored files--##
		elif command == 'showfiles':
			try:
				uName = stringIn[1]
				cont = checkCreds(uName , stringIn[2] , UserStorage)
				if cont == 'Y':
					ret = getKeyString(FileStorage[uName])
					if ret == '':
						ret = 'You have not uploaded any files'
					connectionSocket.send(ret)
				else:
					connectionSocket.send(cont)
			except Exception , e:
				print '\tError: ' + str(e)
		
		##--Deletes a user's stored file--##
		elif command == 'delfile':
			try:
				uName = stringIn[1]
				cont = checkCreds(uName , stringIn[2] , UserStorage)
				if cont == 'Y':
					ret = getKeyString(FileStorage[uName])
					if ret == '':
						ret = 'You have not uploaded any files'
						connectionSocket.send(ret)
					else:
						connectionSocket.send(ret)
						connectionSocket.settimeout(30)
						fileName = connectionSocket.recv(1024)
						connectionSocket.settimeout(defaultTimeout)
						os.remove('bin/'+uName+'/'+fileName)
						del FileStorage[uName][fileName]
						connectionSocket.send('File deleted')
				else:
					connectionSocket.send(cont)
			except Exception , e:
				print '\tError: ' + str(e)
		##--Tests connection and valid sessionID--##
		elif command == 'test':
			try:
				cont = checkCreds(stringIn[1] , stringIn[2] , UserStorage)
				if cont == 'Y':
						connectionSocket.send('Connection successful')
				else:
					connectionSocket.send(cont)
			except Exception , e:
				print '\tError: ' + str(e)
		
		##--Admin Tools--##
		##--Saves data and shuts down server--##
		elif command == 'adminshutdown':
			try:
				cont = checkCreds(stringIn[1] , stringIn[2] , UserStorage)
				if cont == 'Y':
					password = stringIn[3]
					if password == serverPassword:
						connectionSocket.send('Server is now shutting down')
						quitFlag = True
					else:
						print '\tincorrect password'
						connectionSocket.send('Error: Access Denied')
				else:
					connectionSocket.send(cont)
			except Exception , e:
				print '\tError: ' + str(e)
		
		##--Clears all server data--##
		elif command == 'adminclear':
			try:
				cont = checkCreds(stringIn[1] , stringIn[2] , UserStorage)
				if cont == 'Y':
					password = stringIn[3]
					if password == serverPassword:
						try:
							os.rename('bin' , '~~bin~~')
							os.mkdir('bin')
							UserStorage.clear()
							FileStorage.clear()
							connectionSocket.send('Server has reset all storage.')
						except OSError:
							print '\tbin backup still exists'
							connectionSocket.send('Error: Previous bin backup still exists')
						except:
							print '\terror'
							connectionSocket.send('Error: Unknown')
					else:
						print '\tincorrect password'
						connectionSocket.send('Access Denied')
				else:
					connectionSocket.send(cont)
			except Exception , e:
				print '\tError: ' + str(e)
		
		##--Returns all usernames in UserStorage--##
		elif command == 'adminshowusers':
			try:
				cont = checkCreds(stringIn[1] , stringIn[2] , UserStorage)
				if cont == 'Y':
					password = stringIn[3]
					if password == serverPassword:
						retString = '\nUsernames Stored on Server:'
						for key in UserStorage:
							retString += '\n\t' + key
						connectionSocket.send(retString)
					else:
						print '\tincorrect password'
						connectionSocket.send('Access Denied')
				else:
					connectionSocket.send(cont)
			except Exception , e:
				print '\tError: ' + str(e)
				
		##--Exception acts as a safeguard in case something went wrong during transmition--##
		else:
			try:
				print 'Command error'
				connectionSocket.send('Server did not recognise the command given')
			except Exception , e:
				print '\tError: ' + str(e)
		
		##--Close client connection--##
		connectionSocket.close()
	
		##--Constantly save storage data--##
		storageFile = open('bin/ServerStorage.pkl', 'wb')
		pickle.dump(UserStorage, storageFile)
		pickle.dump(FileStorage, storageFile)
		storageFile.close()
		##--End Main Loop--##
	
	serverSocket.close()
##--End main--##

main()
