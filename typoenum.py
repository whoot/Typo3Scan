#!/usr/bin/env python
# -*- coding: utf-8 -*-

############ Version information ##############
__version__ = "0.3"
__program__ = "Typo-Enumerator v" + __version__
__description__ = 'Automatic Typo3 and Typo3 extensions enumeration tool'
__author__ = "Jan Rude"
__licence__ = "BSD Licence"
__status__ = "Development"
###############################################

import os
import datetime
import argparse
import warnings
from colorama import Fore, Style
warnings.filterwarnings(action="ignore", message=".*was already imported", category=UserWarning)
warnings.filterwarnings(action="ignore", category=DeprecationWarning)
from lib import settings
from lib import update
from lib import start

# Main
def main(argv):
	parser = argparse.ArgumentParser(usage='typoenum.py [options]')
	group = parser.add_mutually_exclusive_group()
	anonGroup = parser.add_mutually_exclusive_group()
	group.add_argument('-d', '--domain', dest='domain', type=str, nargs='+')
	group.add_argument('-f', '--file', dest='file', help='File with a list of domains')
	group.add_argument('-u', '--update', dest='update', action='store_true',help='Update the extension file')
	parser.add_argument('--user_agent', dest='user_agent', metavar='USER-AGENT (default: Mozilla/5.0)')
	parser.add_argument('--top', type=int, dest='top', metavar='VALUE', help='Check only most X downloaded extensions (default: all)')
	anonGroup.add_argument('--tor', help='using only TOR for connections', action='store_true')
	anonGroup.add_argument('--privoxy', help='using only Privoxy for connections', action='store_true')
	anonGroup.add_argument('--tp', help='using TOR and Privoxy for connections', action='store_true')
	parser.add_argument('-p', '--port', dest='port', help='Port for TOR/Privoxy (default: 9050/8118)', type=int)
	parser.add_argument('-t', '--threads', dest='threads', default=settings.THREADS, type=int, help=' Threads for HTTP connections (default: 7)')
	parser.add_argument('--timeout', dest='timeout', default=settings.TIMEOUT, type=int, help='(default: 20)')
	parser.add_argument('-v', '--verbose', help='increase output verbosity', action='store_true')
	args = parser.parse_args()

	try:
		if args.update:
			update.download_ext()
			update.generate_list()
			return True

		if args.threads > settings.MAX_NUMBER_OF_THREADS:
			print Fore.RED + "Warning! Threads are set to", args.threads,"(max value is 10)\nThis can cause connection issues and/or DoS\nAborting...." + Fore.RESET
			sys.exit(-2)

		if args.tor:
			from lib import tor_only
			tor_only.start_daemon()
			if args.port:
				tor_only.connect(args.port)
			else:
				tor_only.connect(settings.DEFAULT_TOR_PORT)

		elif args.privoxy:
			from lib import privoxy_only
			privoxy_only.start_daemon()
			if args.port:
				privoxy_only.connect(args.port)
			else:
				privoxy_only.connect(settings.DEFAULT_PRIVOXY_PORT)

		elif args.tp:
			from lib import tor_with_privoxy as tp
			tp.start_daemon()
			if args.port:
				tp.connect(args.port)
			else:
				tp.connect(settings.DEFAULT_PRIVOXY_PORT)

		if args.user_agent:
			settings.user_agent.update({'User-Agent':args.user_agent})

		if args.verbose:
			settings.verbose = args.verbose

		if args.top or args.top is 0:
			settings.TOP_EXTENSION = args.top

		if args.timeout:
			settings.TIMEOUT = args.timeout

		if args.domain:
			for dom in args.domain:
				start.start(dom)

		elif args.file:
			if not isfile(args.file):
				print(Fore.RED + "\nFile not found: " + args.file + "\nAborting..." + Fore.RESET)
				sys.exit(-2)
			else:
				with open(args.file, 'r') as f:
					for line in f:
						start.start(line.strip('\n')[0])
	except Exception, e:
		import traceback
		print ('generic exception: ', traceback.format_exc())

	finally:
		if args.tor:
			tor_only.stop()

		elif args.privoxy:
			privoxy_only.stop()

		elif args.tp:
			tp.stop()

		print '\n'
		now = datetime.datetime.now()
		print __program__ + ' finished at ' + now.strftime("%Y-%m-%d %H:%M:%S") + '\n'
		Style.RESET_ALL
		return True

if __name__ == "__main__":
	import sys
	print(Style.BRIGHT + '\n' + 70*'*')
	print('\t' + __program__ )
	print('\t' + __description__)
	print('\t' + '(c)2014 by ' + __author__)
	print('\t' + 'Status:\t' + __status__)
	print('\t' + 'For legal purposes only!')
	print(70*'*')
	sys.exit( not main( sys.argv ) )