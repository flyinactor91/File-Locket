#!/usr/bin/python

##--File Locket (server)
##--Created by Michael duPont (flyinactor91@gmail.com)
##--v2.0.0 [2013-09-27]
##--Python 2.7.5 - Unix

from serverCommands import *
from socket import *
import pickle , os , random , time , shutil

##--Server settings--##
serverPort = 60145
###The current server password is 'letmein'. To change, run the saltHash function found in clientCommands on your new password with 'masteradmin' as the user and paste the output below
serverPassword = 'c4c98a50cf4abcd72737aff8679dc17b19a42eecb388c13133cd2de6685282578fe9c53320bae4b8b3ea88bf3e0079a35b4570bdfc81cad7cfb498f024b6fea3'
defaultTimeout = 5				#  Seconds. Timeout used for normal connection conditions
socketRecvBuffer = 1024			#  2**x Chars server gets from socket at one time
maxConnectedClients = 1			#  Number of simultaneous clients that the server will accept
fileBuffer = 500000				#  Amount of chars for server to recv and process at one time. View dev notes
outputToFile = True				#  Server log sent to .txt (True) or sent to terminal (False)
##--End settings--##

##--Used at client startup. For client function, string must start int.int.int ; Everything behind it will only be used in a print statement--##
serverVersion = '2.0.0 [2013-09-27]'

##--Accepted commands--##
credCommands = ['send' , 'get' , 'view' , 'del' , 'viewver' , 'recvver' , 'arc' , 'test' , 'stat' , 'viewnot' , 'clearnot' , 'shutdown' , 'clear' , 'showusers' , 'serverstat' , 'sendnotif']
adminCommands = ['shutdown' , 'clear' , 'showusers' , 'serverstat' , 'sendnotif']
noCredCommands = ['signup' , 'login']



