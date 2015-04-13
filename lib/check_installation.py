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

import re
import sys
from colorama import Fore
from lib.request import Request
from lib.output import Output

class Typo3_Installation:
	"""
	This class checks, if Typo3 is used on the domain.
	If Typo3 is used, a link to the login page is shown.

		name: 		URL of the domain
		extensions:	Extensions to check for
		typo3:		If Typo3 is installed
	"""
	@staticmethod
	def run(domain):
		login_found = Typo3_Installation.search_login(domain)
		if not login_found:
			Typo3_Installation.check(domain)

	# Searching for Typo3 references in HTML comments
	@staticmethod
	def check(domain):
		response = Request.get_request(domain.get_name(), '/')
		Request.interesting_headers(domain, response[1], response[2])
		try:
			regex = re.compile('[Tt][Yy][Pp][Oo]3 (\d{1,2}\.\d{1,2}\.[0-9][0-9]?)')
			searchVersion = regex.search(response[0])
			version = searchVersion.groups()
			domain.set_typo3()
			domain.set_typo3_version(version[0].split()[0])
			return True
		except:
			try:
				regex = re.compile('TYPO3 (\d{1,2}\.\d{1,2}) CMS')
				searchHTML = regex.search(response[0])
				version = searchHTML.groups()
				domain.set_typo3()
				domain.set_typo3_version(version[0].split()[0])
				return True
			except:
				return False

	# Searching Typo3 login page
	@staticmethod
	def search_login(domain):
		try:
			response = Request.get_request(domain.get_name(), '/typo3/index.php')
			Request.interesting_headers(domain, response[1], response[2])
			regex = re.compile('<title>(.*)</title>', re.IGNORECASE)
			searchTitle = regex.search(response[0])
			title = searchTitle.groups()[0]
			if 'TYPO3' in title or 'TYPO3 SVN ID:' in response[0]:
				domain.set_typo3()
				domain.set_login_found()
				return True
		except:
			pass
		return False