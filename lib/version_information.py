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

import re
from lib.request import Request

class VersionInformation:
	"""
	This class will search for version information
	"""
	def search_typo3_version(self, domain):
		ChangeLog = {'/typo3_src/ChangeLog':'(\d{1,2}\.\d{1,2}\.?[0-9]?[0-9]?)',  
					'/ChangeLog':'(\d{1,2}\.\d{1,2}\.?[0-9]?[0-9]?)'
					}
		News = {'/typo3_src/NEWS.txt':'http://wiki.typo3.org/TYPO3_(\d{1,2}\.\d{1,2})', 
				'/typo3_src/NEWS.md':"TYPO3 CMS (\d{1,2}\.\d{1,2}) - WHAT'S NEW", 
				'/NEWS.txt':'http://wiki.typo3.org/TYPO3_(\d{1,2}\.\d{1,2})', 
				'/NEWS.md':"TYPO3 CMS (\d{1,2}\.\d{1,2}) - WHAT'S NEW"
				}

		version = 'could not determine'
		for path, regex in ChangeLog.items():
			response = Request.version_information(domain.get_name(), path, regex)
			if not(response is None):
				version = response
				break
		if version == 'could not determine':
			for path, regex in News.items():
				response = Request.version_information(domain.get_name(), path, regex)
				if not(response is None):
					version = response
					break
		domain.set_typo3_version(version)