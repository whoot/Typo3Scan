#!/usr/bin/env python
# -*- coding: utf-8 -*-

################## ChangeLog ##################
## v0.1 Prototype			     ##
## v0.2 Added version search for Typo3 	     ##
## v0.3 Added version guessing		     ##
## v0.4 Optimized requests 		     ##
## v0.5 Added support for Typo v6.X  	     ##
## v0.6 Added extension search		     ##
## v0.7 Added version search for extensions  ##
## v0.8 Added support for TOR Service 	     ##
###############################################

############ Version information ##############
__version__ = "0.8"
__program__ = "Typo-Enumerator v" + __version__
__description__ = 'Find out the Typo3 Version, Login-URL and Extensions'
__author__ = "Jan Rude"
__licence__ = "BSD Licence"
__status__ = "Development"  # ("Prototype", "Development", "Final")
###############################################

################## Imports ####################
import os
import re
import gzip
import time
import socket
import urllib
import urllib2
import argparse
import datetime
from Queue import Queue
from colorama import Fore
from os.path import isfile
from operator import itemgetter
from threading import Thread, Lock
from collections import OrderedDict
import xml.etree.ElementTree as ElementTree
###############################################

############### Global variables ##############
user_agent = {'User-Agent' : None}
extension_list = []
verbosity = False
###############################################

# Checks the Typo version
def check_typo_version_ChangeLog(domain):
	global verbosity
	global user_agent
	try:
		url = urllib2.Request('http://' + domain + '/typo3_src/ChangeLog', None, user_agent)
		f = urllib2.urlopen(url, timeout = 3.0)
		changelog = f.read(200)
		f.close()
		regex = re.compile("RELEASE] Release of (.*)")
		searchVersion = regex.search(changelog)
		version = searchVersion.groups()
		print "Typo3 Version:".ljust(32) + Fore.GREEN + version[0] + Fore.RESET
		print "Link to vulnerabilities:".ljust(32) + "http://www.cvedetails.com/version-search.php?vendor=&product=Typo3&version=" + version[0].split()[1]
	except Exception, e:
		if verbosity:
			print "Typo3 Version:".ljust(32) + "first check failed, trying second one..."
		check_typo_version_NEWS_TXT(domain)

def check_typo_version_NEWS_TXT(domain):
	global verbosity
	global user_agent
	try:
		url = urllib2.Request('http://' + domain + '/typo3_src/NEWS.txt', None, user_agent)
		f = urllib2.urlopen(url, timeout = 3.0)
		changelog = f.read(500)
		f.close()
		regex = re.compile("This document contains information about (.*) which")
		searchVersion = regex.search(changelog)
		version = searchVersion.groups()
		print "Typo3 Version:".ljust(32), Fore.GREEN + version[0] + '.XX' + Fore.RED + ' (only guessable)'+ Fore.RESET
		print "Link to vulnerabilities:".ljust(32) + "http://www.cvedetails.com/version-search.php?vendor=&product=Typo3&version=" + version[0].split()[2]
	except:
		if verbosity:
			print "Typo3 Version:".ljust(32) + "second check failed, trying third one..."
		check_typo_version_NEWS_MD(domain)

def check_typo_version_NEWS_MD(domain):
	global user_agent
	try:
		url = urllib2.Request('http://' + domain + '/typo3_src/NEWS.md', None, user_agent)
		f = urllib2.urlopen(url, timeout = 3.0)
		changelog = f.read(80)
		f.close()
		regex = re.compile("(.*) - WHAT'S NEW")
		searchVersion = regex.search(changelog)
		version = searchVersion.groups()
		print "Typo3 Version:\t\t", Fore.GREEN + version[0] + '.XX' + Fore.RED + ' (only guessable)'+ Fore.RESET
		print "Link to vulnerabilities:".ljust(32) + "http://www.cvedetails.com/version-search.php?vendor=&product=Typo3&version=" + version[0].split()[2]
	except:
		print "Typo3 Version:".ljust(32) + Fore.RED + "Not found" + Fore.RESET

# Checks the Typo login
def check_typo_login(domain):
	global user_agent
	try:	
		req = urllib2.Request('http://' + domain + '/typo3/index.php', None, user_agent)
		connection = urllib2.urlopen(req)
		response = connection.read()
		return check_title(response, connection.geturl())
		connection.close()
	except urllib2.HTTPError, e:
		if e.code == 403:
			return check_title(response, connection.geturl())
		elif e.code == 404:
			print "Typo3 Login:".ljust(32) + Fore.RED + "Typo3 is not used on this domain" + Fore.RESET
	except urllib2.URLError, e:
		print str(e.reason)
	except Exception, e:
		import traceback
		print ('generic exception: ', traceback.format_exc())


