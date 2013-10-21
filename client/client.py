#!/usr/bin/python

##--Michael duPont
##--Change "serverName" in clientCommands to IP of server host before running

##--Note that (...) is optional and [...] is required

from clientCommands import *
import pickle , sys , platform

##------------------------------------Global Strings------------------------------------##

##--General info--##
aboutString = """
File Locket
Created by Michael duPont (flyinactor91@gmail.com)
v2.0.1a [2013-10-21]
Python 2.7.5 - Unix
"""

##--List of commands--##
helpString = """
Available commands:
	send   -s	Send files to the server
	get    -g	Get files from the server
	view   -v	View stored files
	del    -d	Delete files on the server
	ver    -v	File version options
	arc    -a	Get all files on server
	set    -us	Change user settings
	stat   -st	Get info about about files
	notif  -n	Notification options
	test   -t	Test server connection
	login  -li	Login from terminal
	logout -lo	Logout and quit
	quit   -q	Quit without logging out

Admin Tools (requires server pw):
	showusers   A-su	Returns all saved usernames
	serverstat  A-ss	Returns server statistics
	sendnotif   A-sn	Send alert to users
	clear       A-cl	Clears all server lib data
	shutdown    A-sd	Shuts down server and saves data

(...) is optional and [...] is required
(...*) indicates multiple items can be entered"""

##--Release notes--##
noteString = """
1.0.0 [2013-03-28]
	Initial release

1.1.0 [2013-04-10]
	File versioning
	Source and destination directory control
	File transfer improvements
	Server improvements

1.1.1 [2013-04-23]
	User and server statistics
	Recieve file archive
	Client and Server improvements

1.2.0 [2013-07-17]
	Windows/NT support
	#up for directory control
	Signup verifies password
	More reliable file transfers
	Bug fixes
	Code reduction

1.3.0 [2013-08-07]
	Notification system
	Up/Download progress bar
	Check version on startup
	Checksum checks for all transfers
	Client and Server improvements
	Bug fixes
	
1.3.1 [2013-09-05]
	Send, get, del multiple files
	Admin send multi-user alert
	Bug fixes
	Code readability

2.0.0 [2013-09-27]
	Call from command line
	Completely reworked client architecture
	Command name changes and shortcuts

2.0.1 [2013-10-21]
	New setup file
	fl and fl-server added to linux PATH
	Consolidated data to ~/.filelocket
"""

