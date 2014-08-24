#!/usr/bin/env python

"""
Copyright (c) 2014 Jan Rude
"""

import re
import sys
import requests
import urllib2
from colorama import Fore
from lib import settings
if sys.platform.startswith('win32') or sys.platform.startswith('cygwin'):
	import msvcrt

# Searching Typo3 login page
def search_login():
	try:
		r = requests.get(settings.DOMAIN + '/typo3/index.php', allow_redirects=False, timeout=settings.TIMEOUT, headers=settings.user_agent, verify=False)
		statusCode = r.status_code
		httpResponse = r.text
		if statusCode == 200:
			return check_title(httpResponse, r.url)
		elif (statusCode == 301) or (statusCode == 302):
			location = r.headers['location']
			answer = ''
			if sys.platform.startswith('win32') or sys.platform.startswith('cygwin'):
				print 'Got redirect to: ' + str(location) + '\nFollow? (y/n) '
				answer = msvcrt.getche()
			elif sys.platform.startswith('linux'):
				answer = raw_input('Got redirect to: ' + str(location) + '\nFollow? (y/n) ')
			if answer is 'y':
				locsplit = location.split('/')
				settings.DOMAIN = locsplit[0] + '//' + locsplit[2]
				return 'redirect'
			else:
				return check_title(httpResponse, r.url)
		elif statusCode == 404:
			return False
		else:
			print 'Oops! Got unhandled code:'.ljust(32) + str(statusCode) + ': ' + str(r.raise_for_status())
	except requests.exceptions.Timeout:
		print Fore.RED + 'Connection timed out' + Fore.RESET
	except requests.exceptions.TooManyRedirects:
		print Fore.RED + 'Too many redirects' + Fore.RESET
	except requests.exceptions.RequestException as e:
		print Fore.RED + str(e) + Fore.RESET

# Searching for Typo3 references in title
def check_title(response, url):
	try:
		regex = re.compile('<title>(.*)</title>', re.IGNORECASE)
		searchTitle = regex.search(response)
		title = searchTitle.groups()[0]
		if 'TYPO3' in title or 'TYPO3 SVN ID:' in response:
			print 'Typo3 Login:'.ljust(32) + Fore.GREEN + url + Fore.RESET
			return True
	except:
		pass
	return False

# Searching for Typo3 references in HTML comments
def check_main_page():
	req = urllib2.Request(settings.DOMAIN, None, settings.user_agent)
	req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
	try:
		connection = urllib2.urlopen(req, timeout = settings.TIMEOUT)
		response = connection.read()
		connection.close()
		try:
			cookie = connection.info().getheader('Set-Cookie')
			if 'fe_typo_user' in cookie:
				return bad_url()
		except KeyboardInterrupt:
			print Fore.RED + '\nReceived keyboard interrupt.\nQuitting...' + Fore.RESET
			exit(-1)
		except:
			try:
				regex = re.compile('TYPO3(.*)', re.IGNORECASE)
				searchHTML = regex.search(response)
				searchHTML.groups()[0]
				try:
					regex = re.compile('[Tt][Yy][Pp][Oo]3 (\d{1,2}\.\d{1,2}\.[0-9][0-9]?[' '\n])')
					searchVersion = regex.search(response)
					version = searchVersion.groups()
					settings.TYPO_VERSION = 'Typo3 ' + version[0].split()[0]
				except:
					pass
				return bad_url()
			except:
				pass
	except Exception, e:
		if '404' in str(e):
			print Fore.RED + str(e) + '\nPlease ensure you entered the right url' + Fore.RESET
		else:
			print Fore.RED + str(e) + Fore.RESET
		return 'skip'
	return False

def bad_url():
	print 'Typo3 Login:'.ljust(32) + Fore.GREEN + 'Typo3 is used, but could not find login' + Fore.RESET
	print ''.ljust(32) + 'This could result in \'no extensions are installed\'.'
	print ''.ljust(32) + 'Seems like something is wrong with the given url.'
	answer = ''
	if sys.platform.startswith('win32') or sys.platform.startswith('cygwin'):
		print ''.ljust(32) + 'Try anyway (y/n)? '
		answer = msvcrt.getch()
	elif sys.platform.startswith('linux'):
		answer = raw_input(''.ljust(32) + 'Try anyway (y/n)? ')
	if answer is 'y':
		return True
	return 'skip'
