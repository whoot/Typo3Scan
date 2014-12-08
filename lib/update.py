#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, gzip, urllib
from collections import OrderedDict
import xml.etree.ElementTree as ElementTree

# Progressbar
def dlProgress(count, blockSize, totalSize):
	percent = int(count*blockSize*100/totalSize)
	sys.stdout.write("\r[+] Downloading extentions: " + "%d%%" % percent)
	sys.stdout.flush()

# Download extensions from typo3 repository
def download_ext():
	try:
		urllib.URLopener.version = 'TYPO3/7.0.0'		
		urllib.urlretrieve('http://ter.sitedesign.dk/ter/extensions.xml.gz', 'extensions.gz', reporthook=dlProgress)
		inf = gzip.open('extensions.gz', 'rb')
		file_content = inf.read()
		inf.close()
		outF = file("extensions.xml", 'wb')
		outF.write(file_content)
		outF.close()
		os.remove('extensions.gz')
	except Exception, e:
		print "\nOops! Got:", e

# Parse extensions.xml and save extensions in files
def generate_list():
	experimental = {} # everything with 'experimental' and 'test'
	alpha = {}
	beta = {}
	stable = {}
	outdated = {} # everything with 'obsolete' and 'outdated'
	allExt = {}

	print "\n[+] Parsing file..."
	tree = ElementTree.parse('extensions.xml') 
	root = tree.getroot()
	extension = 0
	# for every extension in file
	for child in root:
		# insert every extension in "allExt" dictionary
		allExt.update({child.get('extensionkey'):child[0].text})
		# and search the last version entry
		version = 0
		for version_entry in root[extension].iter('version'):
			version +=1
		# get the state of the latest version
		state = (str(root[extension][version][2].text)).lower()
		if state == 'experimental' or state == 'test':
			experimental.update({child.get('extensionkey'):child[0].text})
		elif state == 'alpha':
			alpha.update({child.get('extensionkey'):child[0].text})
		elif state == 'beta':
			beta.update({child.get('extensionkey'):child[0].text})
		elif state == 'stable':
			stable.update({child.get('extensionkey'):child[0].text})
		elif state == 'obsolete' or state == 'outdated':
			outdated.update({child.get('extensionkey'):child[0].text})
		extension+=1

	# sorting lists according to number of downloads
	print "[+] Sorting according to number of downloads..."
	sorted_experimental = sorted(experimental.iteritems(), key=lambda x: int(x[1]), reverse=True)
	sorted_alpha = sorted(alpha.iteritems(), key=lambda x: int(x[1]), reverse=True)
	sorted_beta = sorted(beta.iteritems(), key=lambda x: int(x[1]), reverse=True)
	sorted_stable = sorted(stable.iteritems(), key=lambda x: int(x[1]), reverse=True)
	sorted_outdated = sorted(outdated.iteritems(), key=lambda x: int(x[1]), reverse=True)
	sorted_allExt = sorted(allExt.iteritems(), key=lambda x: int(x[1]), reverse=True)

	print "[+] Generating files..."
	f = open(os.path.join('extensions', 'experimental_extensions'),'w')
	for i in xrange(0,len(sorted_experimental)):
		f.write(sorted_experimental[i][0]+'\n')
	f.close()

	f = open(os.path.join('extensions', 'alpha_extensions'),'w')
	for i in xrange(0,len(sorted_alpha)):
		f.write(sorted_alpha[i][0]+'\n')
	f.close()

	f = open(os.path.join('extensions', 'beta_extensions'),'w')
	for i in xrange(0,len(sorted_beta)):
		f.write(sorted_beta[i][0]+'\n')
	f.close()

	f = open(os.path.join('extensions', 'stable_extensions'),'w')
	for i in xrange(0,len(sorted_stable)):
		f.write(sorted_stable[i][0]+'\n')
	f.close()

	f = open(os.path.join('extensions', 'outdated_extensions'),'w')
	for i in xrange(0,len(sorted_outdated)):
		f.write(sorted_outdated[i][0]+'\n')
	f.close()

	f = open(os.path.join('extensions', 'all_extensions'),'w')
	for i in xrange(0,len(sorted_allExt)):
		f.write(sorted_allExt[i][0]+'\n')
	f.close()

	print '[+] Loaded', len(sorted_allExt), 'extensions\n'
	os.remove('extensions.xml')