#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Typo3Scan - Automatic Typo3 Enumeration Tool
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
import string
import random
import sqlite3
from colorama import Fore
import lib.request as request
from pkg_resources import parse_version

class Domain:
    """
    This class stores following information about a domain:
        name:                   URL of the domain
        typo3:                  If Typo3 is installed
        typo3_version:          Typo3 Version
        path:                   Full path to Typo3 installation
        installed_extensions:   List of all installed extensions
        interesting_header:     List of interesting headers
    """
    def __init__(self, name):
        if not ('http' in name):
            self.__name = 'https://' + name
        else:
            self.__name = name
        self.__typo3 = False
        self.__typo3_version = ''
        self.__path = ''
        self.__installed_extensions = {}
        self.__interesting_header = {}
        
    def get_name(self):
        return self.__name

    def set_name(self, name):
        self.__name = name

    def is_typo3(self):
        return self.__typo3

    def set_typo3(self):
        self.__typo3 = True

    def set_typo3_version(self, version):
        self.__typo3_version = version

    def get_typo3_version(self):
        return self.__typo3_version

    def set_path(self, path):
        self.__path = path

    def get_path(self):
        return self.__path

    def set_interesting_headers(self, headers, cookies):
        """
        This method searches for interesing headers in the HTTP response
            Server:           Displays the name of the server
            X-Powered-By:     Information about Frameworks (e.g. ASP, PHP, JBoss) used by the web application
            X-*:              Version information in other technologies
            Via:              Informs the client of proxies through which the response was sent
            X-Forwarded-For:  Originating IP address of a client connecting through an HTTP proxy or load balancer
            fe_typo_user:     Frontend cookie for TYPO3
        """
        for header in headers:
            if header == 'Server':
                self.__interesting_header['Server'] = headers.get('Server')
            elif header == 'X-Powered-By':
                self.__interesting_header['X-Powered-By'] = headers.get('X-Powered-By')
            elif header == 'X-Runtime':
                self.__interesting_header['X-Runtime'] = headers.get('X-Runtime')
            elif header == 'X-Version':
                self.__interesting_header['X-Version'] = headers.get('X-Version')
            elif header == 'X-AspNet-Version':
                self.__interesting_header['X-AspNet-Version'] = headers.get('X-AspNet-Version')
            elif header == 'Via':
                self.__interesting_header['Via'] = headers.get('Via')
            elif header == 'X-Forwarded-For':
                self.__interesting_header['X-Forwarded-For'] = headers.get('X-Forwarded-For')
            
        if 'fe_typo_user' in cookies.keys():
            self.__interesting_header['fe_typo_user'] = cookies['fe_typo_user']
            self.set_typo3()

    def get_interesting_headers(self):
        return self.__interesting_header

    def check_root(self):
        """
        This method requests the root page and searches for a specific string.
            Usually there are some TYPO3 notes in the HTML comments.
            If found, it searches for a Typo3 path reference
            in order to determine the Typo3 installation path.
        """
        response = request.get_request('{}'.format(self.get_name()))
        full_path = self.get_name()
        self.set_interesting_headers(response['headers'], response['cookies'])
        if re.search('powered by TYPO3', response['html']):
            self.set_typo3()
            path = re.search('="/?(\S*?)/?(?:typo3temp|typo3conf)/'.format(self.get_name()), response['html'])
            if path and path.groups()[0] != '':
                path = path.groups()[0].replace(self.get_name(), '')
                if path != '':
                    full_path = '{}/{}'.format(self.get_name(), path)
        if full_path.endswith('/'):
            full_path = full_path[:-1]
        self.set_path(full_path)

    def check_default_files(self):
        """
        This method requests different files, which are generated on installation.
            Note: They are not accessible anymore on newer Typo3 installations
        """
        files = {'typo3_src/README.md':'TYPO3 CMS',
                'typo3_src/README.txt':'TYPO3 CMS',
                'typo3_src/INSTALL.md':'INSTALLING TYPO3',
                'typo3_src/INSTALL.txt':'INSTALLING TYPO3',
                'typo3_src/LICENSE.txt':'TYPO3',
                'typo3_src/CONTRIBUTING.md':'TYPO3 CMS'
            }
        for path, regex in files.items():
            try:
                response = request.get_request('{}/{}'.format(self.get_path(), path))
                regex = re.compile(regex)
                searchInstallation = regex.search(response['html'])
                installation = searchInstallation.groups()
                self.set_typo3()
                return True
            except:
                pass
        return False

    def check_404(self):
        """
        This method requests a site which is not available by using a random generated string.
            TYPO3 installations usually generate a default error page,
            which can be used as an indicator.
        """
        random_string = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
        response = request.get_request('{}/{}'.format(self.get_path(), random_string))
        search404 = re.search('[Tt][Yy][Pp][Oo]3 CMS', response['html'])
        if search404:
            self.set_typo3()

    def search_login(self):
        """
        This method requests the default login page
            and searches for a specific string in the title or the response.
            If the access is forbidden (403), extension search is still possible.
        """
        print(' \\\n [+] Backend Login')
        # maybe /typo3_src/typo3/index.php too?
        response = request.get_request('{}/typo3/index.php'.format(self.get_path()))
        searchTitle = re.search('<title>(.*)</title>', response['html'])
        if searchTitle and 'Login' in searchTitle.group(0):
            print('  \u2514', Fore.GREEN + '{}/typo3/index.php'.format(self.get_path()) + Fore.RESET)
        elif ('Backend access denied: The IP address of your client' in response['html']) or (response['status_code'] == 403):
            print('  \u251c', Fore.GREEN + '{}/typo3/index.php'.format(self.get_path()) + Fore.RESET)
            print('  \u2514', Fore.YELLOW + 'But access is forbidden (IP Address Restriction)' + Fore.RESET)
        else:
            print('  \u251c', Fore.RED + 'Could not be found' + Fore.RESET)

    def search_typo3_version(self):
        """
        This methos will search for version information.
            The exact version can be found in the ChangeLog, therefore it will be requested first.
            Less specific version information can be found in the NEWS or INSTALL file. 
        """           
        files = {'/typo3_src/ChangeLog': '[Tt][Yy][Pp][Oo]3 (\d{1,2}\.\d{1,2}\.?[0-9]?[0-9]?)',  
                '/ChangeLog': '[Tt][Yy][Pp][Oo]3 (\d{1,2}\.\d{1,2}\.?[0-9]?[0-9]?)',
                '/typo3_src/typo3/sysext/install/Start/Install.php': '(?:CMS |typo3_src-)(\d{1,2}\.\d{1,2}\.?[0-9]?[0-9]?)',
                '/typo3/sysext/install/Start/Install.php': '(?:CMS |typo3_src-)(\d{1,2}\.\d{1,2}\.?[0-9]?[0-9]?)',
                '/typo3_src/typo3/sysext/backend/composer.json': '"typo3/cms-core": "(\d{1,2}\.\d{1,2}\.?[0-9]?[0-9]?)"',
                '/typo3_src/NEWS.txt': 'http://wiki.typo3.org/TYPO3_(\d{1,2}\.\d{1,2})', 
                '/typo3_src/NEWS.md': '[Tt][Yy][Pp][Oo]3 [Cc][Mm][Ss] (\d{1,2}\.\d{1,2}) - WHAT\'S NEW', 
                '/NEWS.txt': 'http://wiki.typo3.org/TYPO3_(\d{1,2}\.\d{1,2})', 
                '/NEWS.md': '[Tt][Yy][Pp][Oo]3 [Cc][Mm][Ss] (\d{1,2}\.\d{1,2}) - WHAT\'S NEW',
                '/INSTALL.md': '[Tt][Yy][Pp][Oo]3 [Cc][Mm][Ss] (\d{1,2}(.\d{1,2})?)',
                '/INSTALL.txt': '[Tt][Yy][Pp][Oo]3 v(\d{1})'
                }

        version = None
        for path, regex in files.items():
            response = request.version_information(self.get_path()+path, regex)
            if not (response is None) and (version is None or (len(response) > len(version))):
                version = response
                version_path = path

        print('\n [+] Version Information')
        if not (version is None):
            print('  \u251c {}'.format(Fore.GREEN + version + Fore.RESET))
            print('  \u251c see: {}{}'.format(self.get_path(), version_path))
            if len(version) == 3:
                print('  \u251c Could not identify exact version.')
                react = input('  \u251c Do you want to print all vulnerabilities for branch {}? (y/n): '.format(version))
                if react.startswith('y'):
                    version = version + '.0'
                else:
                	return False
            print('  \u2514 Known vulnerabilities\n     \\')
            # sqlite stuff
            conn = sqlite3.connect('lib/typo3scan.db')
            c = conn.cursor()
            c.execute('SELECT advisory, vulnerability, subcomponent, affected_version_max, affected_version_min FROM core_vulns WHERE (?<=affected_version_max AND ?>=affected_version_min)', (version, version,))
            data = c.fetchall()
            if not data:
                print('     \u251c None.')
            else:
                for vuln in data:
                    # maybe instead use this: https://oraerr.com/database/sql/how-to-compare-version-string-x-y-z-in-mysql-2/
                    if parse_version(version) <= parse_version(vuln[3]):
                        print('     [!] {}'.format(Fore.RED + vuln[0] + Fore.RESET))
                        print('      \u251c Vulnerability Type:'.ljust(29), vuln[1])
                        print('      \u251c Subcomponent:'.ljust(29), vuln[2])
                        print('      \u2514 Affected Versions:'.ljust(29), '{} - {}\n'.format(vuln[3], vuln[4]))
        else:
            print('  \u2514', Fore.RED + 'No version information found.' + Fore.RESET)