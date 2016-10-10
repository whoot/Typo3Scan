#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Typo3 Enumerator - Automatic Typo3 Enumeration Tool
# Copyright (c) 2016 Jan Rude
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

__version__ = '0.4.5'
__program__ = 'Typo-Enumerator'
__description__ = 'Automatic Typo3 enumeration tool'
__author__ = 'https://github.com/whoot'

import sys
import os.path
import datetime
import argparse
import json
from colorama import Fore, init, deinit, Style
from lib.check_installation import Typo3_Installation
from lib.version_information import VersionInformation
from lib.extensions import Extensions
from lib.domain import Domain
from lib.update import Update
from lib.output import Output
init()

class Typo3:
	def __init__(self):
		self.__domain_list = []
		self.__extensions = None

	def print_help():
		print(
"""\nUsage: python3 typoenum.py [options]

Options:
  -h, --help 		Show this help message and exit

  Target:
   At least one of these options has to be provided to define the target(s)

    -d [DOMAIN, ...], --domain [DOMAIN, ...] Target domain(s)
    -f FILE, --file FILE 		     Parse targets from file (one domain per line)


  Optional:
   You dont need to specify this arguments, but you may want to

    --top TOP 		Test if top [TOP] downloaded extensions are installed
			  Default: every in list
    --state STATE 	Extension state [all, experimental, alpha, beta, stable, outdated]
			  Default: all
    --timeout TIMEOUT 	The timeout for all requests
			  Default: 10 seconds
    --agent USER_AGENT 	The user-agent used for all requests
			  Default: Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0
    --threads THREADS 	The number of threads used for enumerating the extensions
			  Default: 5


  Anonymity:
   This options can be used to proxy all requests through TOR/Privoxy

    --tor 	    	Using only TOR for connections
    --port PORT     	Port for TOR 
    			  Default: 9050

  General:
    -u, --update        Update TYPO3 extensions
""")

	def run(self):
		parser = argparse.ArgumentParser(add_help=False)
		group = parser.add_mutually_exclusive_group()
		anonGroup = parser.add_mutually_exclusive_group()
		help = parser.add_mutually_exclusive_group()
		group.add_argument('-f', '--file', dest='file')
		group.add_argument('-d', '--domain', dest='domain', type=str, nargs='+')
		group.add_argument('-u', '--update', dest='update', action='store_true')
		parser.add_argument('--top', type=int, dest='top', metavar='VALUE')
		parser.add_argument('--state', dest='ext_state', choices = ['all', 'experimental', 'alpha', 'beta', 'stable', 'outdated'], nargs='+', default = ['all'])
		anonGroup.add_argument('--tor', action='store_true')
		parser.add_argument('-p', '--port', dest='port', type=int)
		parser.add_argument('--threads', dest='threads', type=int, default = 5)
		parser.add_argument('--agent', dest='agent', type=str, default = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0')
		parser.add_argument('--timeout', dest='timeout', type=int, default = 10)
		help.add_argument( '-h', '--help', action='store_true')
		args = parser.parse_args()

		if args.help:
			Typo3.print_help()
			return True

		try:
			if args.update:
				Update()
				return True

			if args.tor:
				from lib.tor import Tor
				if args.port:
					tor = Tor(args.port)
				else:
					tor = Tor()
				tor.start_daemon()
				tor.connect()

			if args.domain:
				for dom in args.domain:
					self.__domain_list.append(Domain(dom, args.ext_state, args.top))
			elif args.file:
				if not os.path.isfile(args.file):
					print(Fore.RED + '\n[x] File not found: ' + args.file + '\n |  Aborting...' + Fore.RESET)
					sys.exit(-1)
				else:
					with open(args.file, 'r') as f:
						for line in f:
							self.__domain_list.append(Domain(line.strip('\n'), args.ext_state, args.top))

			config = {'threads':args.threads, 'agent':args.agent, 'timeout':args.timeout}
			json.dump(config, open('lib/config.json', 'w'))

			for domain in self.__domain_list:
				print('\n\n' + Fore.CYAN + Style.BRIGHT + '[ Checking ' + domain.get_name() + ' ]' + '\n' + '-'* 73  + Fore.RESET + Style.RESET_ALL)
				Typo3_Installation.run(domain)
				for key, value in domain.get_interesting_headers().items():
					Output.interesting_headers(key, value)
				if not domain.get_typo3():
					print(Fore.RED + '\n[x] It seems that Typo3 is not used on this domain' + Fore.RESET)
				else:
					if len(domain.get_typo3_version()) <= 3:
						version = VersionInformation()
						version.search_typo3_version(domain)
					login = Typo3_Installation.search_login(domain)
					Output.typo3_installation(domain)
					if not login:
						print(Fore.YELLOW + '[!] Backend login not found')
						print(' | Extension search would fail')
						print(' | Skipping...')
						print(Fore.RESET)
					else:
						# Loading extensions
						if (self.__extensions is None):
							ext = Extensions(args.ext_state, args.top)
							self.__extensions = ext.load_extensions()
						# copy them in domain object
						if (domain.get_extensions() is None):
							domain.set_extensions(self.__extensions)
						# search
						print ('\n[ Searching', len(self.__extensions), 'extensions ]')
						ext.search_extension(domain, self.__extensions)
						ext.search_ext_version(domain, domain.get_installed_extensions())
						Output.extension_output(domain.get_path(), domain.get_installed_extensions())
		
		except KeyboardInterrupt:
			print('\nReceived keyboard interrupt.\nQuitting...')
			exit(-1)
		finally:
			deinit()
			now = datetime.datetime.now()
			print('\n\n' + __program__ + ' finished at ' + now.strftime('%Y-%m-%d %H:%M:%S') + '\n')
		
if __name__ == '__main__':
	print('\n' + 73*'=' + Style.BRIGHT)
	print(Fore.BLUE)
	print(' _______                     ______ '.center(73))
	print('|_     _|.--.--.-----.-----.|__    |'.center(73))
	print('  |   |  |  |  |  _  |  _  ||__    |'.center(73))
	print('  |___|  |___  |   __|_____||______|'.center(73))
	print('         |_____|__|                 '.center(73))
	print(' _______                                         __              '.center(73))
	print('|    ___|.-----.--.--.--------.-----.----.---.-.|  |_.-----.----.'.center(73)) 
	print('|    ___||     |  |  |        |  -__|   _|  _  ||   _|  _  |   _|'.center(73))
	print('|_______||__|__|_____|__|__|__|_____|__| |___._||____|_____|__|  '.center(73))
	print(Fore.RESET + Style.RESET_ALL)
	print(__description__.center(73))
	print(('Version ' + __version__).center(73))
	print((__author__).center(73))
	print(73*'=')
	main = Typo3()
	main.run()
