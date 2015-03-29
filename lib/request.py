#!/usr/bin/env python
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

import requests
import re
from colorama import Fore
requests.packages.urllib3.disable_warnings()
from lib.output import Output

class Request:
	"""
	This class is used to make all server requests
	"""
	@staticmethod
	def get_request(domain_name, path):
		try:
			r = requests.get(domain_name + path, timeout=10, headers={'User-Agent' : "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)"}, verify=False)
			httpResponse = r.text
			headers = r.headers
			cookies = r.cookies
			status_code = r.status_code
			response = [httpResponse, headers, cookies, status_code]
			return response
		except requests.exceptions.Timeout:
			print(Fore.RED + '[x] Connection timed out' + Fore.RESET)
		except requests.exceptions.ConnectionError as e: 
			print(Fore.RED + '[x] Connection aborted.\n    Please make sure you provided the right URL' + Fore.RESET)
		except requests.exceptions.RequestException as e:
			print(Fore.RED + str(e) + Fore.RESET)

	@staticmethod
	def head_request(domain_name, path):
		try:
			r = requests.head(domain_name + path, timeout=10, headers={'User-Agent' : "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)"}, allow_redirects=False, verify=False)
			status_code = str(r.status_code)
			if status_code == '405':
				print("WARNING, (HEAD) method not allowed!!")
				exit(-1)
			return status_code
		except requests.exceptions.Timeout:
			print(Fore.RED + '[x] Connection timed out' + Fore.RESET)
		except requests.exceptions.ConnectionError as e: 
			print(Fore.RED + '[x] Connection aborted.\n    Please make sure you provided the right URL' + Fore.RESET)
		except requests.exceptions.RequestException as e:
			print(Fore.RED + str(e) + Fore.RESET)

	@staticmethod
	def interesting_headers(headers):
		for header in headers:
			if header == 'server':
				Output.interesting_headers('Server', headers.get('server'))
			elif header == 'x-powered-by':
				Output.interesting_headers('X-Powered-By', headers.get('x-powered-by'))
			elif header == 'via':
				Output.interesting_headers('Via', headers.get('via'))

	@staticmethod
	# not used atm because unreliable
	def version_information(domain_name, path, regex):
		r = requests.get(domain_name + path, stream=True, timeout=10, headers={'User-Agent' : "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)"}, verify=False)
		if r.status_code == 200:
			for content in r.iter_content(chunk_size=400, decode_unicode=False):
				regex = re.compile(regex)
				search = regex.search(str(content))
				version = search.groups()[0]
				return version