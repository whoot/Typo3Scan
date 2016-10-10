#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Typo3 Enumerator - Automatic Typo3 Enumeration Tool
# Copyright (c) 2016 Jan Rude
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/](http://www.gnu.org/licenses/)
#-------------------------------------------------------------------------------

import os, sys, gzip, urllib.request
from collections import OrderedDict
import xml.etree.ElementTree as ElementTree

class Update:
	"""
	This class updates the Typo3 extensions

	It will download the extension file from the official repository, 
	unpack it and sort the extensions in different files
	"""
	def __init__(self):
		print('')
		self.download_ext()
		self.generate_list()

	# Progressbar
	def dlProgress(self, count, blockSize, totalSize):
		"""
			Progressbar for extension download
		"""
		percent = int(count*blockSize*100/totalSize)
		sys.stdout.write('\r[+] Downloading extentions: ' + '%d%%' % percent)
		sys.stdout.flush()

	# Download extensions from typo3 repository
	def download_ext(self):
		"""
			Download extensions from server and unpack the ZIP
		"""
		try:
			# Maybe someday we need to use mirrors: https://repositories.typo3.org/mirrors.xml.gz
			urllib.request.urlretrieve('https://typo3.org/fileadmin/ter/extensions.xml.gz', 'extensions.gz', reporthook=self.dlProgress)
			with gzip.open('extensions.gz', 'rb') as f:
				file_content = f.read()
			f.close()
			outF = open('extensions.xml', 'wb')
			outF.write(file_content)
			outF.close()
			os.remove('extensions.gz')
		except Exception as e:
			print ('\n', e)

	# Parse extensions.xml and save extensions in files
	def generate_list(self):
		"""
			Parse the extension file and 
			sort them according to state and download count
		"""
		experimental = {} # 'experimental' and 'test'
		alpha = {}
		beta = {}
		stable = {}
		outdated = {} # 'obsolete' and 'outdated'
		allExt = {}

		print ('\n[+] Parsing file...')
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
		print ('[+] Sorting according to number of downloads...')
		sorted_experimental = sorted(experimental.items(), key=lambda x: int(x[1]), reverse=True)
		sorted_alpha = sorted(alpha.items(), key=lambda x: int(x[1]), reverse=True)
		sorted_beta = sorted(beta.items(), key=lambda x: int(x[1]), reverse=True)
		sorted_stable = sorted(stable.items(), key=lambda x: int(x[1]), reverse=True)
		sorted_outdated = sorted(outdated.items(), key=lambda x: int(x[1]), reverse=True)
		sorted_allExt = sorted(allExt.items(), key=lambda x: int(x[1]), reverse=True)

		print ('[+] Generating files...')
		f = open(os.path.join('extensions', 'experimental_extensions'),'w')
		for i in range(0,len(sorted_experimental)):
			f.write(sorted_experimental[i][0]+'\n')
		f.close()

		f = open(os.path.join('extensions', 'alpha_extensions'),'w')
		for i in range(0,len(sorted_alpha)):
			f.write(sorted_alpha[i][0]+'\n')
		f.close()

		f = open(os.path.join('extensions', 'beta_extensions'),'w')
		for i in range(0,len(sorted_beta)):
			f.write(sorted_beta[i][0]+'\n')
		f.close()

		f = open(os.path.join('extensions', 'stable_extensions'),'w')
		for i in range(0,len(sorted_stable)):
			f.write(sorted_stable[i][0]+'\n')
		f.close()

		f = open(os.path.join('extensions', 'outdated_extensions'),'w')
		for i in range(0,len(sorted_outdated)):
			f.write(sorted_outdated[i][0]+'\n')
		f.close()

		f = open(os.path.join('extensions', 'all_extensions'),'w')
		for i in range(0,len(sorted_allExt)):
			f.write(sorted_allExt[i][0]+'\n')
		f.close()

		print ('[+] Loaded', len(sorted_allExt), 'extensions')
		os.remove('extensions.xml')