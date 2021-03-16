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
from colorama import Fore, Style
import lib.request as request
from pkg_resources import parse_version

class Domain:
    """
    This class stores following information about a domain:
        name:                   URL of the domain
        path:                   Full path to Typo3 installation
        typo3:                  If Typo3 is installed
        backend:                URL to Typo3 backend login
        typo3_version:          Typo3 Version
        typo3_vulnerabilities:  List of known CORE vulnerabilities
        installed_extensions:   List of all installed extensions
    """
    def __init__(self, name):
        if not ('http' in name):
            self.__name = 'https://' + name
        else:
            self.__name = name
        self.__path = ''
        self.__typo3 = False
        self.__backend = 'Could not be found'
        self.__typo3_version = 'Unknown'
        self.__typo3_vulnerabilities = ''
        self.__installed_extensions = {'installed': 0}
        
    def get_name(self):
        return self.__name

    def set_name(self, name):
        self.__name = name

    def set_path(self, path):
        self.__path = path

    def get_path(self):
        return self.__path

    def is_typo3(self):
        return self.__typo3

    def set_typo3(self):
        self.__typo3 = True

    def set_backend(self, url):
        self.__backend = url

    def get_backend(self):
        return self.__backend

    def set_typo3_version(self, version):
        self.__typo3_version = version

    def get_typo3_version(self):
        return self.__typo3_version

    def set_typo3_vulns(self, vuln):
        self.__typo3_vulnerabilities = vuln

    def get_typo3_vulns(self):
        return self.__typo3_vulnerabilities

    def check_root(self):
        """
        This method requests the root page and searches for a specific string.
            Usually there are some TYPO3 notes in the HTML comments.
            If found, it searches for a Typo3 path reference
            in order to determine the Typo3 installation path.
        """
        full_path = self.get_name()
        response = request.get_request('{}'.format(self.get_name()))
        if re.search('powered by TYPO3', response['html']):
            self.set_typo3()
            path = re.search('="(?:{})/?(\S*?)/?(?:typo3temp|typo3conf)/'.format(self.get_name()), response['html'])
            if path and path.group(1) != '':
                full_path = '{}/{}'.format(self.get_name(), path)            
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
                'typo3_src/CONTRIBUTING.md':'TYPO3 CMS',
                'typo3_src/composer.json':'TYPO3'
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
        print(' [+] Backend Login')
        # maybe /typo3_src/typo3/index.php too?
        response = request.get_request('{}/typo3/index.php'.format(self.get_path()))
        searchTitle = re.search('<title>(.*)</title>', response['html'])
        if searchTitle and 'Login' in searchTitle.group(0):
            print('  \u251c {}'.format(Fore.GREEN + '{}/typo3/index.php'.format(self.get_path()) + Fore.RESET))
            self.set_backend('{}/typo3/index.php'.format(self.get_path()))
        elif ('Backend access denied: The IP address of your client' in response['html']) or (response['status_code'] == 403):
            print('  \u251c {}'.format(Fore.GREEN + '{}/typo3/index.php'.format(self.get_path()) + Fore.RESET))
            print('  \u251c {}'.format(Fore.YELLOW + 'But access is forbidden (IP Address Restriction)' + Fore.RESET))
            self.set_backend('{}/typo3/index.php'.format(self.get_path()))
        else:
            print('  \u251c {}'.format(Fore.RED + 'Could not be found' + Fore.RESET))

    def search_typo3_version(self):
        """
        This methos will search for version information.
            The exact version can be found in the ChangeLog, therefore it will be requested first.
            Less specific version information can be found in the NEWS or INSTALL file. 
        """           
        files = {'typo3_src/composer.json': '(?:"typo3/cms-core":|"typo3/cms-backend":)\s?"([0-9]+\.[0-9]+\.?[0-9x]?[0-9x]?)"',
                'typo3_src/public/typo3/sysext/install/composer.json': '(?:"typo3/cms-core":|"typo3/cms-backend":)\s?"([0-9]+\.[0-9]+\.?[0-9x]?[0-9x]?)"',
                'typo3_src/typo3/sysext/adminpanel/composer.json': '(?:"typo3/cms-core":|"typo3/cms-backend":)\s?"([0-9]+\.[0-9]+\.?[0-9x]?[0-9x]?)"',
                'typo3_src/typo3/sysext/backend/composer.json': '(?:"typo3/cms-core":|"typo3/cms-backend":)\s?"(\d{1,2}\.\d{1,2}\.?[0-9]?[0-9]?)"',
                'typo3_src/typo3/sysext/info/composer.json': '(?:"typo3/cms-core":|"typo3/cms-backend":)\s?"(\d{1,2}\.\d{1,2}\.?[0-9]?[0-9]?)"',
                'typo3_src/ChangeLog': '[Tt][Yy][Pp][Oo]3 (\d{1,2}\.\d{1,2}\.?[0-9]?[0-9]?)',
                'ChangeLog': '[Tt][Yy][Pp][Oo]3 (\d{1,2}\.\d{1,2}\.?[0-9]?[0-9]?)',
                'typo3/sysext/backend/ext_emconf.php': '(?:CMS |typo3_src-)(\d{1,2}\.\d{1,2}\.?[0-9]?[0-9]?)',
                'typo3_src/typo3/sysext/install/Start/Install.php': '(?:CMS |typo3_src-)(\d{1,2}\.\d{1,2}\.?[0-9]?[0-9]?)',
                'typo3/sysext/install/Start/Install.php': '(?:CMS |typo3_src-)(\d{1,2}\.\d{1,2}\.?[0-9]?[0-9]?)',
                'typo3_src/NEWS.txt': 'http://wiki.typo3.org/TYPO3_(\d{1,2}\.\d{1,2})', 
                'typo3_src/NEWS.md': '[Tt][Yy][Pp][Oo]3 [Cc][Mm][Ss] (\d{1,2}\.\d{1,2}) - WHAT\'S NEW',
                'NEWS.txt': 'http://wiki.typo3.org/TYPO3_(\d{1,2}\.\d{1,2})',
                'NEWS.md': '[Tt][Yy][Pp][Oo]3 [Cc][Mm][Ss] (\d{1,2}\.\d{1,2}) - WHAT\'S NEW',
                'typo3_src/INSTALL.md': '(?:typo3_src-)(\d{1,2}\.\d{1,2}\.?[0-9x]?[0-9]?)',
                'typo3_src/INSTALL.txt': '(?:typo3_src-)(\d{1,2}\.\d{1,2}\.?[0-9x]?[0-9]?)',
                'INSTALL.md': '(?:typo3_src-)(\d{1,2}\.\d{1,2}\.?[0-9x]?[0-9]?)',
                'INSTALL.txt': '(?:typo3_src-)(\d{1,2}\.\d{1,2}\.?[0-9x]?[0-9]?)'
                }

        version = None
        version_path = None
        for path, regex in files.items():
            response = request.version_information('{}/{}'.format(self.get_path(), path), regex)
            if response and (version is None or (len(response) > len(version))):
                version = response
                version_path = path

        print('  | \n [+] Version Information')
        if version:
            print('  \u251c Identified Version: '.ljust(28) + '{}'.format(Style.BRIGHT + Fore.GREEN + version + Style.RESET_ALL))
            print('  \u251c Version File: '.ljust(28) + '{}{}'.format(self.get_path(), version_path))
            if len(version) == 3:
                print('  \u251c Could not identify exact version.')
                react = input('  \u251c Do you want to print all vulnerabilities for branch {}? (y/n): '.format(version))
                if react.startswith('y'):
                    version = version + '.0'
                else:
                    return False
            self.set_typo3_version(version)
            # sqlite stuff
            conn = sqlite3.connect('lib/typo3scan.db')
            c = conn.cursor()
            c.execute('SELECT advisory, vulnerability, subcomponent, affected_version_max, affected_version_min FROM core_vulns WHERE (?<=affected_version_max AND ?>=affected_version_min)', (version, version,))
            data = c.fetchall()
            json_list = {}
            if data:
                for vulnerability in data:
                    # maybe instead use this: https://zxq9.com/archives/797
                    if parse_version(version) <= parse_version(vulnerability[3]):
                        json_list[vulnerability[0]] = {'Type': vulnerability[1], 'Subcomponent': vulnerability[2], 'Affected': '{} - {}'.format(vulnerability[3], vulnerability[4]), 'Advisory': 'https://typo3.org/security/advisory/{}'.format(vulnerability[0].lower())}
                if json_list:
                    self.set_typo3_vulns(json_list)
                    print('  \u2514 Known Vulnerabilities:\n')
                    for vulnerability in json_list.keys():
                        print(Style.BRIGHT + '     [!] {}'.format(Fore.RED + vulnerability + Style.RESET_ALL))
                        print('      \u251c Vulnerability Type:'.ljust(28) + json_list[vulnerability]['Type'])
                        print('      \u251c Subcomponent:'.ljust(28) + json_list[vulnerability]['Subcomponent'])
                        print('      \u251c Affected Versions:'.ljust(28) + json_list[vulnerability]['Affected'])
                        print('      \u2514 Advisory URL:'.ljust(28) + json_list[vulnerability]['Advisory'] + '\n')
            if not json_list:
                print('  \u2514 No Known Vulnerabilities')
        else:
            print('  \u2514', Fore.RED + 'Could not be determined.' + Fore.RESET)