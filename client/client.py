#!/usr/bin/python

##--Michael duPont
##--Change "serverName" in clientCommands to IP of server host before running

from clientCommands import *
from socket import *
import pickle , sys , platform

aboutString = """
File Locket
Created by Michael duPont (flyinactor91@gmail.com)
v1.2.xa [22 07 2013]
Python 2.7.4 - Unix

Simple file storage service
Store, access, and delete files
Files are versioned and can be downloaded"""

helpString = """
Available commands:
	sendfile	Send a file to the server
	getfile		Get a file from the server
	viewfiles	View stored files
	delfile		Delete a file on the server
	versions	File version options
	archive		Get all files on server (versions if true)
	set		Change program settings
	stats		Get info about about files
	alerts		Alert options
	test		Test server connection
	logout		Logout and quit
	quit		Quit without logging out

Admin Tools (requires server pw):
	adminshowusers		Returns all saved usernames
	adminserverstats	Returns server statistics
	adminsendalert		Send alert to all users
	adminclear		Clears all server lib data
	adminshutdown		Shuts down server and saves data

Typing #quit into a prompt exits that prompt"""

noteString = """
1.0.0 [28 03 2013]
	Initial release

1.1.0 [10 04 2013]
	File versioning
	Source and destination directory control
	File transfer improvements
	Server improvements

1.1.1 [23 04 2013]
	User and server statistics
	Recieve file archive
	Client and Server improvements

1.2.0 [17 07 2013]
	Windows/NT support
	#up for directory control
	Signup verifies password
	More reliable file transfers
	Bug fixes
	Code reduction

1.2.xa [22 07 2013]
	Check version on startup
	Notification system
	Client and Server improvements
	Bug fixes"""

helpStrings = {'sendfile':'\nsendfile (local file)\nSends a file to the server.',
			   'getfile':'\ngetfile (file on server)\nRecieve a file from the server\nCalling getfile without file name calls viewfiles and a prompt',
			   'viewfiles':"\nviewfiles\nDisplays all the user's files stored on the server",
			   'delfile':'\ndelfile (file on server)\nPerminantly delete a file and its saved versions from the server\nCalling delfile without file name calls viewfiles and a prompt',
			   'versions':'\nversions [command] (file on server) (file version #)\nAvailable commands:\n\tview - View all the versions of a file stored on the server\n\tget - Recieve a file version from the server\nPrompts will be called until all needed info is given',
			   'archive':"\narchive (true)\nRecieve a .zip archive of files stored on the server\nAlso includes the file versions if call followed by 'true'",
			   'set':"\nset (var) (value)\nUser can change program settings\nCalling set with only a var displays that var's value\nCall set by itself for a list of available vars",
			   'alerts':"\nalerts [command]\nAvailable commands:\n\tview - View user's current alerts\n\tclear - Clear user's alerts from the server",
			   'stats':'\nstats\nServer displays information like the number of files a user has uploaded',
			   'test':"\ntest\nContacts the server to check the connection as well as the user's credentials",
			   'logout':'\nlogout\nSigns out user and exits the program\nNote: Server is not contacted',
			   'quit':'\nquit\nExits the program without logging out',
			   'adminshowusers':'\nadminshowusers\nDisplays a list of all users signed up on this server\nRequires server password',
			   'adminserverstats':'\nadminserverstats\nDisplays general information about the server like number of users and approximate server size\nRequires server password',
			   'adminsendalert':'\nadminsendalert\nSend a system-wide alert to all users on the server\nRequires server password',
			   'adminclear':"\nadminclear\nResets the server's data storage and saves a backup of the previous files and data\nThis function cannot be called again while the previous backup exists\nRequires server password",
			   'adminshutdown':'\nadminshutdown\nRemotely shutdown the server\nRequires server password'}


