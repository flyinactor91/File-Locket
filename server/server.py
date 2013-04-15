#!/usr/bin/python

##--File Locket (server)
##--Created by Michael duPont (flyinactor91@gmail.com)
##--v1.1.0a [15 04 2013]
##--Python 2.7.4 - Unix

from serverCommands import *
from socket import *
import pickle , os , random , time , shutil

##--Main Server Function--##
def main():
	##--Server custom settings--##
	serverPort = 60145
	###The current server password is 'letmein'. To change, run the saltHash function found in clientCommands on your new password and paste the output below
	serverPassword = 'c4c98a50cf4abcd72737aff8679dc17b19a42eecb388c13133cd2de6685282578fe9c53320bae4b8b3ea88bf3e0079a35b4570bdfc81cad7cfb498f024b6fea3'
	defaultTimeout = .1			#  Timeout used for normal connection conditions
	userInputTimeout = 30		#  Timeout when response is needed to be typed by client
	socketRecvBuffer = 1024 	#  2**x
	maxConnectedClients = 1		#Number of simultaneous clients that the server will accept
	outputToFile = True			#  Server log sent to .txt (True) or sent to terminal (False)
	##--End settings--##
	
	##--Accepted commands--##
	noCredCommands = ['signup' , 'login']
	credCommands = ['sendfile' , 'recvfile' , 'viewfiles' , 'delfile' , 'versions' , 'recvver' , 'archive' , 'test' , 'adminshutdown' , 'adminclear' , 'adminshowusers']
	
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
	
	if outputToFile: foutput = open('bin/serverLog.txt' , 'ab')
	else: foutput = None
	
	serverSocket = socket(AF_INET , SOCK_STREAM)
	serverSocket.bind(('' , serverPort))
	serverSocket.listen(maxConnectedClients)
	outputMsg(foutput , '\n\n'+time.strftime('%d:%m:%Y-%X')+'\nThe server is ready to recieve')
	
	##--Main Loop--##
	quitFlag = False
	while not quitFlag:
		#try:
		##--Begin once the server recieves a connection--##
		connectionSocket , addr = serverSocket.accept()
		connectionSocket.settimeout(defaultTimeout)
		stringIn = connectionSocket.recv(socketRecvBuffer)
		stringIn = stringIn.split('&&&')
		command = stringIn[0]
		
		##--Command Rec--##
		
		##--Requires username and password--##
		if command in noCredCommands:
			userName = stringIn[1]
			pWord = stringIn[2]
			outputMsg(foutput , str(addr)+'  '+userName+'  '+command)
			
			##--Server creates new folder and library entries and returns valid sessionID--##
			if command == 'signup':
				if userName in UserStorage:
					connectionSocket.send('Error: Username already exists')
					outputMsg(foutput , '\tusername failed')
				else:
					sessionID = str(random.randint(0 , 10**6))
					UserStorage[userName] = [pWord , sessionID]
					FileStorage[userName] = {}
					if not os.path.isdir((os.getcwd())+'/bin/'+userName):
						os.mkdir((os.getcwd())+'/bin/'+userName)
						os.mkdir((os.getcwd())+'/bin/'+userName+'/.fileversions')
					connectionSocket.send('Signup successful:' + sessionID)
			
			##--Server returns valid sessionID--##
			elif command == 'login':
				if userName in UserStorage:
					if UserStorage[userName][0] == pWord:
						sessionID = str(random.randint(0 , 10**6))
						UserStorage[userName][1] = sessionID
						connectionSocket.send('Login successful:' + sessionID)
					else:
						connectionSocket.send('Error: Password does not match')
						outputMsg(foutput , '\tpassword failed')
				else:
					connectionSocket.send('Error: Username does not exist')
					outputMsg(foutput , '\tusername failed')
		
		##--Requires username and sessionID--##
		elif command in credCommands:
			userName = stringIn[1]
			sessionID = stringIn[2]
			outputMsg(foutput , str(addr)+'  '+userName+'  '+command)
			cont = checkCreds(userName , sessionID , UserStorage , foutput)
			if cont == 'Y':
				
				##--Server recieves file and stores in user's folder--##
				if command == 'sendfile':
					fileName = stringIn[3]
					recvChecksum = stringIn[4]
					if fileName in FileStorage[userName] and FileStorage[userName][fileName][0] == recvChecksum:
						connectionSocket.send('File has not changed since last upload')
					else:
						connectionSocket.send('Connection successful')
						try:
							fileLen = int(stringIn[5])
							finLen = 0
							timeString = time.strftime('%d:%m:%Y-%X')
							fin = file('bin/'+userName+'/'+fileName , 'wb')
							if not os.path.isdir('bin/'+userName+'/.fileversions/'+fileName):
								os.mkdir((os.getcwd())+'/bin/'+userName+'/.fileversions/'+fileName)
								FileStorage[userName][fileName] = ['',[]]
							finVer = file('bin/'+userName+'/.fileversions/'+fileName+'/'+str(len(FileStorage[userName][fileName][1]))+'%%%'+fileName , 'wb')
							while finLen < fileLen:
									line = connectionSocket.recv(socketRecvBuffer)
									fin.write(line)
									finVer.write(line)
									finLen = getFileSize(fin)
							fin.close()
							finVer.close()
							checksum = hashFile(open('bin/'+userName+'/'+fileName , 'rb') , hashlib.sha512())
							FileStorage[userName][fileName][0] = checksum
							FileStorage[userName][fileName][1].append(timeString)
							connectionSocket.send('File received')
							outputMsg(foutput , '\t' + fileName + '  success')
						except Exception , e:
							connectionSocket.send('File Save Error: ' + str(e))
							outputMsg(foutput , '\t' + fileName + '  Error: ' + str(e))
				
				##--Sends the requested file to the user--##
				elif command == 'recvfile':
					fileName = stringIn[3]
					if fileName in FileStorage[userName]:
						connectionSocket.settimeout(defaultTimeout)
						fout = file('bin/'+userName+'/'+fileName , 'rb')
						fileLen = str(getFileSize(fout))
						connectionSocket.send(fileLen)
						rec = connectionSocket.recv(socketRecvBuffer)
						if rec == 'send':
							outputData = fout.readlines()
							for line in outputData:
								sent = connectionSocket.send(line)
							rec = connectionSocket.recv(socketRecvBuffer)
							outputMsg(foutput , '\t' + fileName + '  ' + rec)
						else:
							outputMsg(foutput , '\t' + fileName + '  Error: recieve')
					else:
						outputMsg(foutput , '\t' + fileName + '  Error: not found')
				
				##--Sends a list of the user's stored files--##
				elif command == 'viewfiles':
					ret = getKeyString(FileStorage[userName] , '\n')
					if ret == '':
						ret = 'You have not uploaded any files'
					connectionSocket.send(ret)
	
				##--Deletes a user's stored file and versions--##
				elif command == 'delfile':
					fileName = stringIn[3]
					if fileName in FileStorage[userName]:
						os.remove('bin/'+userName+'/'+fileName)
						shutil.rmtree('bin/'+userName+'/.fileversions/'+fileName)
						del FileStorage[userName][fileName]
						connectionSocket.send('File deleted')
					else:
						outputMsg(foutput , '\t' + fileName + '  Error: not found')

				elif command == 'versions':
					fileName = stringIn[3]
					if fileName in FileStorage[userName]: connectionSocket.send(getNumListString(FileStorage[userName][fileName][1]))
				
				##--Lets user download previous file versions--##
				elif command == 'recvver':
					fileName = stringIn[3]
					try:
						fout = file('bin/'+userName+'/.fileversions/'+fileName , 'rb')
						fileLen = str(getFileSize(fout))
						connectionSocket.send(fileLen)
						rec = connectionSocket.recv(socketRecvBuffer)
						if rec == 'send':
							outputData = fout.readlines()
							for line in outputData:
								sent = connectionSocket.send(line)
							rec = connectionSocket.recv(socketRecvBuffer)
							outputMsg(foutput , '\t' + fileName[fileName.find('/')+1:] + '  ' + rec)
						else:
							outputMsg(foutput , '\t' + fileName[fileName.find('/')+1:] + '  Error: recieve')
					except IOError:
						connectionSocket.send(line)
						outputMsg(foutput , '\tNot a file')
				
				##--Sends the user an archive of their files--##
				elif command == 'archive':
					makeZip(userName , 'bin/'+userName , stringIn[3])
					fout = file(userName+'.zip' , 'rb')
					fileLen = str(getFileSize(fout))
					connectionSocket.send(fileLen)
					rec = connectionSocket.recv(socketRecvBuffer)
					if rec == 'send':
						outputData = fout.readlines()
						for line in outputData:
							sent = connectionSocket.send(line)
						rec = connectionSocket.recv(socketRecvBuffer)
						os.remove(userName+'.zip')
					else:
						outputMsg(foutput , '\tError')
						
				##--Tests connection and valid sessionID--##
				elif command == 'test':
					connectionSocket.send('Connection successful')
	
				##--Admin Tools--##
				##--Saves data and shuts down server--##
				elif command == 'adminshutdown':
					password = stringIn[3]
					if password == serverPassword:
						connectionSocket.send('Server is now shutting down')
						quitFlag = True
					else:
						outputMsg(foutput , '\tincorrect password')
						connectionSocket.send('Error: Access Denied')
	
				##--Clears all server data--##
				elif command == 'adminclear':
					password = stringIn[3]
					if password == serverPassword:
						try:
							os.rename('bin' , '~~bin~~')
							os.mkdir('bin')
							UserStorage.clear()
							FileStorage.clear()
							if outputToFile: foutput = open('bin/serverLog.txt' , 'ab')
							else: foutput = None
							outputMsg(foutput , '\n\n'+time.strftime('%d:%m:%Y-%X')+'\nThe server is ready to recieve after adminclear')
							connectionSocket.send('Server has reset all storage.')
						except OSError:
							outputMsg(foutput , '\tbin backup still exists')
							connectionSocket.send('Error: Previous bin backup still exists')
						except:
							outputMsg(foutput , '\terror')
							connectionSocket.send('Error: Unknown')
					else:
						outputMsg(foutput , '\tincorrect password')
						connectionSocket.send('Access Denied')
	
				##--Returns all usernames in UserStorage--##
				elif command == 'adminshowusers':
					password = stringIn[3]
					if password == serverPassword:
						connectionSocket.send('\nUsernames Stored on Server:' + getKeyString(UserStorage , '\n\t'))
					else:
						outputMsg(foutput , '\tincorrect password')
						connectionSocket.send('Access Denied')

			else:
				connectionSocket.send(cont)
		
		##--Exception acts as a safeguard in case something went wrong during transmition--##
		else:
			outputMsg(foutput , str(addr)+'  Command error')
			connectionSocket.send('Server did not recognise the command given')
		#except Exception , e:
			#outputMsg(foutput , '\tError: ' + str(e))
		
		##--Close client connection--##
		connectionSocket.close()
	
		##--Constantly save storage data--##
		storageFile = open('bin/ServerStorage.pkl', 'wb')
		pickle.dump(UserStorage, storageFile)
		pickle.dump(FileStorage, storageFile)
		storageFile.close()
		##--End Main Loop--##
		
	if outputToFile:
		foutput.close()
	serverSocket.close()
	##--End main--##

main()
