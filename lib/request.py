#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Typo3 Enumerator - Automatic Typo3 Enumeration Tool
# Copyright (c) 2014-2022 Jan Rude
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
# along with this program. If not, see [http://www.gnu.org/licenses/](http://www.gnu.org/licenses/)
#-------------------------------------------------------------------------------

import re
import os.path
import requests
from colorama import Fore
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def get_request(url, config):
    """
    All GET requests are done in this method.
        This method is not used, when searching for extensions and their version info
        There are three error types which can occur:
            Connection timeout
            Connection error
            anything else
        If a RequestException occurs, then we will return an empty html response body. This will cancel the root detection.
    """
    try:
        response = {}
        if config['auth']:
            r = requests.get(url, timeout=config['timeout'], headers=config['headers'], auth=(config['auth'][0], config['auth'][1]), verify=False)
        else:
            r = requests.get(url, timeout=config['timeout'], headers=config['headers'], cookies=config['cookies'], verify=False)
        response['status_code'] = r.status_code
        response['html'] = r.text
        response['headers'] = r.headers
        response['cookies'] = r.cookies
        response['url'] = r.url
        return response
    except requests.exceptions.Timeout as e:
        print(e)
        print(Fore.RED + '[x] Connection error\n    Please make sure you provided the right URL\n' + Fore.RESET)
        exit(-1)
    except requests.exceptions.RequestException as e:
        print(Fore.RED + str(e) + Fore.RESET)
        # Return an empty response['html'] element. 
        # If this error occurs within the first request made (TYPO3 detection), then all following scans will be canceled
        response['html'] = ''
        return response

def head_request(url, config):
    """
    All HEAD requests are done in this method.
        HEAD requests are used when searching for extensions
        There are three error types which can occur:
            Connection timeout
            Connection error
            anything else
    """
    try:
        if config['auth']:
            r = requests.head(url, timeout=config['timeout'], headers=config['headers'], auth=(config['auth'][0], config['auth'][1]), allow_redirects=False, verify=False)
        else:
            r = requests.head(url, timeout=config['timeout'], headers=config['headers'], cookies=config['cookies'], allow_redirects=False, verify=False)
        status_code = str(r.status_code)
        if status_code == '405':
            r = get_request(url, config)
            status_code = r['status_code']
        return status_code
    except requests.exceptions.Timeout:
        print(Fore.RED + ' [x] Connection timed out on "{}"'.format(url) + Fore.RESET)
    except requests.exceptions.RequestException as e:
        print(Fore.RED + str(e) + Fore.RESET)

def version_information(url, regex, config):
    """
        This method is used for version search only.
        It performs a GET request, if the response is 200 - Found, it reads the first 400 bytes the response only,
        because usually the TYPO3 version is in the first few lines of the response.
    """
    if regex is None:
        regex = '([0-9]+\.[0-9]+\.[0-9x][0-9x]?)'
    try:
        if config['auth']:
            r = requests.get(url, stream=True, timeout=config['timeout'], headers=config['headers'], auth=(config['auth'][0], config['auth'][1]), verify=False)
        else:
            r = requests.get(url, stream=True, timeout=config['timeout'], headers=config['headers'], cookies=config['cookies'], verify=False)
        if r.status_code == 200:
            version = None
            if ('manual.sxw' in url) and not ('Page Not Found' in r.text):
                return 'check manually'
            for content in r.iter_content(chunk_size=400, decode_unicode=False):
                try:
                    search = re.search(regex, str(content))
                    version = search.group(1)
                except:
                    try:
                        search = re.search('([0-9]+-[0-9]+-[0-9]+)', str(content))
                        version = search.group(1)
                    except:
                        continue
                if version:
                    r.close()
                    break
            return version
    except requests.exceptions.Timeout:
        print(Fore.RED + ' [x] Connection timed out on "{}"'.format(url) + Fore.RESET)
    except requests.exceptions.RequestException as e:
        print(Fore.RED + str(e) + Fore.RESET)
