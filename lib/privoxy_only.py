import socket
import urllib2
import os, sys
import re

try:
	import socks
except:
	print "The module 'SocksiPy' is not installed."
	if sys.platform.startswith('linux'):
		"Please install it with: sudo apt-get install python-socksipy"
	else:
		"You can download it from http://socksipy.sourceforge.net/"
	sys.exit(-2)

def start_daemon():
	if sys.platform.startswith('linux'):
		os.system('service privoxy start')
		print '[ ok ] Starting privoxy daemon...done.'
	elif sys.platform.startswith('win32') or sys.platform.startswith('cygwin'):
		print "Please make sure Privoxy is running..."
	else:
		print "You are using", sys.platform, ", which is not supported (yet)."
		sys.exit(-2)
	
# Using Privoxy for all connections
def connect(port):
	print "\nChecking connection..."
	socks.setdefaultproxy(socks.PROXY_TYPE_HTTP, "127.0.0.1", port, True)
	socket.socket = socks.socksocket
	try:
		url = urllib2.Request('https://check.torproject.org/')
		torcheck = urllib2.urlopen(url)
		response = torcheck.read()
		torcheck.close()
	except:
		print "Failed to connect through Privoxy!"
		print "Please make sure your configuration is right!\n"
		sys.exit(-2)
	try:
		# TODO: Check on privoxy at http://ha.ckers.org/weird/privoxy.html
		regex = re.compile("(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})")
		searchIP = regex.search(response)
		IP = searchIP.groups()[0]
		print "Your IP is: ", IP
	except:
		print "It seems like Privoxy is not used.\nAborting...\n"
		sys.exit(-2)

def stop():
	print "\n"
	if sys.platform.startswith('linux'):
		os.system('service privoxy stop')
		print '[ ok ] Stopping privoxy daemon...done.'
	elif sys.platform.startswith('win32') or sys.platform.startswith('cygwin'):
		print "You can close Privoxy now..."