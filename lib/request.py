#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Typo3 Enumerator - Automatic Typo3 Enumeration Tool
# Copyright (c) 2014-2017 Jan Rude
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
import json
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from colorama import Fore
from lib.output import Output

class Request:
	"""
		This class is used to make all server requests
	"""
	@staticmethod
	def get_request(domain_name, path):
		"""
		All GET requests are done in this method.
			This method is not used, when searching for extensions and their Readmes/ChangeLogs
			There are three error types which can occur:
				Connection timeout
				Connection error
				anything else
		"""
		try:
			config = json.load(open('lib/config.json'))
			r = requests.get(domain_name + path, timeout=config['timeout'], headers={'User-Agent' : config['agent']}, verify=False)
			httpResponse = str((r.text).encode('utf-8'))
			headers = r.headers
			cookies = r.cookies
			status_code = r.status_code
			response = [httpResponse, headers, cookies, status_code]
			return response
		except requests.exceptions.Timeout:
			print(Fore.RED + '[x] Connection timed out' + Fore.RESET)
		except requests.exceptions.ConnectionError as e: 
			print(Fore.RED + '[x] Connection error\n | Please make sure you provided the right URL' + Fore.RESET)
		except requests.exceptions.RequestException as e:
			print(Fore.RED + str(e) + Fore.RESET)

	@staticmethod
	def head_request(domain_name, path):
		"""
		All HEAD requests are done in this method.
			HEAD requests are used when searching for extensions and their Readmes/ChangeLogs
			There are three error types which can occur:
				Connection timeout
				Connection error
				anything else
		"""
		try:
			config = json.load(open('lib/config.json'))
			r = requests.head(domain_name + path, timeout=config['timeout'], headers={'User-Agent' : config['agent']}, allow_redirects=False, verify=False)
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
	def interesting_headers(headers, cookies):
		"""
		This method searches for interesing headers in the HTTP response.
			Server:			Displays the name of the server
			X-Powered-By:	Information about Frameworks (e.g. ASP, PHP, JBoss) used by the web application
			X-*:			Version information in other technologies
			Via:			Informs the client of proxies through which the response was sent.
			be_typo_user:	Backend cookie for TYPO3
			fe_typo_user:	Frontend cookie for TYPO3
		"""
		found_headers = {}
		for header in headers:
			if header == 'server':
				found_headers['Server'] = headers.get('server')
			elif header == 'x-powered-by':
				found_headers['X-Powered-By'] = headers.get('x-powered-by')
			elif header == 'x-runtime':
				found_headers['X-Runtime'] = headers.get('x-runtime')
			elif header == 'x-version':
				found_headers['X-Version'] = headers.get('x-version')
			elif header == 'x-aspnet-version':
				found_headers['X-AspNet-Version'] = headers.get('x-aspnet-version')
			elif header == 'via':
				found_headers['Via'] = headers.get('via')
		try:
			typo_cookie = cookies['be_typo_user']
			found_headers['be_typo_user'] = typo_cookie
		except:
			pass
		try:
			typo_cookie = cookies['fe_typo_user']
			found_headers['fe_typo_user'] = typo_cookie
		except:
			pass
		return found_headers

	@staticmethod
	def version_information(domain_name, path, regex):
		"""
			This method is used for version search only.
			It performs a GET request, if the response is 200 - Found, it reads the first 400 bytes the response only,
			because usually the TYPO3 version is in the first few lines of the response.
		"""
		config = json.load(open('lib/config.json'))
		r = requests.get(domain_name + path, stream=True, timeout=config['timeout'], headers={'User-Agent' : config['agent']}, verify=False)
		if r.status_code == 200:
			try:
				for content in r.iter_content(chunk_size=400, decode_unicode=False):
					regex = re.compile(regex)
					search = regex.search(str(content))
					version = search.groups()[0]
					return version
			except:
				return None