##--More detailed help for each command--##
helpStrings = {'send':'\nsend/-s (local files*)\nSend one or more files to the server.',
			   '-s':'\nsend/-s (local files*)\nSend one or more files to the server.',
			   'get':'\nget/-g (files on server*)\nRecieve one or more files from the server\nCalling get without file name calls view and a prompt',
			   '-g':'\nget/-g (files on server*)\nRecieve one or more files from the server\nCalling get without file name calls view and a prompt',
			   'view':"\nview/-v\nDisplays all the user's files stored on the server",
			   '-v':"\nview/-v\nDisplays all the user's files stored on the server",
			   'del':'\ndel/-d (files on server*)\nPerminantly delete a file and its saved versions from the server\nCalling del without file name calls view and a prompt',
			   '-d':'\ndel/-d (files on server*)\nPerminantly delete a file and its saved versions from the server\nCalling del without file name calls view and a prompt',
			   'ver':'\nver/-v [command] (file on server) (file version #)\nAvailable commands:\n\tview - View all the versions of a file stored on the server\n\tget - Recieve a file version from the server',
			   '-vr':'\nver/-v [command] (file on server) (file version #)\nAvailable commands:\n\tview - View all the versions of a file stored on the server\n\tget - Recieve a file version from the server',
			   'arc':"\narc/-a (true)\nRecieve a .zip archive of files stored on the server\nAlso includes the file versions if call followed by 'true'",
			   '-a':"\narc/-a (true)\nRecieve a .zip archive of files stored on the server\nAlso includes the file versions if call followed by 'true'",
			   'set':"\nset/-us (var) (value)\nUser can change user settings\nCalling set with only a var displays that var's value\nCall set by itself for a list of available vars",
			   '-us':"\nset/-us (var) (value)\nUser can change user settings\nCalling set with only a var displays that var's value\nCall set by itself for a list of available vars",
			   'not':"\nnot/-n [command]\nAvailable commands:\n\tview - View user's current notifications\n\tclear - Clear user's notifications from the server",
			   '-n':"\nnot/-n [command]\nAvailable commands:\n\tview - View user's current notifications\n\tclear - Clear user's notifications from the server",
			   'stat':'\nstat/-st\nServer displays information like the number of files a user has uploaded',
			   '-st':'\nstat/-st\nServer displays information like the number of files a user has uploaded',
			   'test':"\ntest/-t\nContacts the server to check the connection as well as the user's credentials",
			   '-t':"\ntest/-t\nContacts the server to check the connection as well as the user's credentials",
			   'login':'\nlogin/-li\nLogin or signup from the terminal without launching the prompt',
			   '-li':'\nlogin/-li\nLogin or signup from the terminal without launching the prompt',
			   'logout':'\nlogout/-lo\nSigns out user and exits the program\nNote: Server is not contacted',
			   '-lo':'\nlogout/-lo\nSigns out user and exits the program\nNote: Server is not contacted',
			   'quit':'\nquit/-q\nExits the program without logging out',
			   '-q':'\nquit/-q\nExits the program without logging out',
			   'showusers':'\nshowusers/A-su\nDisplays a list of all users signed up on this server\nRequires server password',
			   'A-su':'\nshowusers/A-su\nDisplays a list of all users signed up on this server\nRequires server password',
			   'serverstats':'\nserverstat/A-ss\nDisplays general information about the server like number of users and approximate server size\nRequires server password',
			   'A-ss':'\nserverstat/A-ss\nDisplays general information about the server like number of users and approximate server size\nRequires server password',
			   'sendnotif':'\nsendnotif/A-sn (target user*) ("notification")\nSend a single-user, multi-user, or system-wide alert\nSetting "all" as the targeted user sends alert to all users\nNotification must be surrounded by "quotes"\nRequires server password',
			   'A-sn':'\nsendnotif/A-sn (target user*) ("notification")\nSend a single-user, multi-user, or system-wide alert\nSetting "all" as the targeted user sends alert to all users\nNotification must be surrounded by "quotes"\nRequires server password',
			   'clear':"\nclear/A-cl\nResets the server's data storage and saves a backup of the previous files and data\nThis function cannot be called again while the previous backup exists\nRequires server password",
			   'A-cl':"\nclear/A-cl\nResets the server's data storage and saves a backup of the previous files and data\nThis function cannot be called again while the previous backup exists\nRequires server password",
			   'shutdown':'\nshutdown/A-sd\nRemotely shutdown the server\nRequires server password',
			   'A-sd':'\nshutdown/A-sd\nRemotely shutdown the server\nRequires server password'}

##--The non-alpha version number of the client to compare with that of the server. Ex. 1.3.0--##
clientVersion = '2.0.1'



##------------------------------------Startup actions------------------------------------##

##--Check bin and make if unavailable--##
if not os.path.isdir(os.path.expanduser('~/.filelocket')): os.mkdir(os.path.expanduser('~/.filelocket'))

##--Create client data by trying to load the .pkl storage file.--##
##--If no file is found (aka first run), declare default values--##
try:
	storageFile = open(os.path.expanduser('~/.filelocket/ClientStorage.pkl'), 'rb')
	userName = pickle.load(storageFile)
	sessionID = pickle.load(storageFile)
	userSets = pickle.load(storageFile)
	storageFile.close()
except:
	userName , sessionID = '' , ''
	userSets = {'senddir':'','destdir':'','startalert':True}
quitFlag = False