##--Main Server Function--##
def main():
	
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
	
	##--Open or create output file. Else will print to terminal--##
	if outputToFile: foutput = open('bin/serverLog.txt' , 'ab')
	else: foutput = None
	
	##--Init server socket--##
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

			##--Command Recognition--##

			##--Sent upon client startup, not sent to log/terminal--##
			##--Send version number for client comparison--##
			if command == 'versionTest': connectionSocket.send(serverVersion)
			##--Send int number of notifications--##
			elif command == 'notifNum':
				userName = stringIn[1]
				if userName in UserStorage: connectionSocket.send(str(len(UserStorage[userName][2])))
				else:
					connectionSocket.send('Error: Username does not exist')
					outputMsg(foutput , str(addr)+'  '+userName+'  '+command+'\n\tusername failed')

			##--Requires username and sessionID--##
			elif command in credCommands:
				userName = stringIn[1]
				outputMsg(foutput , str(addr)+'  '+userName+'  '+command)
				cont = checkCreds(userName , stringIn[2] , UserStorage , foutput) #Returns 'Y' to continue. Else returns error string
				if cont == 'Y':

					##--Server recieves file and stores in user's folder--##
					if command == 'send':
						fileName = stringIn[3]
						recvChecksum = stringIn[4]
						##--Checks Whether file has changed. If not, send error and quit--##
						if fileName in FileStorage[userName] and FileStorage[userName][fileName][0] == recvChecksum:
							connectionSocket.send('File has not changed since last upload')
						else:
							##--Send file transfer buffers--##
							connectionSocket.send(str(fileBuffer)+'&&&'+str(socketRecvBuffer))
							try:
								fileLen = int(stringIn[5])	#Length of incoming file
								finLen = 0					#Length server has recieved
								timeString = time.strftime('%Y-%m-%d %H:%M:%SZ' , time.gmtime())
								##--Open file--##
								fin = file('bin/'+userName+'/'+fileName , 'wb')
								curBuffer = 0	#Like finLen but used with fileBuffer
								##--Recieve until file on server matches length of file on client--##
								while finLen < fileLen:
									line = connectionSocket.recv(socketRecvBuffer)
									curBuffer += len(line)
									##--Once curBuffer equals or exceeds fileBuffer, send client int of total length recieved--##
									if curBuffer >= fileBuffer:
										connectionSocket.send(str(finLen))
										curBuffer = 0
									fin.write(line)
									finLen = getFileSize(fin)	#More reliable to check the actual length of the file than track the incoming chars
									#print fileLen , finLen   #Good point to help figure out var fileBuffer
								fin.close()
								checksum = hashFile('bin/'+userName+'/'+fileName , hashlib.sha256())
								##--Checks if both files are the same via checksum--##
								if checksum != recvChecksum:
									connectionSocket.send('File Send Error: Checksum did not match. Try sending again')
									outputMsg(foutput , '\tchecksum error')
								else:
									##--If file is new, create data and version folder--##
									if fileName not in FileStorage[userName]: FileStorage[userName][fileName] = ['',[]]	#['checksum string',[list of versions by date]]
									if not os.path.isdir('bin/'+userName+'/.fileversions/'+fileName): os.mkdir('bin/'+userName+'/.fileversions/'+fileName)
									FileStorage[userName][fileName][0] = recvChecksum		#Store checksum
									FileStorage[userName][fileName][1].append(timeString)	#Store date-time in version list
									##--Copy recieved file into .fileversions/filename/x%%%filename--##
									shutil.copy2('bin/'+userName+'/'+fileName , 'bin/'+userName+'/.fileversions/'+fileName+'/'+str(len(FileStorage[userName][fileName][1]))+'%%%'+fileName)
									##--If first upload, increase total file and version count. Else just version count--##
									if len(FileStorage[userName][fileName][1]) == 1:
										ServerStats['Total Files'] += 1
										ServerStats['Total Files and Versions'] += 2
									else:
										ServerStats['Total Files and Versions'] += 1
									connectionSocket.send('File received')
									outputMsg(foutput , '\t' + fileName + '  success')
							except Exception , e:
								connectionSocket.send('File Save Error: ' + str(e))
								ServerStats['Critical Errors'] += 1
								criticalError(str(e) , stringIn , FileStorage[userName])
								outputMsg(foutput , '\t' + fileName + '  Error: ' + str(e))

					##--Sends the requested file to the user--##
					elif command == 'get':
						fileName = stringIn[3]
						if fileName in FileStorage[userName]:
							msg = sendFile(connectionSocket , 'bin/'+userName+'/'+fileName , socketRecvBuffer)
							outputMsg(foutput , '\t' + fileName + '  ' + msg)
						else:
							connectionSocket.send('Error: not a file')
							outputMsg(foutput , '\t' + fileName + '  Error: not a file')

					##--Sends a list of the user's stored files--##
					elif command == 'view':
						ret = getKeyString(FileStorage[userName] , '\n')
						if ret == '':
							ret = 'You have not uploaded any files'
						connectionSocket.send(ret)

					##--Deletes a user's stored file and versions--##
					elif command == 'del':
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
					elif command == 'viewver':
						fileName = stringIn[3]
						if fileName in FileStorage[userName]: connectionSocket.send(getNumListString(FileStorage[userName][fileName][1],True))

					##--Lets user download previous file versions--##
					elif command == 'recvver':
						fileName = stringIn[3]
						try:
							msg = sendFile(connectionSocket , 'bin/'+userName+'/.fileversions/'+fileName , socketRecvBuffer)
							outputMsg(foutput , '\t' + fileName + '  ' + msg)
						except IOError:
							connectionSocket.send('Error: Not a file or version')
							outputMsg(foutput , '\tNot a file')

					##--Sends the user an archive of their files--##
					elif command == 'arc':
						makeZip(userName , 'bin/'+userName , stringIn[3])
						msg = sendFile(connectionSocket , userName+'.zip' , socketRecvBuffer)
						outputMsg(foutput , '\t' + msg)
						os.remove(userName+'.zip')

					##--Tests connection and valid sessionID--##
					elif command == 'test':
						connectionSocket.send('Connection successful')

					##--Sends formatted string of the user's stats--##
					elif command == 'stat':
						ret = '\nNumber of Files:  '+str(len(FileStorage[userName]))
						verNum = 0
						for fileName in FileStorage[userName]: verNum += len(FileStorage[userName][fileName][1])
						ret += '\nTotal Stored Versions:  '+str(verNum)
						storeSize = getFolderSize('bin/'+userName)/(1024*1024.0)	#Size in every file in MB
						verSize = getFolderSize('bin/'+userName+'/.fileversions')/(1024*1024.0)		#Size of version folder in MB
						ret += '\nApprox Storage Size:  {0:.3f} MB'.format(storeSize-verSize)
						ret += '\n***** with Versions:  {0:.3f} MB'.format(storeSize)
						connectionSocket.send(ret)
					
					##--Sends number or foratted string of notifications to user--##
					elif command == 'viewnot':
						if stringIn[3]:
							if len(UserStorage[userName][2]) == 0: ret = 'You have no notifications'
							else: ret = getNumListString(UserStorage[userName][2])
							connectionSocket.send(ret)
						##--The # only command was moved out of cred commands because it's called at start-up--##
						##--This line is kept in case this functionality is needed in the future--##
						else: connectionSocket.send(str(len(UserStorage[userName][2])))
					
					##--Clears user's notifiactions--##
					elif command == 'clearnot':
						UserStorage[userName][2] = []
						connectionSocket.send('Notifiactions have been cleared')

					##--Admin Tools--##
					elif command in adminCommands:
						if stringIn[3] == serverPassword:

							##--Saves data and shuts down server--##
							if command == 'shutdown':
								quitFlag = True
								connectionSocket.send('Server is now shutting down')

							##--Clears all server data--##
							elif command == 'clear':
								try:
									##--Save old data by renaming file--##
									##--This command will fail here if the old bin still exists as a precaution--##
									os.rename('bin' , '~~bin~~')
									##--Reset all server databases--##
									UserStorage.clear()
									FileStorage.clear()
									ServerStats = {'Total Files':0,'Total Files and Versions':0,'Total Users':0,'Critical Errors':0}
									##--Rebuild file system--##
									os.mkdir('bin')
									if outputToFile: foutput = open('bin/serverLog.txt' , 'ab')
									else: foutput = None
									resetTime = time.strftime('%Y-%m-%d %H:%M:%SZ' , time.gmtime())
									outputMsg(foutput , '\n\n'+resetTime+'\nThe server is ready to recieve after adminclear')
									connectionSocket.send('Server has reset all storage')
								
								##--Raises if ~~bin~~ still exists. Prevents database from accidental deletion--##
								except OSError:
									outputMsg(foutput , '\tbin backup still exists')
									connectionSocket.send('Error: Previous bin backup still exists')
								except Exception , e:
									outputMsg(foutput , '\tError: ' + str(e))
									ServerStats['Critical Errors'] += 1
									criticalError(str(e) , stringIn)
									connectionSocket.send('Error: Unknown')

							##--Returns all usernames in UserStorage--##
							elif command == 'showusers':
								connectionSocket.send('\nUsernames Stored on Server:' + getKeyString(UserStorage , '\n\t'))

							##--Returns all usernames in UserStorage--##
							elif command == 'serverstat':
								ret = getKeyString(ServerStats , '\n' , ':  ')
								ret += '\nApprox Server Size:  {0:.3f} MB'.format(getFolderSize('bin')/(1024*1024.0))
								ret += '\nTime Online:  '+onlineTime
								if 'resetTime' in locals(): ret += '\nTime of Last Reset:  '+resetTime
								connectionSocket.send(ret)
							
							##--Admin Notify--##
							elif command == 'sendnotif':
								targetUser = stringIn[4]
								if targetUser == 'all':
									for user in UserStorage: UserStorage[user][2].append(stringIn[5])
									connectionSocket.send('Notification has been sent to all users')
								elif targetUser in UserStorage:
									UserStorage[targetUser][2].append(stringIn[5])
									connectionSocket.send('Notification has been sent to ' + targetUser)
								else:
									connectionSocket.send('Error: Could not send the notification to '+targetUser+'. User does not exist')
						
						##--If server password did not match--##
						else:
							outputMsg(foutput , '\tincorrect password')
							connectionSocket.send('Error: Access Denied')
				
				##--If username or session ID did not match--##
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
				outputMsg(foutput , str(addr)+'  Command error  '+command)
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
