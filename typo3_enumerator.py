#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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

__version__ = "0.4"
__program__ = "Typo-Enumerator"
__description__ = 'Automatic Typo3 enumeration tool'
__author__ = "https://github.com/whoot"

import sys
import os.path
import datetime
import argparse
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

	def run(self):
		parser = argparse.ArgumentParser(usage='typoenum.py [options]', add_help=False)
		group = parser.add_mutually_exclusive_group()
		anonGroup = parser.add_mutually_exclusive_group()
		group.add_argument('-f', '--file', dest='file')
		group.add_argument('-d', '--domain', dest='domain', type=str, nargs='+')
		group.add_argument('-u', '--update', dest='update', action='store_true')
		parser.add_argument('--top', type=int, dest='top', metavar='VALUE')
		parser.add_argument('--state', dest='ext_state', choices = ['all', 'experimental', 'alpha', 'beta', 'stable', 'outdated'], nargs='+', default = ['all'])
		anonGroup.add_argument('--tor', help='using only TOR for connections', action='store_true')
		anonGroup.add_argument('--privoxy', help='using only Privoxy for connections', action='store_true')
		anonGroup.add_argument('--tp', help='using TOR and Privoxy for connections', action='store_true')
		parser.add_argument('-p', '--port', dest='port', help='Port for TOR/Privoxy (default: 9050/8118)', type=int)

		parser.add_argument( "-h", "--help", action="help")
		args = parser.parse_args()

		try:
			if args.update:
				Update()
				return True

			if args.tor:
				from lib.tor_only import Tor
				if args.port:
					tor = Tor(args.port)
				else:
					tor = Tor()
				tor.start_daemon()
				tor.connect()

			elif args.privoxy:
				from lib.privoxy_only import Privoxy
				if args.port:
					privoxy = Privoxy(args.port)
				else:
					privoxy = Privoxy()
				privoxy.start_daemon()
				privoxy.connect()

			elif args.tp:
				from lib.tor_with_privoxy import Tor_with_Privoxy
				if args.port:
					tp = Tor_with_Privoxy(args.port)
				else:
					tp = Tor_with_Privoxy()
				tp.start_daemon()
				tp.connect()

			if args.domain:
				for dom in args.domain:
					self.__domain_list.append(Domain(dom, args.ext_state, args.top))
			elif args.file:
				if not os.path.isfile(args.file):
					print(Fore.RED + "\n[x] File not found: " + args.file + "\n |  Aborting..." + Fore.RESET)
					sys.exit(-2)
				else:
					with open(args.file, 'r') as f:
						for line in f:
							domain_list.append(Domain(line.strip('\n'), args.ext_state, args.top))
			for domain in self.__domain_list:
				print('\n\n' + Fore.CYAN + Style.BRIGHT '[ Checking ' + domain.get_name() + ' ]' + '\n' + "-"* 73  + Fore.RESET + Style.RESET_ALL)
				Typo3_Installation.run(domain)
				if not domain.get_typo3():
					print(Fore.RED + '\n[x] Typo3 is not used on this domain' + Fore.RESET)
				else:
					if domain.get_login_found():
						# search version info
						version = VersionInformation()
						version.search_typo3_version(domain)
					Output.typo3_installation(domain)
					if not domain.get_login_found():
						print(Fore.YELLOW + '[!] Backend login not found\n | Extension enumeration would be failing\n | Skipping...' + Fore.RESET)
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
						Output.extension_output(domain.get_installed_extensions())
		
		except KeyboardInterrupt:
			print("\nReceived keyboard interrupt.\nQuitting...")
			exit(-1)
		finally:
			deinit()
			now = datetime.datetime.now()
			print('\n\n' + __program__ + ' finished at ' + now.strftime("%Y-%m-%d %H:%M:%S") + '\n')
		
if __name__ == "__main__":
	print('\n' + 73*'=' + Style.BRIGHT)
	print(Fore.BLUE + ' _______                     ______ '.center(73))
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