##------------------------------------Parser and Functions------------------------------------##
##--Parse input and call corresponding function--##
def parser(varsIn):
	global userName , sessionID , userSets , quitFlag
	command = varsIn[0]
	if command == 'send' or command == '-s': sendFunc(varsIn)
	elif command == 'get' or command == '-g': getFunc(varsIn)
	elif command == 'view' or command == '-v': print sendData('view&&&'+userName+'&&&'+sessionID)
	elif command == 'del' or command == '-d': delFunc(varsIn)
	elif command == 'ver' or command == '-vr': verFunc(varsIn)
	elif command == 'arc' or command == '-ar': arcFunc(varsIn)
	elif command == 'set' or command == '-us': setFunc(varsIn)
	elif command == 'not' or command == '-n': notifFunc(varsIn)
	elif command == 'test' or command == '-t': print sendData('test&&&'+userName+'&&&'+sessionID)
	elif command == 'stat' or command == '-st': print sendData('stat&&&'+userName+'&&&'+sessionID)
	elif command == 'showusers' or command == 'A-su':
		password = saltHash(getpass.getpass('Server Password: ') , 'masteradmin')
		print sendData('showusers&&&'+userName+'&&&'+sessionID+'&&&'+password)
	elif command == 'serverstat' or command == 'A-ss':
		password = saltHash(getpass.getpass('Server Password: ') , 'masteradmin')
		print sendData('serverstat&&&'+userName+'&&&'+sessionID+'&&&'+password)
	elif command == 'sendnotif' or command == 'A-sn': sendNotifFunc(varsIn)
	elif command == 'clear' or command == 'A-cl':
		password = saltHash(getpass.getpass('Server Password: ') , 'masteradmin')
		resp = sendData('clear&&&'+userName+'&&&'+sessionID+'&&&'+password)
		print resp
		if resp[:5] != 'Error': username , quitFlag = '' , True	#If succesful server wipe
	elif command == 'shutdown' or command == 'A-sd':
		password = saltHash(getpass.getpass('Server Password: ') , 'masteradmin')
		resp = sendData('shutdown&&&'+userName+'&&&'+sessionID+'&&&'+password)
		print resp
		if resp[:5] != 'Error': quitFlag = True	#If succesful server shutdown
	elif command == 'about' or command == '-ab': print aboutString
	elif command == 'notes' or command == '-no': print noteString
	elif command == 'help' or command == '-h': helpFunc(varsIn)
	elif command == 'login' or command == '-li': print 'You are already logged in'
	elif command == 'logout' or command == '-lo':
		userName , sessionID = '' , ''
		userSets = {'senddir':'','destdir':'','startalert':True}
		quitFlag = True
	elif command == 'quit' or command == '-q':
		quitFlag = True
	else: print 'Not a recognised command'

##--Send one or more files to the server--##
def sendFunc(varsIn):
	if len(varsIn) == 1:
		fileName = raw_input('File name: ')
		print sendFile('send&&&'+userName+'&&&'+sessionID , fileName , userSets)
	else:
		for i in range(1,len(varsIn)): print sendFile('send&&&'+userName+'&&&'+sessionID , varsIn[i] , userSets)

##--Recieve one or more files from the server--##
def getFunc(varsIn):
	if len(varsIn) == 1:
		ret = sendData('view&&&'+userName+'&&&'+sessionID) #Server sends list of files (if any)
		print ret
		if ret != 'You have not uploaded any files':
			fileName = raw_input('\nFile: ')
			if fileName in ret.split('\n'): print recvFile('get&&&'+userName+'&&&'+sessionID , fileName , userSets)
			else: print 'Error: Not an available file'
	elif len(command) >= 2:
		for i in range(1,len(command)): print recvFile('get&&&'+userName+'&&&'+sessionID , varsIn[i] , userSets)

##--Delete one or more files on the server--##
def delFunc(varsIn):
	if len(varsIn) == 1: print viewFileAndSend(userName+'&&&'+sessionID , 'del' , userSets)
	else:
		for i in range(1,len(varsIn)): print sendData('del&&&'+userName+'&&&'+sessionID+'&&&'+varsIn[i])

##--View file versions (and) get a versioned file from the server--##
def verFunc(varsIn):
	if len(varsIn) == 2:
		ret = viewFileAndSend(userName+'&&&'+sessionID , 'viewver' , userSets)
		if type(ret) != tuple: print ret
		else:
			print ret[0]
			if varsIn[1] == 'get':
				verNum = raw_input('\nVersion number: ')
				if int(verNum) != 0 and int(verNum)-1 in range(len(ret[0].split('\n'))-3):
					fileName = ret[1]
					print recvFile('recvver&&&'+userName+'&&&'+sessionID , fileName+'/'+verNum+'%%%'+fileName , userSets)
				else: print 'Error: Not an applicable number'
	elif len(varsIn) == 3:
		fileName = varsIn[2]
		ret = sendData('viewver&&&'+userName+'&&&'+sessionID+'&&&'+fileName)
		print ret
		if varsIn[1] == 'get':
			verNum = raw_input('\nVersion number: ')
			if int(verNum) != 0 and int(verNum)-1 in range(len(ret.split('\n'))-3):
				print recvFile('recvver&&&'+userName+'&&&'+sessionID , fileName+'/'+verNum+'%%%'+fileName , userSets)
			else: print 'Error: Not an applicable number'
	elif len(varsIn) == 4 and varsIn[1] == 'get':
		fileName = command[2]
		verNum = command[3]
		print recvFile('recvver&&&'+userName+'&&&'+sessionID , fileName+'/'+verNum+'%%%'+fileName , userSets)
	else: print '\nver [command] (file on server) (version #)\nAvailable commands: get, view'

