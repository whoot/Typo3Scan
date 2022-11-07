#!/usr/bin/env python3
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

import sqlite3
import os.path
from colorama import Fore, Style
import lib.request as request
from lib.thread_pool import ThreadPool
from pkg_resources import parse_version

class Extensions:
    """
    Extension class
    """
    def __init__(self, domain, extensions, config):
        self.__domain = domain
        self.__extensions = extensions
        self.__config = config
        self.__database = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'typo3scan.db')

    def search_extension(self):
        """
            This method loads the extensions from the database and searches for installed extensions.
                /typo3conf/ext/:        Local installation path. This is where extensions usually get installed.
                /typo3/sysext/:         Extensions shipped with core
        """
        found_extensions = {}
        thread_pool = ThreadPool()
        for ext in self.__extensions:
            thread_pool.add_job((request.head_request, ('{}/typo3conf/ext/{}/'.format(self.__domain, ext), self.__config)))
            thread_pool.add_job((request.head_request, ('{}/typo3/sysext/{}/'.format(self.__domain, ext), self.__config)))
        thread_pool.start(self.__config['threads'])

        for installed_extension in thread_pool.get_result():
            url = (installed_extension[1][0])[:-1]
            name = url[url.rfind('/')+1:]
            found_extensions[name] = {'url':url, 'version': None, 'file': None}
        return found_extensions

    def search_ext_version(self, found_extensions):
        """
            This method adds a job for every installed extension.
            The goal is to find a file with version information.
        """
        thread_pool = ThreadPool()
        for extension,values in found_extensions.items():
            thread_pool.add_job((request.version_information, (values['url'] + '/composer.json', '(?:"dev-master"|"version")\s?[:=]\s?"?([0-9]+\.[0-9]+\.?[0-9x]?[0-9x]?)', self.__config)))
            thread_pool.add_job((request.version_information, (values['url'] + '/Documentation/Settings.yml', '(?:release\s?[=:])\s?"?([0-9]+\.[0-9]+\.?[0-9]?[0-9]?)', self.__config)))
            thread_pool.add_job((request.version_information, (values['url'] + '/Documentation/Settings.yaml', '(?:release\s?[=:])\s?"?([0-9]+\.[0-9]+\.?[0-9]?[0-9]?)', self.__config)))
            thread_pool.add_job((request.version_information, (values['url'] + '/Documentation/Settings.cfg', '(?:release\s?[=:])\s?"?([0-9]+\.[0-9]+\.?[0-9]?[0-9]?)', self.__config)))
            thread_pool.add_job((request.version_information, (values['url'] + '/ChangeLog.txt', None, self.__config)))
            thread_pool.add_job((request.version_information, (values['url'] + '/Documentation/ChangeLog', None, self.__config)))
            thread_pool.add_job((request.version_information, (values['url'] + '/CHANGELOG.md', None, self.__config)))
            thread_pool.add_job((request.version_information, (values['url'] + '/ChangeLog', None, self.__config)))
            thread_pool.add_job((request.version_information, (values['url'] + '/doc/manual.sxw', None, self.__config)))
            thread_pool.add_job((request.version_information, (values['url'] + '/doc/manual.pdf', None, self.__config)))
            thread_pool.add_job((request.version_information, (values['url'] + '/doc/manual.odt', None, self.__config)))
        thread_pool.start(self.__config['threads'], version_search=True)

        for version_path in thread_pool.get_result():
            path = version_path[0]
            version = version_path[1]
            name = version_path[0]
            if 'Documentation/' in name:
                name = name[:name.rfind('Documentation/')+1]
            if 'doc/' in name:
                name = name[:name.rfind('doc/')+1] 
            name = name[name.find('ext/')+4:name.rfind('/')]
            found_extensions[name]['version'] = version
            found_extensions[name]['file'] = path
        return found_extensions


    def output(self, extension_dict):
        conn = sqlite3.connect(self.__database)
        c = conn.cursor()
        print('\n\n [+] Extension Information')
        print(' -------------------------')
        json_list = []
        for extension,info in extension_dict.items():
            c.execute('SELECT title,version,state FROM extensions where extensionkey=?', (extension,))
            data = c.fetchone()
            print(Style.BRIGHT + '  [+] {}'.format(Fore.GREEN + extension + Style.RESET_ALL))
            if data is None:
                print('   \u251c Extension ({}) is unknown'.format(extension))
                continue
            print('   \u251c Extension Title: '.ljust(28) + '{}'.format(data[0]))
            print('   \u251c Extension Repo: '.ljust(28) + 'https://extensions.typo3.org/extension/{}'.format(extension))
            print('   \u251c Extension Url: '.ljust(28) + '{}'.format(info['url']))
            if not 'stable' in data[2]:
                print('   \u251c Current Version: '.ljust(28) + '{} ({})'.format(data[1], Fore.RED + data[2] + Style.RESET_ALL))
            else:
                print('   \u251c Current Version: '.ljust(28) + '{} ({})'.format(data[1], data[2]))
            entry = {'Name': extension, 'Title': data[0], 'Repo': 'https://extensions.typo3.org/extension/{}'.format(extension), 'Current': '{} ({})'.format(data[1], data[2]), 'Url': info['url'], 'Version': 'unknown', 'Version File': 'not found', 'Vulnerabilities':[]}
            if info['version']:
                entry.update({'Version': info['version']})
                entry.update({'Version File': info['file']})
                c.execute('SELECT advisory, vulnerability, affected_version_max, affected_version_min FROM extension_vulns WHERE (extensionkey=? AND ?<=affected_version_max AND ?>=affected_version_min)', (extension, info['version'], info['version'],))
                data = c.fetchall()
                print('   \u251c Identified Version: '.ljust(28) + '{}'.format(Style.BRIGHT + Fore.GREEN + info['version'] + Style.RESET_ALL))
                vuln_list = []
                if data:
                    vuln = {}
                    for vulnerability in data:
                        if parse_version(info['version']) <= parse_version(vulnerability[2]):
                            vuln_list.append(Style.BRIGHT + '     [!] {}'.format(Fore.RED + vulnerability[0] + Style.RESET_ALL))
                            vuln_list.append('      \u251c Vulnerability Type: '.ljust(28) + vulnerability[1])
                            vuln_list.append('      \u251c Affected Versions: '.ljust(28) + '{} - {}'.format(vulnerability[2], vulnerability[3]))
                            vuln_list.append('      \u2514 Advisory Url:'.ljust(28) + 'https://typo3.org/security/advisory/{}\n'.format(vulnerability[0].lower()))
                            vuln[vulnerability[0]] = {'Type': vulnerability[1], 'Affected': '{} - {}'.format(vulnerability[2], vulnerability[3]), 'Advisory': 'https://typo3.org/security/advisory/{}'.format(vulnerability[0].lower())}
                    entry.update({'Vulnerabilities': vuln})
                if vuln_list:
                    print('   \u251c Version File: '.ljust(28) + '{}'.format(info['file']))
                    print('   \u2514 Known Vulnerabilities:\n')
                    for vulnerability in vuln_list:
                        print(vulnerability)
                else:
                    print('   \u2514 Version File: '.ljust(28) + '{}'.format(info['file']))
            else:
                print('   \u2514 Identified Version: '.ljust(28) + '-unknown-')
            print()
            json_list.append(entry)
        conn.close()
        return json_list
