#!/usr/bin/python

##--Michael duPont
##--Change "serverName" to IP of server host before running

from clientCommands import *
from socket import *
import pickle

aboutString = """
File Locket
Created by Michael duPont (flyinactor91@gmail.com)
v1.1.0 [10 04 2013]
Python 2.7.4 - Unix

Upgrades for future releases:
	Folder support
	Up arrow yields previous entries
	File encryption (user-held keys)
	User account support/authentication
	Optional GUI (much later)
"""

helpString = """
Available commands:
	sendfile		Send a file to the server
	getfile			Get a file from the server
	viewfiles		View stored files
	delfile			Delete a file on the server
	versions		File version options
	set			Change program settings
	test			Test server connection
	logout			Logout and quit
	quit			Quit without logging out
	
Admin Tools (requires admin pw):
	adminshowusers		Returns all saved usernames
	adminclear		Clears all server lib data
	adminshutdown		Shuts down server and saves data
"""

noteString = """
1.0.0 [28 03 2013]
	Initial release

1.1.0 [10 04 2013]
	File versioning
	Added source and destination directory control
	File transfer improvements
	Server improvements
"""

##--Main Client Function--##
def main():
	##--Server connection settings--##
	serverName = 'localhost'  	#Change to IP address server computer
	serverPort = 60145			#Should match that int set on server
	
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
			userName , sucBool , sessionID = startUp(serverName , serverPort)
		##--Save userName and sessionID--##
		storageFile = open('ClientStorage.pkl', 'wb')
		pickle.dump(userName , storageFile)
		pickle.dump(sessionID , storageFile)
		pickle.dump(userSets , storageFile)
		storageFile.close()
	else:
		print '\nWelcome back' , userName
		sucBool = True
	if sucBool:
		print 'Program Info:  #about , #help , #notes'
	else:
		quitFlag = True
		userName = ''
		
	##--Command Loop--##
	while not quitFlag:
		command = raw_input('\ncmd: ')   #Ask user for command input
		credentials = command.split(' ')[0] + '&&&' + userName + '&&&' + sessionID
		
		##--Send a file to the server--##
		if command == 'sendfile':
			sendFile(credentials , userSets , serverName , serverPort)
		
		##--Recieve a file from the server--##
		elif command == 'getfile':
			getFile(credentials , userSets , serverName , serverPort)
		
		##--Returns a list  of files stored on the server--##
		elif command == 'viewfiles':
			print sendData(credentials , serverName , serverPort)
		
		##--Delete a file on the server--##
		elif command == 'delfile':
			delFile(credentials , serverName , serverPort)
			
		##--Get or delete a versioned file on the server--##
		elif command.split(' ')[0] == 'versions':
			if len(command.split(' ')) != 2:
				print '\nversions [command]\nAvailable commands:\nget\nview'
			else:
				verCommand = command.split(' ')[1]
				if verCommand == 'get' or verCommand == 'view':
					versioning(credentials , verCommand , userSets , serverName , serverPort)
				else:
					print 'Not a recognised command'
		
		##--Change user settings--##
		elif command.split(' ')[0] == 'set':
			userSets = settings(command.split(' ') , userSets)
		
		##--Checks for healthy connection and valid sessionID--##
		elif command == 'test':
			print sendData(credentials , serverName , serverPort)
		
		##--Log user out of program and shutdown--##
		elif command == 'logout':
			userName = ''
			quitFlag = True
		
		##--Admin actions if password is correct:--##
			##--AdminShutdown shuts down server--##		
			##--AdminClear clears server storage--##		
			##--AdminShowUsers shows all user names stored on the server--##		
		elif command == 'adminshutdown' or command == 'adminclear' or command == 'adminshowusers':
			sucBool = admin(credentials , serverName , serverPort)
			if command == 'adminshutdown' and sucBool:
				quitFlag = True
			elif command == 'adminclear' and sucBool:
				userName = ''
				quitFlag = True
		
		##--Quit--##
		elif command == 'quit':
			quitFlag = True
		
		##--About--##
		elif command == '#about':
			print aboutString
		
		##--Help--##
		elif command == '#help':
			print helpString
		
		##--Release Notes--##
		elif command == '#notes':
			print noteString
		
		##--Exception--##
		else:
			print 'Not a recognised command'
		
		##--End Command Loop--##
	
	##--Save userName and sessionID--##
	storageFile = open('ClientStorage.pkl', 'wb')
	pickle.dump(userName , storageFile)
	pickle.dump(sessionID , storageFile)
	pickle.dump(userSets , storageFile)
	storageFile.close()
	
	print '\nGoodbye\n'
##--End main--##

main()