##--Get an archive of all files stored on the server--##
def arcFunc(varsIn):
	if len(varsIn) != 2: print recvFile('arc&&&'+userName+'&&&'+sessionID+'&&&' , 'archive.zip' , userSets)
	else: print recvFile('arc&&&'+userName+'&&&'+sessionID+'&&&T' , 'archive.zip' , userSets)

##--Change user settings--##
def setFunc(varsIn):
	global userSets
	
	##--If no setting name given, print Usage and all setting names--##
	if len(varsIn) == 1: print '\nset (var) (value)\nClear var value with #clear\nVariables that can be set:' + getKeyString(userSets , '\n\t') + '\ndir settings support:\n\t~ for home dir\n\t#cwd for curdir\n\t#up to move up one dir'
	
	##--If a valid setting name--##
	elif varsIn[1] in userSets:
		
		##--If only setting name given, print its value--##
		if len(varsIn) == 2:
			setVal = userSets[varsIn[1]]
			if setVal == '': setVal = 'No value set'
			print varsIn[1] + ':  ' + str(setVal)
		
		##--Else, change the value of given setting--##
		else:
			
			##--Clear value of given setting--##
			if varsIn[2] == '#clear': userSets[varsIn[1]] = ''
			
			##--Directory controls for senddir and destdir--##
			elif varsIn[1] == 'senddir' or varsIn[1] == 'destdir':
				##--Replace ~ with home directory. Ex ~/Documents --> /home/user/Documents
				if varsIn[2][:1] == '~': varsIn[2] = os.path.expanduser(varsIn[2])
				##--Replace #cwd with current working directory
				elif varsIn[2][:4] == '#cwd': varsIn[2] = varsIn[2].replace('#cwd' , os.getcwd() , 1)
				##--Replace last folder with what follows. Ex /A/B/C --> #up/D --> /A/B/D
				elif varsIn[2][:3] == '#up':
					oldDir = userSets[varsIn[1]]
					if platform.system() == 'Windows': varsIn[2] = varsIn[2].replace('#up' , oldDir[:oldDir[:len(oldDir)-1].rfind('\\')])
					else: varsIn[2] = varsIn[2].replace('#up' , oldDir[:oldDir[:len(oldDir)-1].rfind('/')])
				##--Make sure directory location ends with / or \\
				if (varsIn[2][len(varsIn[2])-1:] != '/') and (varsIn[2] != ''):
					if platform.system() == 'Windows': varsIn[2] += '\\'
					else: varsIn[2] += '/'
				##--Check if path is a valid directory. If it is, set new value. If not, print error
				if not os.path.isdir(varsIn[2]):
					print varsIn[2] + ' is not a directory'
				else: userSets[varsIn[1]] = varsIn[2]
			
			##--Set startalert value to boolean True of False--##
			elif varsIn[1] == 'startalert':
				if varsIn[2][:1].lower() == 't': userSets[varsIn[1]] = True
				elif varsIn[2][:1].lower() == 'f': userSets[varsIn[1]] = False
				else: print 'On/Off values can only be set True/False'
	
	##--Catch invalid setting name--##
	else: print varsIn[1] + ' is not an available setting'

##--View or clear user's alerts on the server--##
def notifFunc(varsIn):
	if len(varsIn) == 1:
		print '\nnot [command]\nAvailable commands: view , clear'
	elif varsIn[1] == 'view': print sendData('viewnot&&&'+userName+'&&&'+sessionID+'&&&True')	#True tells server to send the actual messages
	elif varsIn[1] == 'clear': print sendData('clearnot&&&'+userName+'&&&'+sessionID)

