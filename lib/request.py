#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Typo3 Enumerator - Automatic Typo3 Enumeration Tool
# Copyright (c) 2014-2020 Jan Rude
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
import json
import requests
from colorama import Fore
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def get_request(url):
    """
    All GET requests are done in this method.
        This method is not used, when searching for extensions and their Readmes/ChangeLogs
        There are three error types which can occur:
            Connection timeout
            Connection error
            anything else
    """
    config = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')))
    timeout = config['timeout']
    auth = config['auth']
    cookie = config['cookie']
    custom_headers = {'User-Agent' : config['User-Agent']}
    try:
        if cookie != '':
            name = cookie.split('=')[0]
            value = cookie.split('=')[1]
            custom_headers[name] = value
        response = {}
        if auth != '':
            r = requests.get(url, timeout=config['timeout'], headers=custom_headers, auth=(auth.split(':')[0], auth.split(':')[1]), verify=False)
        else:
            r = requests.get(url, timeout=config['timeout'], headers=custom_headers, verify=False)
        response['status_code'] = r.status_code
        response['html'] = r.text
        response['headers'] = r.headers
        response['cookies'] = r.cookies
        return response
    except requests.exceptions.Timeout:
        print(e)
        print(Fore.RED + '[x] Connection timed out' + Fore.RESET)
    except requests.exceptions.ConnectionError as e: 
        print(e)
        print(Fore.RED + '[x] Connection error\n | Please make sure you provided the right URL' + Fore.RESET)
        exit(-1)
    except requests.exceptions.RequestException as e:
        print(Fore.RED + str(e) + Fore.RESET)

def head_request(url):
    """
    All HEAD requests are done in this method.
        HEAD requests are used when searching for extensions and their Readmes/ChangeLogs
        There are three error types which can occur:
            Connection timeout
            Connection error
            anything else
    """
    
    config = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')))
    timeout = config['timeout']
    auth = config['auth']
    cookie = config['cookie']
    custom_headers = {'User-Agent' : config['User-Agent']}
    try:
        if cookie != '':
            name = cookie.split('=')[0]
            value = cookie.split('=')[1]
            custom_headers[name] = value
        if auth != '':
            r = requests.head(url, timeout=config['timeout'], headers=custom_headers, auth=(auth.split(':')[0], auth.split(':')[1]), verify=False)
        else:
            r = requests.head(url, timeout=config['timeout'], headers=custom_headers, allow_redirects=False, verify=False)
        status_code = str(r.status_code)
        if status_code == '405':
            print('[x] WARNING: \'HEAD\' method not allowed!')
            exit(-1)
        return status_code
    except requests.exceptions.Timeout:
        print(Fore.RED + '[x] Connection timed out' + Fore.RESET)
    except requests.exceptions.ConnectionError as e: 
        print(Fore.RED + '[x] Connection aborted.\n    Please make sure you provided the right URL' + Fore.RESET)
    except requests.exceptions.RequestException as e:
        print(Fore.RED + str(e) + Fore.RESET)

def version_information(url, regex):
    """
        This method is used for version search only.
        It performs a GET request, if the response is 200 - Found, it reads the first 400 bytes the response only,
        because usually the TYPO3 version is in the first few lines of the response.
    """
    if regex is None:
        regex = '([0-9]+\.[0-9]+\.[0-9x][0-9x]?)'
    config = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')))
    timeout = config['timeout']
    auth = config['auth']
    cookie = config['cookie']
    custom_headers = {'User-Agent' : config['User-Agent']}
    if cookie != '':
        name = cookie.split('=')[0]
        value = cookie.split('=')[1]
        custom_headers[name] = value
    if auth != '':
        r = requests.get(url, stream=True, timeout=config['timeout'], headers=custom_headers, auth=(auth.split(':')[0], auth.split(':')[1]), verify=False)
    else:
        r = requests.get(url, stream=True, timeout=config['timeout'], headers=custom_headers, verify=False)
    if r.status_code == 200:
        try:
            for content in r.iter_content(chunk_size=400, decode_unicode=False):
                search = re.search(regex, str(content))
                version = search.group(1)
                r.close()
                return version
        except:
            r.close()
            return None