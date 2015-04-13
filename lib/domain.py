#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Typo3 Enumerator - Automatic Typo3 Enumeration Tool
# Copyright (c) 2015 Jan Rude
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

class Domain(object):
	"""
	This class stores following information about a domain:
		name: 					URL of the domain
		typo3:					If Typo3 is installed
		typo3_version:			Typo3 Version
		login_found:			determines of the default login page was found or not
		extensions:				List of extensions to check for
		installed_extensions:	List of all installed extensions
	"""
	def __init__(self, name, ext_state, top=False):
		if not ('http' in name):
			self.__name = 'http://' + name
		else:
			self.__name = name
		self.__typo3 = False
		self.__typo3_version = ''
		self.__login_found = False
		self.__extension_config = [ext_state, top]
		self.__extensions = None
		self.__installed_extensions = {}
		self.__interesing_header = {}

	def get_name(self):
		return self.__name

	def set_name(self, name):
		self.__name = name

	def get_extensions(self):
		return self.__extensions

	def set_extensions(self, extensions):
		self.__extensions = extensions

	def get_extension_config(self):
		return self.__extension_config

	def get_installed_extensions(self):
		return self.__installed_extensions

	def set_installed_extensions(self, extension):
		self.__installed_extensions[extension] = False

	def set_installed_extensions_version(self, extension, ChangeLog):
		self.__installed_extensions[extension] = ChangeLog

	def get_typo3(self):
		return self.__typo3

	def set_typo3(self):
		self.__typo3 = True

	def set_typo3_version(self, version):
		self.__typo3_version = version

	def get_typo3_version(self):
		return self.__typo3_version

	def get_login_found(self):
		return self.__login_found

	def set_login_found(self):
		self.__login_found = True

	def set_interesting_headers(self, header_key, header_value):
		self.__interesing_header[header_key] = header_value

	def get_interesting_headers(self):
		return self.__interesing_header