##--Adminsenalert requires usernames and message to send--##
def sendNotifFunc(varsIn):
	password = saltHash(getpass.getpass('Server Password: ') , 'masteradmin') #Ask for password to send to server
	##--If more than one target user--##
	if len(varsIn) > 2:		
		for i in range(1 , len(varsIn)-1): print sendData('sendnotif&&&'+userName+'&&&'+sessionID+'&&&'+password+'&&&'+varsIn[i]+'&&&'+varsIn[len(varsIn)-1])
	##--If only one target user--##
	else:
		if len(varsIn) == 1:
			user = raw_input('Target user: ')
			notif = raw_input('Notification to send: ')
		elif len(varsIn) == 2:
			user = command[1]
			notif = raw_input('Notification to send: ')
		print sendData('sendnotif&&&'+userName+'&&&'+sessionID+'&&&'+password+'&&&'+user+'&&&'+notif)

def helpFunc(varsIn):
	print varsIn
	if len(varsIn) == 1: print helpString
	elif len(varsIn) == 2:
		if varsIn[1] in helpStrings: print helpStrings[varsIn[1]]
		else: print 'Not a command'
	else: print 'help (command)'



##------------------------------------Run Environments------------------------------------##
##--Launches the client prompt--##
def promptMain():
	global userName , sessionID , userSets
	
	##--If first run or last user logged out, run signup/login--##
	if userName == '':
		while userName == '':
			lin = raw_input('Login or Sign up? (L/S) : ').lower()
			if lin == 'l': userName , sessionID = startUp('login')
			elif lin == 's': userName , sessionID = startUp('signup')
			else: print 'Not an option\n'
		##--Save userName and sessionID--##
		saveStorage(userName , sessionID , userSets)
	##--Else print welcome back message so user can double check that they are the one logged in--##
	else: print 'Welcome back' , userName
	
	##--If user setting startalert is true, contact server for current number of notifications and display if not zero--##
	if userSets['startalert']:
		notifNum = sendData('notifNum&&&'+userName)
		if notifNum.isdigit():
			if int(notifNum) == 1: print 'You have 1 notification'
			elif int(notifNum) > 1: print 'You have '+notifNum+' notifications'
			#Ignore if alertNum == 0
		else: print 'Notification ' + notifNum
	print 'Program Info:  about/-ab , help/-h (command) , notes/-no'
	
	##--Command Loop--##
	while not quitFlag:
		commandList = stringToList(raw_input('\ncmd: '))
		parser(commandList)
	print '\nGoodbye\n'

##--Processes single commands from terminal--##
def termMain():
	global userName , sessionID
	##--If no current user, login/signup or quit--##
	if userName == '':
		if sys.argv[1] == 'login' or sys.argv[1] == '-li':
			while userName == '':
				lin = raw_input('Login or Sign up? (L/S) : ').lower()
				if lin == 'l': userName , sessionID = startUp('login')
				elif lin == 's': userName , sessionID = startUp('signup')
				else: print 'Not an option\n'
			##--Save userName and sessionID--##
			saveStorage(userName , sessionID , userSets)
			print 'Logged in'
		else: sys.exit('\nNo user is logged in. Call with -li to login or signup.\nYou can also launch the File-Locket prompt.\n')
	else:
		newList = sys.argv
		newList.pop(0)		#Remove file call (./client.py) from command list
		parser(newList)
	print



##------------------------------------Program Main------------------------------------##
def main():
	##--Startup Actions--##
	
	##--Print help without contacting server if terminal--##
	if len(sys.argv) > 1:
		if sys.argv[1] == 'help' or sys.argv[1] == '-h':
			sys.argv.pop(0)
			helpFunc(sys.argv)
			sys.exit()
	
	##--Check if server is online and determines if client-server is compatable--##
	serverData = sendData('versionTest')
	if userSets['startalert']:
		serverVersion = serverData[:serverData.find(' ')]
		if serverVersion[:5] == 'Error': sys.exit('Error: Server is offline') #Program exits if server connection cannot be established
		compare = compareVersions(clientVersion.split('.') , serverVersion.split('.'))
		if compare == -1: print '\n\nClient ('+clientVersion+') is out of date and might not work with the server ('+serverData+')\nGo to https://github.com/flyinactor91/File-Locket to get the latest version\n\n'
		if compare == 1: print '\n\nClient ('+clientVersion+') is running a newer version and might not work with the server ('+serverData+')\nContact your administrator to have them update the server software\n\n'
		#Can change to 'if serverVersion not in [list of acceptable versions]'	
	
	##--Determine run environment--##
	if len(sys.argv) == 1:
		promptMain()
	else: termMain()
	
	##--Shutdown actions--##

	##--Save userName and sessionID--##
	saveStorage(userName , sessionID , userSets)



##--Run Main--##
main()
