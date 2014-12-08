#!/usr/bin/env python

"""
Copyright (c) 2014 Jan Rude
"""

import time 
from Queue import Queue
from os.path import isfile
from threading import Thread, Lock
try:
	from colorama import Fore, Back
except:
	pass
from lib import settings
from lib import versioninfo
from lib import login
from lib import output
from lib import extensions

# Startmethod
def check_typo_installation(domain):
	settings.DOMAIN = domain
	settings.EXTENSIONS_FOUND = 0
	if settings.COLORAMA:
		output = Fore.CYAN + '[ Checking ' + domain + ' ]' + '\n' + "-"* 70  + Fore.RESET
	else:
		output = '[ Checking ' + domain + ' ]' + '\n' + "-"* 70
	print '\n\n' + output

	check = login.search_login()
	if check is "redirect":
		check_typo_installation(settings.DOMAIN)

	elif check is True:
		init_extension_search()
	else:
		mainpage = login.check_main_page()
		if mainpage is True:
			init_extension_search()
		elif mainpage is not "skip":
			output("Typo3 Login:".ljust(32) + "Typo3 is not used on this domain", False)

def init_extension_search():
	settings.in_queue = Queue()
	versioninfo.search_version_info()
	versioninfo.output()

	if settings.TOP_EXTENSION != 0:
		if not settings.EXTENSION_LIST:
			extensions.generate_list()

		extensions.copy()
		extensions_to_check = settings.in_queue.qsize()

		print '\nChecking', extensions_to_check, 'extension(s)...'
		# Thanks to 'RedSparrow': http://stackoverflow.com/questions/17991033/python-cant-kill-main-thread-with-keyboardinterrupt
		try:
			while True:
				if settings.in_queue.empty() == False:
					time.sleep(0.5)
					for i in xrange(0, settings.THREADS):
						t = Thread(target=extensions.check_extension, args=())
						t.daemon = True
						t.start()
				else:
					break
		except KeyboardInterrupt:
			output("\nReceived keyboard interrupt.\nQuitting...", False)
			exit(-1)
		settings.in_queue.join()

		installed_ext = settings.EXTENSIONS_FOUND
		if installed_ext == 0:
			output("No extensions installed", False)
		else:
			output('\n' + str(settings.EXTENSIONS_FOUND) + '/' + str(extensions_to_check) + ' extension(s) installed', True)
	else:
		print '\nSkipping check for extensions...'

# print error messages
def output(message, setting):
	if settings.COLORAMA:
		if not setting:
			print Fore.RED + message + Fore.RESET
		if setting:
			print Fore.GREEN + message + Fore.RESET
	else:
		print message