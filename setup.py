##--Michael duPont
##--v2.0.1 [2013-10-21]

#	See install notes for directions
#   This script must be run with root permissions
#   sudo python setup.py (   /-client/-server) (-link)

import sys , os , time

##--Bash install name--##
##--Ex: fl , filel , flocket, f-l , etc--##
bashClientName = 'fl'
bashServerName = 'fl-server'

def makeClientLink(curdir = False):
	if os.path.lexists('/usr/bin/'+bashClientName): os.system('rm /usr/bin/'+bashClientName)
	if curdir: os.symlink(os.getcwd()+'/client/client.py', '/usr/bin/'+bashClientName)
	else: os.system('ln -s /usr/local/bin/filelocket/client/client.py /usr/bin/'+bashClientName)

def makeServerLink(curDir = False):
	if os.path.lexists('/usr/bin/'+bashServerName): os.system('rm /usr/bin/'+bashServerName)
	if curDir: os.symlink(os.getcwd()+'/server/server.py', '/usr/bin/'+bashServerName)
	else: os.system('ln -s /usr/local/bin/filelocket/server/server.py /usr/bin/'+bashServerName)

def makeClient():
	if not os.path.isdir('/usr/local/bin/filelocket'): os.system('mkdir /usr/local/bin/filelocket')
	if not os.path.isdir('/usr/local/bin/filelocket/client'): os.system('mkdir /usr/local/bin/filelocket/client')
	os.system('cp client/client.py /usr/local/bin/filelocket/client')
	os.system('cp client/clientCommands.py /usr/local/bin/filelocket/client')
	os.system('chmod a+x /usr/local/bin/filelocket/client/client.py')
	makeClientLink()

def makeServer():
	if not os.path.isdir('/usr/local/bin/filelocket'): os.system('mkdir /usr/local/bin/filelocket')
	if not os.path.isdir('/usr/local/bin/filelocket/server'): os.system('mkdir /usr/local/bin/filelocket/server')
	os.system('cp server/server.py /usr/local/bin/filelocket/server')
	os.system('cp server/serverCommands.py /usr/local/bin/filelocket/server')
	os.system('chmod a+x /usr/local/bin/filelocket/server/server.py')
	makeServerLink()

def main():
		if len(sys.argv) == 1:
			makeClient()
			makeServer()
		elif len(sys.argv) == 2:
			if sys.argv[1] == '-client': makeClient()
			elif sys.argv[1] == '-server': makeServer()
			elif sys.argv[1] == '-link':
				makeClientLink(True)
				makeServerLink(True)
			else: print 'Usage: sudo python setup.py (  /-client/-server) (-link)'
		elif len(sys.argv) == 3:
			if sys.argv[1] == '-client' and sys.argv[2] == '-link': makeClientLink(True)
			elif sys.argv[1] == '-server' and sys.argv[2] == '-link': makeServerLink(True)
			else: print 'Usage: sudo python setup.py (  /-client/-server]) (-link)'
		else: print 'Usage: sudo python setup.py (  /-client/-server) (-link)'

main()
