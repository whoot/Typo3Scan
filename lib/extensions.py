#!/usr/bin/env python

"""
Copyright (c) 2014 Jan Rude
"""

import re
import time
import urllib2
from Queue import Queue
from colorama import Fore
from os.path import isfile
from threading import Thread, Lock
from lib import settings

def generate_list():
	if not isfile('extensions'):
		print(Fore.RED + "\nExtensionfile not found!\nPlease update Typo-Enumerator (python typoenum.py -u)" + Fore.RESET)
		sys.exit(-2)
	with open('extensions', 'r') as f:
		count = 0
		for extension in f:
			if settings.TOP_EXTENSION > count:
				settings.EXTENSION_LIST.append(extension.split('\n')[0])
				count += 1
			else:
				f.close()
				return

def copy():
	for extension in settings.EXTENSION_LIST:
		settings.in_queue.put(extension)

# Searching installed extensions
# Check on version if we get 200 or 403.
def check_extension():
	while True:
		extension = settings.in_queue.get()
		for path in settings.EXTENSION_PATHS:
			try:
				req = urllib2.Request('http://' + settings.DOMAIN + path + extension + '/', None, settings.user_agent)
				connection = urllib2.urlopen(req, timeout = settings.TIMEOUT)
				connection.close()
				check_extension_version(path, extension)
				settings.in_queue.task_done()
				return
			except urllib2.HTTPError, e:
				if e.code == 403:
					check_extension_version(path, extension)
					settings.in_queue.task_done()
					return
			except urllib2.URLError, e:
				pass
				#retry = raw_input('Error on checking ' + extension + ': ' + str(e.reason) + '\nRetrying? (y/n) ')
				#if retry:
				#	settings.in_queue.put(extension)
		# if extension is not in any given path, it's not installed
		if settings.verbose:
			settings.out_queue.put(extension.ljust(32) + Fore.RED + 'not installed' + Fore.RESET)
		settings.in_queue.task_done()

# Searching version of installed extension
def check_extension_version(path, extension):
	# if no version information is available, skip version search
	if extension in settings.NO_VERSIONINFO:
		if settings.verbose:
			settings.out_queue.put(extension.ljust(32) + Fore.GREEN + 'installed' + Fore.RESET + ' (no version information available)')
		else:
			settings.out_queue.put(extension.ljust(32) + Fore.GREEN + 'installed' + Fore.RESET)
	else:
		try:
			request = urllib2.Request('http://' + settings.DOMAIN + path + extension +'/ChangeLog', None, settings.user_agent)
			response = urllib2.urlopen(request, timeout = settings.TIMEOUT)
			changelog = response.read(1500)
			response.close()
			try:
				regex = re.compile("(\d{1,2}\.\d{1,2}\.?[0-9]?[0-9]?[' '\n])")
				searchVersion = regex.search(changelog)
				version = searchVersion.groups()
				settings.out_queue.put(extension.ljust(32) + Fore.GREEN + 'installed (v' + version[0].split()[0] + ')' + Fore.RESET)
			except:
				try:
					regex = re.compile("(\d{2,4}[\.\-]\d{1,2}[\.\-]\d{1,4})")
					search = regex.search(changelog)
					version = search.groups()
					settings.out_queue.put(extension.ljust(32) + Fore.GREEN + 'installed (last entry from ' + version[0] + ')' + Fore.RESET)
				except:
					if settings.verbose:
						settings.out_queue.put(extension.ljust(32) + Fore.GREEN + "installed" + Fore.RESET + " (no version information found)")
					else:
						settings.out_queue.put(extension.ljust(32) + Fore.GREEN + "installed" + Fore.RESET)
		except:
			settings.out_queue.put(extension.ljust(32) + Fore.GREEN + "installed" + Fore.RESET)