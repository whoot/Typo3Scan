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

from colorama import Fore

class Output:
	"""
	This class handles the output
	"""
	def __init__(self):
		pass

	def typo3_installation(domain):
		print('')
		if domain.get_login_found():
			if domain.get_name().endswith('/'):
				print('[+] Typo3 backend login:'.ljust(30) + Fore.GREEN + domain.get_name() + 'typo3/index.php' + Fore.RESET)
			else:
				print('[+] Typo3 backend login:'.ljust(30) + Fore.GREEN + domain.get_name() + '/typo3/index.php' + Fore.RESET)
		else:
			print('[+] Typo3 backend login:'.ljust(30) + Fore.RED + 'not found' + Fore.RESET)
		print('[+] Typo3 version:'.ljust(30) + Fore.GREEN + domain.get_typo3_version() + Fore.RESET)
		if (domain.get_typo3_version() != 'could not be determined'):
			print(' | known vulnerabilities:'.ljust(30) + Fore.GREEN + 'http://www.cvedetails.com/version-search.php?vendor=&product=Typo3&version=' + domain.get_typo3_version() + Fore.RESET)
		print('')

	def interesting_headers(name, value):
		string = '[!] ' + name + ':'
		print(string.ljust(30) + value)

	def extension_output(path, extens):
		if not extens:
			print(Fore.RED + ' | No extension found' + Fore.RESET)
		else:
			for extension in extens:
				print(Fore.BLUE + '\n[+] Name: ' + extension.split('/')[3] + '\n' + "-"* 31  + Fore.RESET)
				print(' | Location:'.ljust(16) + path + extension)
				if not (extens[extension] == False):
					print(' | ' + extens[extension].split('.')[0] + ':'.ljust(4) + (path + extension + '/'+ extens[extension]))