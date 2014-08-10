#!/usr/bin/env python

"""
Copyright (c) 2014 Jan Rude
"""

from Queue import Queue
from colorama import Fore
from threading import Thread, Lock
from lib import settings

# Output thread
def thread():
	while settings.out_queue is not settings.out_queue.empty():
		try:
			extension = settings.out_queue.get()
			print(extension)
			settings.out_queue.task_done()
		except Exception, e:
			print "Oops! Got:", e