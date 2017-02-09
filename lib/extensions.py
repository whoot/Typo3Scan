#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Typo3 Enumerator - Automatic Typo3 Enumeration Tool
# Copyright (c) 2014-2017 Jan Rude
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

import os.path
import json
from lib.request import Request
from lib.output import Output
from lib.thread_pool import ThreadPool

class Extensions:
	"""
	Extension class
	"""
	def __init__(self, ext_state, top, path):
		self.__ext_state = ext_state
		self.__top = top
		self.__path = path

	def load_extensions(self):
		"""
			This method loads the defined extensions from the extension file.
			IF the extension file is not found, an error is raised.
		"""
		extensions = []
		for state in self.__ext_state:
			ext_file = state + '_extensions'
			if not os.path.isfile(os.path.join(self.__path, 'extensions', ext_file)):
				raise Exception("\n\nCould not find extension file " + ext_file + '!\nTry --update')

			with open(os.path.join(self.__path, 'extensions', ext_file), 'r') as f:
				count = 0
				for extension in f:
					if not(self.__top is None):
						if count < self.__top:
							extensions.append(extension.split('\n')[0])
							count += 1
					else:
						extensions.append(extension.split('\n')[0])
				f.close()
		return extensions

	def search_extension(self, domain, extensions):
		"""
			This method searches for installed extensions.
				/typo3conf/ext/:		Local installation path. This is where extensions get usually installed.
				/typo3/ext/:			Global installation path (not used atm)
				/typo3/sysext/:			Extensions shipped with core (not used atm)
		"""
		config = json.load(open(os.path.join(self.__path, 'lib', 'config.json')))
		thread_pool = ThreadPool()
		for ext in extensions:
			thread_pool.add_job((Request.head_request, (domain.get_name(), '/typo3conf/ext/' + ext)))
			#thread_pool.add_job((Request.head_request, (domain.get_name(), '/typo3/ext/' + ext)))
			#thread_pool.add_job((Request.head_request, (domain.get_name(), '/typo3/sysext/' + ext)))
		thread_pool.start(config['threads'])

		for installed_extension in thread_pool.get_result():
			domain.set_installed_extensions(installed_extension[1][1])

	def search_ext_version(self, domain, extension_dict):
		"""
			This method adds a job for every installed extension.
			The goal is to find a ChangeLog or Readme in order to determine the version.
		"""
		config = json.load(open('lib/config.json'))
		thread_pool = ThreadPool()
		for extension_path in extension_dict:
			thread_pool.add_job((Request.head_request, (domain.get_name(), extension_path + '/ChangeLog')))
			thread_pool.add_job((Request.head_request, (domain.get_name(), extension_path + '/ChangeLog.txt')))
			thread_pool.add_job((Request.head_request, (domain.get_name(), extension_path + '/Readme.txt')))
			thread_pool.add_job((Request.head_request, (domain.get_name(), extension_path + '/README.md')))
			thread_pool.add_job((Request.head_request, (domain.get_name(), extension_path + '/README.rst')))
		
		thread_pool.start(config['threads'], True)

		for changelog_path in thread_pool.get_result():
			ext, path = self.parse_extension(changelog_path)
			domain.set_installed_extensions_version(path, ext[4])

	def parse_extension(self, path):
		ext = (path[1][1]).split('/')
		path = '/' + ext[1] + '/' + ext[2] + '/' + ext[3]
		return (ext, path)