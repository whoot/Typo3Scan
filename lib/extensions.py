#!/usr/bin/env python

"""
Copyright (c) 2014 Jan Rude
"""

import re
import os
import sys
import time
import urllib2
from Queue import Queue
try:
	from colorama import Fore
except:
	pass
from os.path import isfile
from threading import Thread, Lock
from lib import settings

def generate_list():
	print ''
	for ext_file in settings.EXTENSION_FILE:
		if not isfile(os.path.join('extensions', ext_file)):
			output("Could not find extension file " + ext_file 
					+ "\nPossible values are: experimental | alpha | beta | stable | outdated | all", False)
			sys.exit(-1)

		with open(os.path.join('extensions', ext_file), 'r') as f:
			count = 0
			print "[+] Loading:", ext_file
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
# Check version if getting 200 or 403.
def check_extension():
	while True:
		extension = settings.in_queue.get()
		for path in settings.EXTENSION_PATHS:
			try:
				req = urllib2.Request(settings.DOMAIN + path + extension + '/', None, settings.user_agent)
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
				#if retry is 'y':
				#	settings.in_queue.put(extension)
		# if extension is not in any given path, it's not installed
		if settings.verbose:
			output(extension.ljust(32) + 'not installed', False)
		settings.in_queue.task_done()

# Searching version of installed extension
def check_extension_version(path, extension):
	settings.EXTENSIONS_FOUND += 1
	# if no version information is available, skip version search
	if extension in settings.NO_VERSIONINFO:
		if settings.verbose:
			output(extension.ljust(32) + 'installed (no version information available)', True)
		else:
			output(extension.ljust(32) + 'installed', True)
	else:
		try:
			request = urllib2.Request(settings.DOMAIN + path + extension +'/ChangeLog', None, settings.user_agent)
			response = urllib2.urlopen(request, timeout = settings.TIMEOUT)
			changelog = response.read(1500)
			response.close()
			try:
				regex = re.compile("(\d{1,2}\.\d{1,2}\.?[0-9]?[0-9]?[' '\n])")
				searchVersion = regex.search(changelog)
				version = searchVersion.groups()
				output(extension.ljust(32) + 'installed (v' + version[0].split()[0] + ')', True)
			except:
				try:
					regex = re.compile("(\d{2,4}[\.\-]\d{1,2}[\.\-]\d{1,4})")
					search = regex.search(changelog)
					version = search.groups()
					output(extension.ljust(32) + 'installed (last entry from ' + version[0] + ')', True)
				except:
					if settings.verbose:
						output(extension.ljust(32) + 'installed (no version information found)', True)
					else:
						output(extension.ljust(32) + 'installed', True)
		except:
			output(extension.ljust(32) + "installed", True)

def output(message, status):
	if settings.COLORAMA:
		if status:
			print Fore.GREEN + message + Fore.RESET
		else:
			print Fore.RED + message + Fore.RESET
	else:
		print message