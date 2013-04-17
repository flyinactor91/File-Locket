#!/usr/bin/python

##--Michael duPont
##--Change "serverName" in clientCommands to IP of server host before running

from clientCommands import *
from socket import *
import pickle

aboutString = """
File Locket
Created by Michael duPont (flyinactor91@gmail.com)
v1.1.0a [17 04 2013]
Python 2.7.4 - Unix

Simple file storage service
Store, access, and delete files
Files are versioned and can be downloaded
"""

helpString = """
Available commands:
	sendfile	Send a file to the server
	getfile 	Get a file from the server
	viewfiles	View stored files
	delfile		Delete a file on the server
	versions	File version options
	archive		Get all files on server (versions if true)
	set		Change program settings
	userstats	Get info about about files
	test		Test server connection
	logout		Logout and quit
	quit		Quit without logging out
	
Admin Tools (requires admin pw):
	adminshowusers	Returns all saved usernames
	adminserverstats	Returns server statistics
	adminclear	Clears all server lib data
	adminshutdown	Shuts down server and saves data

Typing #quit into a prompt exits that prompt
"""

noteString = """
1.0.0 [28 03 2013]
	Initial release

1.1.0 [10 04 2013]
	File versioning
	Source and destination directory control
	File transfer improvements
	Server improvements

1.1.0a [17 04 2013]
	User and server statistics
	Recieve file archive
	Client and Server improvements
"""

helpStrings = {'sendfile':'\nsendfile [local file]\nSends a file to the server.','getfile':'\ngetfile (file on server)\nRecieve a file from the server\nCalling getfile without file name calls viewfiles and a prompt','viewfiles':"\nviewfiles\nDisplays all the user's files stored on the server",'delfile':'\ndelfile (file on server)\nPerminantly delete a file and its saved versions from the server\nCalling delfile without file name calls viewfiles and a prompt','versions':'\nversions [command] (file on server) (file version #)\nAvailable commands:\n\tview - View all the versions of a file stored on the server\n\tget - Recieve a file version from the server\nPrompts will be called until a file name and version number are given','archive':'\narchive (true)\nRecieve a .zip archive of files stored on the server\nAlso includes the file versions if call followed by true','set':"\nset (var) (value)\nUser can change program settings\nCalling set with only a var displays that var's value\nCall set by itself for a list of available vars",'userstats':'\nServer displays information like the number of files a user has uploaded','test':"\ntest\nContacts the server to check the connection as well as the user's credentials",'logout':'\nlogout\nSigns out user and exits the program\nNote: Server is not contacted','quit':'\nquit\nExits the program without logging out','adminshowusers':'\nadminshowusers\nDisplays a list of all users signed up on this server\nRequires server password','adminserverstats':'\nDisplays general information about the server like number of users and approximate server size\nRequires server password','adminclear':"\nadminclear\nResets the server's data storage and saves a backup of the previous files and data\nThis function cannot be called again while the previous backup exists\nRequires server password",'adminshutdown':'\nadminshutdown\nRemotely shutdown the server\nRequires server password'}


