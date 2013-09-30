##--Michael duPont
##--v2.0.1a [2013-09-30]

#   This script must be run with root permissions
#   sudo python setup.py (   /-client/-server) (-link)

import sys , os , time

def makeClient():
	if not os.path.isdir('/usr/local/bin/filelocket'): os.system('mkdir /usr/local/bin/filelocket')
	if not os.path.isdir('/usr/local/bin/filelocket/client'): os.system('mkdir /usr/local/bin/filelocket/client')
	os.system('cp client/client.py /usr/local/bin/filelocket/client')
	os.system('cp client/clientCommands.py /usr/local/bin/filelocket/client')
	os.system('chmod a+x /usr/local/bin/filelocket/client/client.py')
	if os.path.lexists('/usr/bin/filelocket'): os.system('rm /usr/bin/filelocket')
	os.system('ln -s /usr/local/bin/filelocket/client/client.py /usr/bin/filelocket')

def makeServer():
	if not os.path.isdir('/usr/local/bin/filelocket'): os.system('mkdir /usr/local/bin/filelocket')
	if not os.path.isdir('/usr/local/bin/filelocket/server'): os.system('mkdir /usr/local/bin/filelocket/server')
	os.system('cp server/server.py /usr/local/bin/filelocket/server')
	os.system('cp server/serverCommands.py /usr/local/bin/filelocket/server')
	os.system('chmod a+x /usr/local/bin/filelocket/server/server.py')
	if os.path.lexists('/usr/bin/filelocket-server'): os.system('rm /usr/bin/filelocket-server')
	os.system('ln -s /usr/local/bin/filelocket/server/server.py /usr/bin/filelocket-server')

def main():
		if len(sys.argv) == 1:
			makeClient()
			makeServer()
		elif len(sys.argv) == 2:
			if sys.argv[1] == '-client': makeClient()
			elif sys.argv[1] == '-server': makeServer()
			elif sys.argv[1] == '-link':
				if os.path.lexists('/usr/bin/filelocket'): os.system('rm /usr/bin/filelocket')
				os.symlink(os.getcwd()+'/client/client.py', '/usr/bin/filelocket')
				if os.path.lexists('/usr/bin/filelocket-server'): os.system('rm /usr/bin/filelocket-server')
				os.symlink(os.getcwd()+'/server/server.py', '/usr/bin/filelocket-server')
			else: print 'Usage: sudo python setup.py (  /-client/-server) (-link)'
		elif len(sys.argv) == 3:
			if sys.argv[1] == '-client' and sys.argv[2] == '-link':
				if os.path.lexists('/usr/bin/filelocket'): os.system('rm /usr/bin/filelocket')
				os.symlink(os.getcwd()+'/client/client.py', '/usr/bin/filelocket')
			elif sys.argv[1] == '-server' and sys.argv[2] == '-link':
				if os.path.lexists('/usr/bin/filelocket-server'): os.system('rm /sr/bin/filelocket-server')
				os.symlink(os.getcwd()+'/server/server.py', '/usr/bin/filelocket-server')
			else: print 'Usage: sudo python setup.py (  /-client/-server]) (-link)'
		else: print 'Usage: sudo python setup.py (  /-client/-server) (-link)'

main()
