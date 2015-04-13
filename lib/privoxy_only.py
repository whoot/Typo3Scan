#-------------------------------------------------------------------------------
# Typo3 Enumerator - Automatic Typo3 Enumeration Tool
# Copyright (c) 2015 Jan Rude
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/](http://www.gnu.org/licenses/)
#-------------------------------------------------------------------------------

import socket
import os, sys
import re
from colorama import Fore
from lib.request import Request
try:
	import socks
except:
	print(Fore.RED + 'The module \'SocksiPy\' is not installed.')
	if sys.platform.startswith('linux'):
		print('Please install it with: sudo apt-get install python-socksipy' + Fore.RESET)
	else:
		print('You can download it from https://code.google.com/p/socksipy-branch/' + Fore.RESET)
	sys.exit(-2)

class Privoxy:
	def __init__(self, port=8118):
		self.__port = port
		Request.timeout = 20

	def start_daemon(self):
		if sys.platform.startswith('linux'):
			os.system('service privoxy start')
			print('[ ok ] Starting privoxy daemon...done.')
		elif sys.platform.startswith('win32') or sys.platform.startswith('cygwin'):
			print('Please make sure Privoxy is running...')
		else:
			print('You are using', sys.platform, ', which is not supported (yet).')
			sys.exit(-2)
		
	# Using Privoxy for all connections
	def connect(self):
		print('\nChecking connection...')
		socks.setdefaultproxy(socks.PROXY_TYPE_HTTP, '127.0.0.1', self.__port, True)
		socks.socket.setdefaulttimeout(20)
		socket.socket = socks.socksocket
		try:
			request = Request.get_request('https://check.torproject.org/')
			response = str(request[0])
		except:
			print('Failed to connect through Privoxy!')
			print('Please make sure your configuration is right!\n')
			sys.exit(-2)
		try:
			# TODO: Check on privoxy at http://ha.ckers.org/weird/privoxy.html
			regex = re.compile("(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})")
			searchIP = regex.search(response)
			IP = searchIP.groups()[0]
			print('Your IP is: ', IP)
		except:
			print('It seems like Privoxy is not used.\nAborting...\n')
			sys.exit(-2)

	def stop(self):
		print('\n')
		if sys.platform.startswith('linux'):
			os.system('service privoxy stop')
			print('[ ok ] Stopping privoxy daemon...done.')
		elif sys.platform.startswith('win32') or sys.platform.startswith('cygwin'):
			print('You can stop Privoxy now...')