##--Main Client Function--##
def main():	
	try:
		##--Load in (via pickle) IP dictionary--##
		storageFile = open('ClientStorage.pkl', 'rb')
		userName = pickle.load(storageFile)
		sessionID = pickle.load(storageFile)
		userSets = pickle.load(storageFile)
		storageFile.close()
	except:
		userName = ''
		sessionID = ''
		userSets = {'senddir':'','destdir':''}
	
	command = ''
	quitFlag = False
	
	##--Ask user for name and init--##
	if userName == '':
		while userName == '':
				lin = ''
				while lin != 'L' and lin != 'S':
					lin = raw_input('\nLogin or Sign up? (L/S) : ').upper()
				if lin == 'L': userName , sucBool , sessionID = login()
				elif lin == 'S': userName , sucBool , sessionID = signUp()
		##--Save userName and sessionID--##
		saveStorage(userName , sessionID , userSets)
	else:
		print '\nWelcome back' , userName
		sucBool = True
	if sucBool:
		print 'Program Info:  #about , #help (command) , #notes'
	else:
		quitFlag = True
		userName = ''
		
	##--Command Loop--##
	while not quitFlag:
		command = raw_input('\ncmd: ').split(' ')   #Ask user for command input
		credentials = userName + '&&&' + sessionID
		
		##--Send a file to the server--##
		if command[0] == 'sendfile':
			if len(command) == 1:
				print 'sendfile [local file]'
			else:
				sendFile(command[0]+'&&&'+credentials , command[1] , userSets)
		
		##--Recieve a file from the server--##
		elif command[0] == 'getfile':
			if len(command) == 1:
				ret = sendData('viewfiles&&&'+credentials)
				#Server checks if sessionID matches and sends list of files (if any)
				print ret
				if ret != 'You have not uploaded any files':
					ret = ret.split('\n') #Create searchable list from file names
					fileName = raw_input('\nFile: ')
					if fileName != '#quit':
						if fileName in ret: recvFile('recvfile&&&'+credentials , fileName , userSets)
						else: print 'Error: Not an available file'
			elif len(command) == 2:
				recvFile('recvfile&&&'+credentials , command[1] , userSets)
			else:
				print 'getfile (file on server)'
		
		##--Delete a file on the server--##
		elif command[0] == 'delfile':
			if len(command) == 1:
				print filesView(credentials , command[0] , userSets)
			elif len(command) == 2:
				print sendData('delfile&&&'+credentials+'&&&'+command[1])
			else:
				print 'delfile (file on server)'
			
		##--View file versions (and) get a versioned file from the server--##
		elif command[0] == 'versions':
			if len(command) == 2:
				ret = filesView(credentials , command[0] , userSets)
				print ret[0]
				if command[1] == 'get':
					verNum = str(int(raw_input('\nVersion number: '))-1)
					if verNum != '#quit' and int(verNum) in range(len(ret[0].split('\n'))-1):
						fileName = ret[1]
						recvFile('recvver&&&'+credentials , fileName+'/'+verNum+'%%%'+fileName , userSets)
			elif len(command) == 3:
				fileName = command[2]
				ret = sendData(command[0]+'&&&'+credentials+'&&&'+fileName)
				print ret
				if command[1] == 'get':
					verNum = str(int(raw_input('\nVersion number: '))-1)
					if verNum != '#quit' and int(verNum) in range(len(ret[0].split('\n'))-1):
						fileName = command[2]
						recvFile('recvver&&&'+credentials , fileName+'/'+verNum+'%%%'+fileName , userSets)
			elif len(command) == 4 and command[1] == 'get':
				fileName = command[2]
				verNum = str(int(command[3])-1)
				recvFile('recvver&&&'+credentials , fileName+'/'+verNum+'%%%'+fileName , userSets)
			else: print '\nversions [command] (file on server) (file version #)\nAvailable commands: get, view'
		
		##--Get an archive of all files stored on the server--##
		elif command[0] == 'archive':
			if len(command) != 2: recvFile('archive&&&'+credentials+'&&&' , 'archive.zip' , userSets)
			else: recvFile('archive&&&'+credentials+'&&&T' , 'archive.zip' , userSets)
		
		##--Change user settings--##
		elif command[0] == 'set':
			userSets = settings(command , userSets)
		
		##--viewfiles - Returns a list  of files stored on the server--##
		##--test - Checks for healthy connection and valid sessionID--##
		##--userstats - Returns user's storage stats--##
		elif command[0] == 'viewfiles' or command[0] == 'test' or command[0] == 'userstats':
			print sendData(command[0]+'&&&'+credentials)
		
		##--Log user out of program and shutdown--##
		elif command[0] == 'logout':
			userName = ''
			quitFlag = True
		
		##--Admin actions if password is correct:--##
			##--AdminShutdown shuts down server--##		
			##--AdminClear clears server storage--##		
			##--AdminShowUsers shows all user names stored on the server--##		
		elif command[0] == 'adminshutdown' or command[0] == 'adminclear' or command[0] == 'adminshowusers' or command[0] == 'adminserverstats':
			password = getpass.getpass('Server Password: ')	#Ask for password to send to server
			resp = sendData(command[0]+'&&&'+credentials+'&&&'+saltHash(password , 'masteradmin'))
			if type(resp) != type(None):
				print resp
				if command[0] == 'adminshutdown' and resp[:5] != 'Error':
					quitFlag = True
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
