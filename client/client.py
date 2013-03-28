#!/usr/bin/python

##--Michael duPont
##--Change "serverName" to IP of server host before running

from clientCommands import *
from socket import *
import pickle

aboutString = """
File Locket
Created by Michael duPont (flyinactor91@gmail.com)
v1.0.0 [28 03 2013]
Python 2.7.3 - Unix

Simple file storage service.
Files stored on the server do not undergo further encryption.
Passwords are "deliciously salted" and hashed client side so your precious digits are secure.
~~Admin clear saves a backup of all files and storage dictionaries.

Upgrades for future releases:
	Choose dest directory upon getfile
	Up arrow yields previous entries
	File encryption (user-held keys)
	File versioning
	User account support/authentication
	Optional GUI (much later)
"""

helpString = """
Available commands:
	sendfile		Send a file to the server
	getfile			Get a file from the server
	showfiles		Show stored files
	delfile			Delete a file on the server
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
"""

##--Main Client Function--##
def main():
	serverName = "localhost" #"localhost" ######Change this to the IP address of whatever computer the server is running on
	serverPort = 60145
	command = ""
	quitFlag = False
	
	try:
		##--Load in (via pickle) IP dictionary--##
		storageFile = open('ClientStorage.pkl', 'rb')
		userName = pickle.load(storageFile)
		sessionID = pickle.load(storageFile)
		storageFile.close()
	except:
		userName = ""
		sessionID = ""

	##--Ask user for name and init--##
	if userName == "":
		while userName == "":
			userName , sucBool , sessionID = startUp(serverName , serverPort)
	else:
		print "\nWelcome back" , userName
		sucBool = True
	if sucBool:
		print "Program Info:  #about, #help, #notes"
	else:
		quitFlag = True
		userName = ""
		
	##--Command Loop--##
	while not quitFlag:
		command = raw_input("\ncmd: ").lower()   #Ask user for command input
		
		##--Send a file to the server--##
		if command == 'sendfile':
			sendFile(command + "&&&" + userName + "&&&" + sessionID , serverName , serverPort)
		
		##--Recieve a file from the server--##
		elif command == 'getfile':
			getFile(command + "&&&" + userName + "&&&" + sessionID , serverName , serverPort)
		
		##--Returns a list  of files stored on the server--##
		elif command == 'showfiles':
			showFiles(command + "&&&" + userName + "&&&" + sessionID , serverName , serverPort)
		
		##--Delete a file on the server--##
		elif command == 'delfile':
			delFile(command + "&&&" + userName + "&&&" + sessionID , serverName , serverPort)
		
		##--Checks for healthy connection and valid sessionID--##
		elif command == 'test':
			print sendData(command + "&&&" + userName + "&&&" + sessionID , serverName , serverPort)
		
		##--Log user out of program and shutdown--##
		elif command == 'logout':
			userName = ""
			quitFlag = True
		
		##--Admin actions if password is correct:--##
			##--AdminShutdown shuts down server--##		
			##--AdminClear clears server storage--##		
			##--AdminShowUsers shows all user names stored on the server--##		
		elif command == "adminshutdown" or command == "adminclear" or command == "adminshowusers":
			sucBool = admin(command , userName , sessionID , serverName , serverPort)
			if command == "adminshutdown" and sucBool:
				quitFlag = True
			elif command == "adminclear" and sucBool:
				userName = ""
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
			print "Not a recognised command"
		
		##--End Command Loop--##
		#clientSocket.close()
	
	##--Save userName and sessionID--##
	storageFile = open('ClientStorage.pkl', 'wb')
	pickle.dump(userName , storageFile)
	pickle.dump(sessionID , storageFile)
	storageFile.close()
	
	print "\nGoodbye\n"
##--End main--##

main()
