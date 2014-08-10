#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, gzip, urllib
from collections import OrderedDict
import xml.etree.ElementTree as ElementTree

# Progressbar
def dlProgress(count, blockSize, totalSize):
	percent = int(count*blockSize*100/totalSize)
	sys.stdout.write("\rDownloading extentions: " + "%d%%" % percent)
	sys.stdout.flush()

# Download extensions from typo3 repository
def download_ext():
	try:
		urllib.urlretrieve('http://ter.sitedesign.dk/ter/extensions.xml.gz', 'extensions.gz', reporthook=dlProgress)
		inf = gzip.open('extensions.gz', 'rb')
		file_content = inf.read()
		inf.close()
		outF = file("extensions.xml", 'wb')
		outF.write(file_content)
		outF.close()
		os.remove('extensions.gz')
	except Exception, e:
		print "Oops! Got:".ljust(32), e

# Parse extensions.xml and save extensions in file
def generate_list():
	extension = 'extensions.xml'
	print "\nParsing file..."
	tree = ElementTree.parse(extension) 
	tag_dict = tree.getroot()
	exten_Dict = {}
	for extensions in tag_dict.getchildren():
			ext = {extensions.get('extensionkey'):extensions[0].text}
			exten_Dict.update(ext)	
	sorted_dict = sorted(exten_Dict.iteritems(), key=lambda x: int(x[1]), reverse=True)	
	f = open('extensions','w')
	for i in xrange(0,len(exten_Dict)):
		f.write(sorted_dict[i][0]+'\n')
	f.close()
	print 'Loaded', len(exten_Dict), 'extensions\n'
	os.remove('extensions.xml')