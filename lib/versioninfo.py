#!/usr/bin/env python

"""
Copyright (c) 2014 Jan Rude
"""

import re
import urllib2
from colorama import Fore
from lib import settings

# Searching for Typo3 version
def search_version_info():
	for path, regex in settings.TYPO3_VERSION_INFO.iteritems():
		try:
			request = urllib2.Request(settings.DOMAIN + path, None, settings.user_agent)
			response = urllib2.urlopen(request, timeout = settings.TIMEOUT)
			news = response.read(700)
			response.close()
			regex = re.compile(regex)
			search = regex.search(news)
			version = search.groups()
			if settings.TYPO_VERSION is None or (len('Typo3' + version[0]) > len(settings.TYPO_VERSION)):
				settings.TYPO_VERSION = 'Typo3 ' + version[0]
				return
		except:
			pass

# Output of Typo3 version
def output():
	if settings.TYPO_VERSION is None:
		print "Typo3 Version:".ljust(32) + Fore.RED + "Not found" + Fore.RESET
	else:
		print "Typo3 Version:".ljust(32) + Fore.GREEN + settings.TYPO_VERSION + Fore.RESET
		print "Link to vulnerabilities:".ljust(32) + "http://www.cvedetails.com/version-search.php?vendor=&product=Typo3&version=" + settings.TYPO_VERSION.split()[1]