# Checks, if URL is a Typo-Login
def check_title(httpResponse, url):
	regex = re.compile("<title>(.*)</title>", re.IGNORECASE)
	searchTitle = regex.search(httpResponse)
	title = searchTitle.groups()[0]
	if 'TYPO3' in title or 'TYPO3 SVN ID:' in httpResponse:
		print "Typo3 Login:".ljust(32) + Fore.GREEN + url + Fore.RESET
		return True
	else:
		print "Typo3 Login:".ljust(32) + Fore.RED + "Typo3 is not used on this domain" + Fore.RESET
		return False

# Searches for installed extensions
def check_extensions(domain, input_queue, output_queue):
	global user_agent
	global verbosity
	while True:
		extension = input_queue.get()
		try:
			req = urllib2.Request('http://' + domain + '/typo3conf/ext/' + extension + "/", None, user_agent)
			connection = urllib2.urlopen(req)
			connection.close()
			check_extension_version(domain, extension, output_queue)
		except urllib2.HTTPError, e:
			if e.code == 403:
				check_extension_version(domain, extension, output_queue)
			elif e.code == 404:
				if verbosity:
					output_queue.put(extension.ljust(32) + Fore.RED + "not installed" + Fore.RESET)
				pass
		except urllib2.URLError, e:
			print str(e.reason)
		except Exception, e:
				import traceback
				print ('generic exception: ', traceback.format_exc())
		input_queue.task_done()

# Searches for version of installed extension
def check_extension_version(domain, extension, output_queue):
	global verbosity
	global user_agent
	try:
		url = urllib2.Request('http://' + domain + '/typo3conf/ext/' + extension + '/ChangeLog', None, user_agent)
		connection = urllib2.urlopen(url, timeout = 15.0)
		changelog = connection.read(1500)
		connection.close()
		regex = re.compile("(\d{1,2}\.\d{1,2}\.[0-9][0-9]?[' '\n])")
		searchVersion = regex.search(changelog)
		version = searchVersion.groups()
		output_queue.put(extension.ljust(32) + Fore.GREEN + "installed (v" + version[0].split()[0] + ")" + Fore.RESET)
	except:
		try:
			regex = re.compile("(\d{2,4}[\.\-]\d{1,2}[\.\-]\d{1,4})")
			searchVersion = regex.search(changelog)
			version = searchVersion.groups()
			output_queue.put(extension.ljust(32) + Fore.GREEN + "installed (last entry from " + version[0] + ")" + Fore.RESET)
		except:
			if verbosity:
				output_queue.put(extension.ljust(32) + Fore.GREEN + "installed" + Fore.RESET + " (could not find version)")
			else:
				output_queue.put(extension.ljust(32) + Fore.GREEN + "installed" + Fore.RESET)

# Output
def output_thread(q):
	if q.empty():
		print Fore.RED + "No extensions are installed" + Fore.RESET
	else:	
		while q is not q.empty():
			try:
				extension = q.get()
				print(extension)
				q.task_done()
			except Exception, e:
				print "Oops! Got:", e

# Loading extensions
def generate_extensions_list(top):
	global extension_list
	extension = 'extensions.xml'
	print "\nLoading extensions..."
	if not isfile(extension):
	 	print(Fore.RED + "File not found: " + extension + "\nAborting..." + Fore.RESET)
	 	sys.exit(-2)

	tree = ElementTree.parse(extension) 
	tag_dict = tree.getroot()
	exten_Dict = {}

	for extensions in tag_dict.getchildren():
			ext = {extensions.get('extensionkey'):extensions[0].text}
			exten_Dict.update(ext)
	print 'Loaded ' , len(exten_Dict), ' extensions\n'

	if top is not None:
		sorted_dict = sorted(exten_Dict.iteritems(), key=lambda x: int(x[1]), reverse=True)
			
		for i in xrange(0,top):
			extension_list.append(sorted_dict[i][0])
	else:
		for extension_name in tag_dict:
			extension_list.append(extension_name.get('extensionkey'))

# Copy used extensions in queue
def copy_extensions(input_queue):
	global extension_list
	for ext in extension_list:
		input_queue.put(ext)

# Progressbar
def dlProgress(count, blockSize, totalSize):
	percent = int(count*blockSize*100/totalSize)
	sys.stdout.write("\rDownloading extentions: " + "%d%%" % percent)
	sys.stdout.flush()