##--Main Client Function--##
def main():
	
	clientVersion = '1.2.0'
	
	try:
		##--Load in (via pickle) client storage values--##
		storageFile = open('ClientStorage.pkl', 'rb')
		userName = pickle.load(storageFile)
		sessionID = pickle.load(storageFile)
		userSets = pickle.load(storageFile)
		storageFile.close()
	except:
		userName , sessionID = '' , ''
		userSets = {'senddir':'','destdir':'','startalert':'T'}

	##--Check if server is online and determines if client-server is compatable--##
	serverData = sendData('versionTest')
	serverVersion = serverData[:serverData.find(' ')]
	if serverVersion[:5] == 'Error': sys.exit('Error: Server is offline') #Program exits if server connection cannot be established
	compare = compareVersions(clientVersion.split('.') , serverVersion.split('.'))
	if compare == -1: print '\n\nClient ('+clientVersion+') is out of date and might not work with the server ('+serverData+')\nGo to https://github.com/flyinactor91/File-Locket to get the latest version\n\n'
	if compare == 1: print '\n\nClient ('+clientVersion+') is running a newer version and might not work with the server ('+serverData+')\n\n'
	#Can change to 'if x not in [list of acceptable versions]'
	
	##--Ask user for name and init--##
	if userName == '':
		while userName == '':
			lin = getInput('Login or Sign up? (L/S) : ').lower()
			if lin == 'l': userName , sessionID = startUp('login')
			elif lin == 's': userName , sessionID = startUp('signup')
			else: print 'Not an option. Use #quit to exit\n'
		##--Save userName and sessionID--##
		saveStorage(userName , sessionID , userSets)
	else:
		print 'Welcome back' , userName
	if userSets['startalert']:
		alertNum = int(sendData('viewalerts&&&'+userName+'&&&'+sessionID+'&&&'))
		if alertNum == 1: print 'You have 1 alert'
		elif alertNum > 1: print 'You have '+str(alertNum)+' alerts'
	print 'Program Info:  #about , #help (command) , #notes'

	##--Command Loop--##
	quitFlag = False
	while not quitFlag:
		command = raw_input('\ncmd: ').split(' ')   #Ask user for command input
		credentials = userName + '&&&' + sessionID

		##--Send a file to the server--##
		if command[0] == 'sendfile':
			if len(command) == 1:
				fileName = raw_input('File name: ')
				if fileName != '#quit': print sendFile(command[0]+'&&&'+credentials , fileName , userSets)
			elif len(command) == 2: print sendFile(command[0]+'&&&'+credentials , command[1] , userSets)
			else: print 'sendfile (local file)'

		##--Recieve a file from the server--##
		elif command[0] == 'getfile':
			if len(command) == 1:
				ret = sendData('viewfiles&&&'+credentials) #Server sends list of files (if any)
				print ret
				if ret != 'You have not uploaded any files':
					fileName = raw_input('\nFile: ')
					if fileName != '#quit':
						if fileName in ret.split('\n'): print recvFile('recvfile&&&'+credentials , fileName , userSets)
						else: print 'Error: Not an available file'
			elif len(command) == 2: print recvFile('recvfile&&&'+credentials , command[1] , userSets)
			else: print 'getfile (file on server)'

		##--Delete a file on the server--##
		elif command[0] == 'delfile':
			if len(command) == 1: print viewFileAndSend(credentials , command[0] , userSets)
			elif len(command) == 2: print sendData('delfile&&&'+credentials+'&&&'+command[1])
			else: print 'delfile (file on server)'

		##--View file versions (and) get a versioned file from the server--##
		elif command[0] == 'versions':
			if len(command) == 2:
				ret = viewFileAndSend(credentials , command[0] , userSets)
				if type(ret) != tuple: print ret
				else:
					print ret[0]
					if command[1] == 'get':
						verNum = raw_input('\nVersion number: ')
						if verNum != '#quit':
							if int(verNum) != 0 and int(verNum)-1 in range(len(ret[0].split('\n'))-3):
								fileName = ret[1]
								print recvFile('recvver&&&'+credentials , fileName+'/'+str(int(verNum)-1)+'%%%'+fileName , userSets)
							else: print 'Error: Not an applicable number'
			elif len(command) == 3:
				fileName = command[2]
				ret = sendData(command[0]+'&&&'+credentials+'&&&'+fileName)
				print ret
				if command[1] == 'get':
					verNum = raw_input('\nVersion number: ')
					if verNum != '#quit':
						if int(verNum) != 0 and int(verNum)-1 in range(len(ret.split('\n'))-3):
							fileName = command[2]
							print recvFile('recvver&&&'+credentials , fileName+'/'+str(int(verNum)-1)+'%%%'+fileName , userSets)
						else: print 'Error: Not an applicable number'
			elif len(command) == 4 and command[1] == 'get':
				fileName = command[2]
				verNum = str(int(command[3])-1)
				print recvFile('recvver&&&'+credentials , fileName+'/'+verNum+'%%%'+fileName , userSets)
			else: print '\nversions [command] (file on server) (version #)\nAvailable commands: get, view'

		##--Get an archive of all files stored on the server--##
		elif command[0] == 'archive':
			if len(command) != 2: print recvFile('archive&&&'+credentials+'&&&' , 'archive.zip' , userSets)
			else: print recvFile('archive&&&'+credentials+'&&&T' , 'archive.zip' , userSets)

		##--Change user settings--##
		elif command[0] == 'set':
			if len(command) == 1: print '\nset (var) (value)\nClear var value with #clear\nVariables that can be set:' + getKeyString(userSets , '\n\t') + '\ndir settings support:\n\t~ for home dir\n\t#cwd for curdir\n\t#up to move up one dir'
			elif command[1] in userSets:
				if len(command) == 2:
					setVal = userSets[command[1]]
					if setVal == '': setVal = 'No value set'
					print command[1] + ':  ' + str(setVal)
				else:
					if command[2] == '#clear': userSets[command[1]] = ''
					elif command[1] == 'senddir' or command[1] == 'destdir':
						if command[2][:1] == '~': command[2] = os.path.expanduser(command[2])
						elif command[2][:4] == '#cwd': command[2] = command[2].replace('#cwd' , os.getcwd() , 1)
						elif command[2][:3] == '#up':
							oldDir = userSets[command[1]]
							if platform.system() == 'Windows': command[2] = command[2].replace('#up' , oldDir[:oldDir[:len(oldDir)-1].rfind('\\')])
							else: command[2] = command[2].replace('#up' , oldDir[:oldDir[:len(oldDir)-1].rfind('/')])
						if (command[2][len(command[2])-1:] != '/') and (command[2] != ''):
							if platform.system() == 'Windows': command[2] += '\\'
							else: command[2] += '/'
						if not os.path.isdir(command[2]):
							print command[2] + ' is not a directory'
						else: userSets[command[1]] = command[2]
					elif command[1] == 'startalert':
						if command[2][:1].lower() == 't': userSets[command[1]] = True
						elif command[2][:1].lower() == 'f': userSets[command[1]] = False
						else: print 'On/Off values can only be set True/False'
			else: print command[1] + ' is not an available setting'

		##--viewfiles - Returns a list  of files stored on the server--##
		##--test - Checks for healthy connection and valid sessionID--##
		##--stats - Returns user's storage stats--##
		elif command[0] in ['viewfiles','test','stats']:
			print sendData(command[0]+'&&&'+credentials)
		
		##--View or clear user's alerts on the server--##
		elif command[0] == 'alerts':
			if len(command) == 1:
				print '\nalerts [command]\nAvailable commands: view , clear'
			elif command[1] == 'view': print sendData('viewalerts&&&'+credentials+'&&&True')
			elif command[1] == 'clear': print sendData('clearalerts&&&'+credentials)
		
		##--Log user out of program and shutdown--##
		elif command[0] == 'logout':
			userName , sessionID = '' , ''
			userSets = {'senddir':'','destdir':'','startalert':True}
			quitFlag = True

		##--Admin actions if password is correct:--##
		elif command[0] in ['adminshutdown','adminclear','adminshowusers','adminserverstats','adminsendalert']:
			password = getpass.getpass('Server Password: ') #Ask for password to send to server
			if password == '#quit': sys.exit()
			alert = ''
			if command[0] == 'adminsendalert':
				alert = '&&&' + raw_input('Alert to send to all users: ')
			resp = sendData(command[0]+'&&&'+credentials+'&&&'+saltHash(password , 'masteradmin')+alert)
			if type(resp) != type(None):
				print resp
				if command[0] == 'adminshutdown' and resp[:5] != 'Error': quitFlag = True
				elif command[0] == 'adminclear' and resp[:5] != 'Error':
					userName = ''
					quitFlag = True

		##--Quit--##
		elif command[0] == 'quit': quitFlag = True

		##--About--##
		elif command[0] == '#about': print aboutString

		##--Help--##
		elif command[0] == '#help':
			if len(command) == 1: print helpString
			elif len(command) == 2:
				if command[1] in helpStrings: print helpStrings[command[1]]
				else: print 'Not a command'
			else: print '#help (command)'

		##--Release Notes--##
		elif command[0] == '#notes': print noteString

		##--Exception--##
		else: print 'Not a recognised command'

		##--End Command Loop--##

	##--Save userName and sessionID--##
	saveStorage(userName , sessionID , userSets)

	print '\nGoodbye\n'
##--End main--##

main()
