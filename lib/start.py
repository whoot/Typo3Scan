#!/usr/bin/env python

"""
Copyright (c) 2014 Jan Rude
"""

import time 
from Queue import Queue
from os.path import isfile
from threading import Thread, Lock
from colorama import Fore, Back
from lib import settings
from lib import versioninfo
from lib import login
from lib import output
from lib import extensions

# Startmethod
def check_typo_installation(domain):
	settings.DOMAIN = domain
	print '\n\n' + Fore.CYAN + '[ Checking ' + domain + ' ]' + '\n' + "-"* 70  + Fore.RESET

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
			print "Typo3 Login:".ljust(32) + Fore.RED + "Typo3 is not used on this domain" + Fore.RESET

def init_extension_search():
	settings.in_queue = Queue()
	settings.out_queue = Queue()
	versioninfo.search_version_info()
	versioninfo.output()

	if not settings.EXTENSION_LIST:
		extensions.generate_list()

	extensions.copy()
	extensions_to_check = settings.in_queue.qsize()

	if extensions_to_check is not 0:
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
			print Fore.RED + "\nReceived keyboard interrupt.\nQuitting..." + Fore.RESET
			exit(-1)
		settings.in_queue.join()

		installed_ext = settings.out_queue.qsize()
		if installed_ext is 0:
			print Fore.RED + "No extensions installed" + Fore.RESET
		else:
			t = Thread(target=output.thread, args=())
			t.daemon = True
			t.start()
			settings.out_queue.join()
			print Fore.GREEN + '\n', str(settings.EXTENSIONS_FOUND) + '/' + str(extensions_to_check),'extension(s) installed' + Fore.RESET
	else:
		print '\nSkipping check for extensions...'