# Update function
def update():
	try:
		urllib.urlretrieve('http://ter.sitedesign.dk/ter/extensions.xml.gz', 'extensions.gz', reporthook=dlProgress)
		inf = gzip.open('extensions.gz', 'rb')
		file_content = inf.read()
		inf.close()
		outF = file("extensions.xml", 'wb')
		outF.write(file_content)
		outF.close()
		print "\n"
		os.remove('extensions.gz')
	except Exception, e:
		print "Oops! Got:".ljust(32), e

# Using Privoxy and TOR for all connections
def setting_up_tor():
	try:
		import socks
	except:
		print "The module 'SocksiPy' is not installed.\nPlease install it with: sudo apt-get install python-socksipy"
		sys.exit(-2)

	print "Setting up proxy to Privoxy on Port 8118"
	socks.setdefaultproxy(socks.PROXY_TYPE_HTTP, "127.0.0.1", 8118, True)
	socket.socket = socks.socksocket
	try:
		url = urllib2.Request('https://check.torproject.org/')
		torcheck = urllib2.urlopen(url)
		response = torcheck.read()
		torcheck.close()
	except:
		print "Failed to connect to Privoxy and/or TOR!\nPlease make sure they are running and configured!\nYou can start them with:\nservice privoxy start\nservice tor start\n"
		sys.exit(-2)
	try:
		regex = re.compile('Congratulations. This browser is configured to use Tor.')
		searchVersion = regex.search(response)
		version = searchVersion.groups()
		print "Connection to TOR established"
	except:
		print "It seems like TOR is not used.\nAborting...\n"
		sys.exit(-2)

# Starting checks
def start(domain, top, tor):
	in_queue = Queue()
	out_queue = Queue()
	regex = re.compile("(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})")
	searchIP = regex.search(domain)
	if not (searchIP is None):
		IP = searchIP.groups()[0]
		hostname = socket.gethostbyaddr(IP)
		print("\n\n[*] Check for " + domain + " (" + hostname[0] + ")")
	else:
		print("\n\n[*] Check for " + domain)		
		
	if check_typo_login(domain) is True:
		if not extension_list:
			generate_extensions_list(top)
		
		check_typo_version_ChangeLog(domain)
		copy_extensions(in_queue)
		print '\nChecking', in_queue.qsize(), 'Extensions:\nThis may take a while...'
		if tor:
			threads = 2
		else:
			threads = 10
		for i in xrange(0, threads):
			t = Thread(target=check_extensions, args=(domain, in_queue, out_queue))
			t.daemon = True
			t.start()
		in_queue.join()

		t = Thread(target=output_thread, args=(out_queue,))
		t.daemon = True
		t.start()
		out_queue.join()

# Main
def main(argv):
	global user_agent
	global verbosity
	parser = argparse.ArgumentParser(add_help=False, usage='typoenum.py -d DOMAIN [DOMAIN ...] | -f FILE [--user_agent USER-AGENT] [--top VALUE] [-v] [--tor]')
	group = parser.add_mutually_exclusive_group()
	group.add_argument('-d', '--domain', dest='domain', type=str, nargs='+')
	group.add_argument('-f', '--file', dest='file', help='File with a list of domains')
	group.add_argument('-u', '--update', dest='update', action='store_true',help='Get/Update the extension file')
	parser.add_argument('--user_agent', dest='user_agent', default='Mozilla/5.0', metavar='USER-AGENT (default: Mozilla/5.0)')
	parser.add_argument('--top', type=int, dest='top', metavar='VALUE', help='Check only most X downloaded extensions (default: all)', default=None)
	parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
	parser.add_argument("--tor", help="using tor for connections", action="store_true")
	args = parser.parse_args()
	
	if not args.domain and not args.file and not args.update:
		parser.print_help()
		return True

	if args.tor:
		setting_up_tor()

	if args.update:
		update()
		return True

	user_agent = {'User-Agent' : args.user_agent}
	verbosity = args.verbose

	if args.domain and not args.file:
		for dom in args.domain:
			start(dom, args.top, args.tor)

	elif not args.domain and args.file:
		if not isfile(args.file):
			print(Fore.RED + "\nFile not found: " + args.file + "\nAborting..." + Fore.RESET)
			sys.exit(-2)
		else:
			with open(args.file, 'r') as f:
				for line in f:
					start(line.strip(), args.top, args.tor)
	print '\n'
	now = datetime.datetime.now()
	print __program__ + ' finished at ' + now.strftime("%Y-%m-%d %H:%M:%S") + '\n'
	return True

if __name__ == "__main__":
	import sys
	print('\n' + 70*'*')
	print('\t' + __program__ )
	print('\t' + __description__)
	print('\t' + '(c)2014 by ' + __author__)
	print('\t' + 'Status:\t' + __status__)
	print('\t' + 'For legal purposes only!')
	print(70*'*' + '\n')
	sys.exit( not main( sys.argv ) )
