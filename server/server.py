#!/usr/bin/python

##--File Locket (server)
##--Created by Michael duPont (flyinactor91@gmail.com)
##--v1.2.xa [2013-08-04]
##--Python 2.7.4 - Unix

from serverCommands import *
from socket import *
import pickle , os , random , time , shutil

##--Main Server Function--##
def main():
	##--Server settings--##
	serverPort = 60145
	###The current server password is 'letmein'. To change, run the saltHash function found in clientCommands on your new password and paste the output below
	serverPassword = 'c4c98a50cf4abcd72737aff8679dc17b19a42eecb388c13133cd2de6685282578fe9c53320bae4b8b3ea88bf3e0079a35b4570bdfc81cad7cfb498f024b6fea3'
	defaultTimeout = 5				#  Timeout used for normal connection conditions
	socketRecvBuffer = 1024			#  2**x
	maxConnectedClients = 1			#  Number of simultaneous clients that the server will accept
	fileBuffer = 500000				#  Amount of bits for server to recv and process at a time. View dev notes
	outputToFile = False				#  Server log sent to .txt (True) or sent to terminal (False)
	##--End settings--##
	
	serverVersion = '1.2.0 alpha [2013-08-04]'

	##--Accepted commands--##
	credCommands = ['sendfile' , 'recvfile' , 'viewfiles' , 'delfile' , 'versions' , 'recvver' , 'archive' , 'test' , 'stats' , 'viewalerts' , 'clearalerts' , 'adminshutdown' , 'adminclear' , 'adminshowusers' , 'adminserverstats' , 'adminsendalert']
	adminCommands = ['adminshutdown' , 'adminclear' , 'adminshowusers' , 'adminserverstats' , 'adminsendalert']
	noCredCommands = ['signup' , 'login']

	##--Check bin and make if unavailable--##
	if not os.path.isdir('bin'): os.mkdir('bin')
	##--Load in (via pickle) User and File dictionaries--##
	try:
		storageFile = open('bin/ServerStorage.pkl', 'rb')
		UserStorage = pickle.load(storageFile)
		FileStorage = pickle.load(storageFile)
		ServerStats = pickle.load(storageFile)
		storageFile.close()
	except:
		UserStorage = {}
		FileStorage = {}
		ServerStats = {'Total Files':0,'Total Files and Versions':0,'Total Users':0,'Critical Errors':0}

	if outputToFile: foutput = open('bin/serverLog.txt' , 'ab')
	else: foutput = None

	serverSocket = socket(AF_INET , SOCK_STREAM)
	serverSocket.bind(('' , serverPort))
	serverSocket.listen(maxConnectedClients)
	onlineTime = time.strftime('%Y-%m-%d %H:%M:%SZ' , time.gmtime())
	outputMsg(foutput , '\n\n'+onlineTime+'\nThe server is ready to recieve')

	##--Main Loop--##
	quitFlag = False
	while not quitFlag:
		try:
			##--Begin once the server recieves a connection--##
			connectionSocket , addr = serverSocket.accept()
			connectionSocket.settimeout(defaultTimeout)
			stringIn = connectionSocket.recv(socketRecvBuffer)
			stringIn = stringIn.split('&&&')
			command = stringIn[0]

			##--Command Rec--##

			##--Confirms server is online, not sent to log/terminal--##
			if command == 'inittest': connectionSocket.send('T') #Backwards compatable with v1.2.0
			elif command == 'versionTest': connectionSocket.send(serverVersion) #As of v1.2.xa [2013-07-20]
			elif command == 'alertNum':
				userName = stringIn[1]
				if userName in UserStorage: connectionSocket.send(str(len(UserStorage[userName][2])))
				else:
					connectionSocket.send('Error: Username does not exist')
					outputMsg(foutput , str(addr)+'  '+userName+'  '+command+'\n\tusername failed')

			##--Requires username and sessionID--##
			elif command in credCommands:
				userName = stringIn[1]
				outputMsg(foutput , str(addr)+'  '+userName+'  '+command)
				cont = checkCreds(userName , stringIn[2] , UserStorage , foutput)
				if cont == 'Y':

					##--Server recieves file and stores in user's folder--##
					if command == 'sendfile':
						fileName = stringIn[3]
						recvChecksum = stringIn[4]
						if fileName in FileStorage[userName] and FileStorage[userName][fileName][0] == recvChecksum:
							connectionSocket.send('File has not changed since last upload')
						else:
							connectionSocket.send(str(fileBuffer)+'&&&'+str(socketRecvBuffer))
							try:
								fileLen = int(stringIn[5])
								finLen = 0
								timeString = time.strftime('%Y-%m-%d %H:%M:%SZ' , time.gmtime())
								if not os.path.isfile('bin/'+userName+'/'+fileName):
									os.mkdir((os.getcwd())+'/bin/'+userName+'/.fileversions/'+fileName)
									FileStorage[userName][fileName] = ['',[]]
								fin = file('bin/'+userName+'/'+fileName , 'wb')
								finVer = file('bin/'+userName+'/.fileversions/'+fileName+'/'+str(len(FileStorage[userName][fileName][1]))+'%%%'+fileName , 'wb')
								curBuffer = 0
								while finLen < fileLen:
									line = connectionSocket.recv(socketRecvBuffer)
									curBuffer += len(line)
									if curBuffer >= fileBuffer:
										connectionSocket.send('cont')
										curBuffer = 0
									fin.write(line)
									finVer.write(line)
									finLen = getFileSize(fin)
									#print fileLen , finLen   #Good point to help figure out var fileBuffer
								fin.close()
								finVer.close()
								#checksum = hashFile(open('bin/'+userName+'/'+fileName , 'rb') , hashlib.sha512())
								FileStorage[userName][fileName][0] = recvChecksum
								FileStorage[userName][fileName][1].append(timeString)
								connectionSocket.send('File received')
								if len(FileStorage[userName][fileName][1]) == 1:
									ServerStats['Total Files'] += 1
									ServerStats['Total Files and Versions'] += 2
								else:
									ServerStats['Total Files and Versions'] += 1
								outputMsg(foutput , '\t' + fileName + '  success')
							except Exception , e:
								connectionSocket.send('File Save Error: ' + str(e))
								os.remove('bin/'+userName+'/'+fileName)
								os.remove('bin/'+userName+'/.fileversions/'+fileName+'/'+str(len(FileStorage[userName][fileName][1]))+'%%%'+fileName)
								ServerStats['Total Files and Versions'] = ServerStats['Total Files and Versions'] - (len(FileStorage[userName][fileName][1])+1)
								ServerStats['Total Files'] = ServerStats['Total Files'] - 1
								del FileStorage[userName][fileName]
								ServerStats['Critical Errors'] += 1
								criticalError(str(e) , stringIn , FileStorage[userName])
								outputMsg(foutput , '\t' + fileName + '  Error: ' + str(e))

					##--Sends the requested file to the user--##
					elif command == 'recvfile':
						fileName = stringIn[3]
						if fileName in FileStorage[userName]:
							msg = sendFile(connectionSocket , file('bin/'+userName+'/'+fileName , 'rb') , socketRecvBuffer)
							outputMsg(foutput , '\t' + fileName + '  ' + msg)
						else:
							connectionSocket.send('Error: not a file')
							outputMsg(foutput , '\t' + fileName + '  Error: not a file')

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
							ServerStats['Total Files and Versions'] = ServerStats['Total Files and Versions'] - (len(FileStorage[userName][fileName][1])+1)
							ServerStats['Total Files'] = ServerStats['Total Files'] - 1
							del FileStorage[userName][fileName]
							connectionSocket.send('File deleted')
						else:
							outputMsg(foutput , '\t' + fileName + '  Error: not found')

					##--Sends a list of versions for a given file--##
					elif command == 'versions':
						fileName = stringIn[3]
						if fileName in FileStorage[userName]: connectionSocket.send(getNumListString(FileStorage[userName][fileName][1],True))

					##--Lets user download previous file versions--##
					elif command == 'recvver':
						fileName = stringIn[3]
						try:
							msg = sendFile(connectionSocket , file('bin/'+userName+'/.fileversions/'+fileName , 'rb') , socketRecvBuffer)
							outputMsg(foutput , '\t' + fileName + '  ' + msg)
						except IOError:
							connectionSocket.send('Error: Not a file or version')
							outputMsg(foutput , '\tNot a file')

					##--Sends the user an archive of their files--##
					elif command == 'archive':
						makeZip(userName , 'bin/'+userName , stringIn[3])
						msg = sendFile(connectionSocket , file(userName+'.zip' , 'rb') , socketRecvBuffer)
						outputMsg(foutput , '\t' + msg)
						os.remove(userName+'.zip')

					##--Tests connection and valid sessionID--##
					elif command == 'test':
						connectionSocket.send('Connection successful')

					##--Sends formatted string of the user's stats--##
					elif command == 'stats':
						ret = '\nNumber of Files:  '+str(len(FileStorage[userName]))
						verNum = 0
						for fileName in FileStorage[userName]: verNum += len(FileStorage[userName][fileName][1])
						ret += '\nTotal Stored Versions:  '+str(verNum)
						storeSize = getFolderSize('bin/'+userName)/(1024*1024.0)
						verSize = getFolderSize('bin/'+userName+'/.fileversions')/(1024*1024.0)
						ret += '\nApprox Storage Size:  %0.3f MB' % (storeSize-verSize)
						ret += '\n***** with Versions:  %0.3f MB' % (storeSize)
						connectionSocket.send(ret)
					
					##--Sends number of alerts or foratted string of alerts to user--##
					elif command == 'viewalerts':
						if stringIn[3]:
							if len(UserStorage[userName][2]) == 0: ret = 'You have no alerts'
							else: ret = getNumListString(UserStorage[userName][2])
							connectionSocket.send(ret)
						else: connectionSocket.send(str(len(UserStorage[userName][2])))
					
					##--Clears user's alerts--##
					elif command == 'clearalerts':
						UserStorage[userName][2] = []
						connectionSocket.send('Alerts have been cleared')

					##--Admin Tools--##
					elif command in adminCommands:
						if stringIn[3] == serverPassword:

							##--Saves data and shuts down server--##
							if command == 'adminshutdown':
								quitFlag = True
								connectionSocket.send('Server is now shutting down')

							##--Clears all server data--##
							elif command == 'adminclear':
								try:
									os.rename('bin' , '~~bin~~')
									os.mkdir('bin')
									UserStorage.clear()
									FileStorage.clear()
									ServerStats = {'Total Files':0,'Total Files and Versions':0,'Total Users':0,'Critical Errors':0}
									if outputToFile: foutput = open('bin/serverLog.txt' , 'ab')
									else: foutput = None
									resetTime = time.strftime('%Y-%m-%d %H:%M:%SZ' , time.gmtime())
									outputMsg(foutput , '\n\n'+resetTime+'\nThe server is ready to recieve after adminclear')
									connectionSocket.send('Server has reset all storage')
								except OSError:
									outputMsg(foutput , '\tbin backup still exists')
									connectionSocket.send('Error: Previous bin backup still exists')
								except Exception , e:
									outputMsg(foutput , '\tError: ' + str(e))
									ServerStats['Critical Errors'] += 1
									criticalError(str(e) , stringIn)
									connectionSocket.send('Error: Unknown')

							##--Returns all usernames in UserStorage--##
							elif command == 'adminshowusers':
								connectionSocket.send('\nUsernames Stored on Server:' + getKeyString(UserStorage , '\n\t'))

							##--Returns all usernames in UserStorage--##
							elif command == 'adminserverstats':
								ret = getKeyString(ServerStats , '\n' , ':  ')
								ret += '\nApprox Server Size:  %0.3f MB' % (getFolderSize('bin')/(1024*1024.0))
								ret += '\nTime Online:  '+onlineTime
								if 'resetTime' in locals(): ret += '\nTime of Last Reset:  '+resetTime
								connectionSocket.send(ret)
							
							##--Admin alert--##
							elif command == 'adminsendalert':
								targetUser = stringIn[4]
								if targetUser == 'all':
									for user in UserStorage: UserStorage[user][2].append(stringIn[5])
									connectionSocket.send('Alert has been sent to all users')
								elif targetUser in UserStorage:
									UserStorage[targetUser][2].append(stringIn[5])
									connectionSocket.send('Alert has been sent to ' + targetUser)
								else:
									connectionSocket.send('Error: Could not send the alert to '+targetUser+'. User does not exist')
						else:
							outputMsg(foutput , '\tincorrect password')
							connectionSocket.send('Error: Access Denied')
				else: connectionSocket.send(cont)

			##--Requires username and password--##
			elif command in noCredCommands:
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
						UserStorage[userName] = [pWord , sessionID , []]
						FileStorage[userName] = {}
						if not os.path.isdir((os.getcwd())+'/bin/'+userName):
							os.mkdir((os.getcwd())+'/bin/'+userName)
							os.mkdir((os.getcwd())+'/bin/'+userName+'/.fileversions')
						ServerStats['Total Users'] += 1
						connectionSocket.send('success&&&' + sessionID)

				##--Server returns valid sessionID--##
				elif command == 'login':
					if userName in UserStorage:
						if UserStorage[userName][0] == pWord:
							sessionID = str(random.randint(0 , 10**6))
							UserStorage[userName][1] = sessionID
							connectionSocket.send('success&&&' + sessionID)
						else:
							connectionSocket.send('Error: Password does not match')
							outputMsg(foutput , '\tpassword failed')
					else:
						connectionSocket.send('Error: Username does not exist')
						outputMsg(foutput , '\tusername failed')

			##--Exception acts as a safeguard in case something went wrong during transmition--##
			else:
				outputMsg(foutput , str(addr)+'  Command error')
				ServerStats['Critical Errors'] += 1
				criticalError(stringIn)
				connectionSocket.send('Server did not recognise the command given')
		except Exception , e:
			ServerStats['Critical Errors'] += 1
			criticalError(str(e) , stringIn)
			outputMsg(foutput , '\tError: ' + str(e))

		##--Close client connection--##
		connectionSocket.close()

		##--Constantly save storage data--##
		storageFile = open('bin/ServerStorage.pkl', 'wb')
		pickle.dump(UserStorage, storageFile)
		pickle.dump(FileStorage, storageFile)
		pickle.dump(ServerStats, storageFile)
		storageFile.close()
		##--End Main Loop--##

	if outputToFile: foutput.close()
	serverSocket.close()
	##--End main--##

main()
