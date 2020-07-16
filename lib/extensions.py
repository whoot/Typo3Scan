#!/usr/bin/env python3
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

import sqlite3
from colorama import Fore, Style
import lib.request as request
from lib.thread_pool import ThreadPool
from pkg_resources import parse_version

class Extensions:
    """
    Extension class
    """
    def __init__(self):
        pass

    def search_extension(self, domain, extensions, threads):
        """
            This method loads the extensions from the database and searches for installed extensions.
                /typo3conf/ext/:        Local installation path. This is where extensions usually get installed.
                /typo3/ext/:            Global installation path (not used atm)
                /typo3/sysext/:         Extensions shipped with core
        """
        found_extensions = {}
        thread_pool = ThreadPool()
        for ext in extensions:
            thread_pool.add_job((request.head_request, ('{}/typo3conf/ext/{}/'.format(domain, ext))))
            thread_pool.add_job((request.head_request, ('{}/typo3/sysext/{}/'.format(domain, ext))))
            #thread_pool.add_job((request.head_request, ('{}/typo3/ext/{}/'.format(domain, ext))))
        thread_pool.start(threads)

        for installed_extension in thread_pool.get_result():
            name = installed_extension[1][:-1]
            name = name[name.rfind('/')+1:]
            found_extensions[name] = {'url':installed_extension[1], 'version': None, 'file': None}
        return found_extensions

    def search_ext_version(self, found_extensions, threads):
        """
            This method adds a job for every installed extension.
            The goal is to find a file with version information.
        """
        thread_pool = ThreadPool()
        for extension,values in found_extensions.items():
            thread_pool.add_job((request.version_information, (values['url'] + 'Documentation/ChangeLog/Index.rst', None)))
            thread_pool.add_job((request.version_information, (values['url'] + 'Documentation/Changelog/Index.rst', None)))
            thread_pool.add_job((request.version_information, (values['url'] + 'Documentation/Settings.cfg', None)))
            thread_pool.add_job((request.version_information, (values['url'] + 'Documentation/Settings.yml', '(?:release:)\s?([0-9]+\.[0-9]+\.?[0-9]?[0-9]?)')))
            thread_pool.add_job((request.version_information, (values['url'] + 'Settings.yml', '(?:release:)\s?([0-9]+\.[0-9]+\.?[0-9]?[0-9]?)')))
            thread_pool.add_job((request.version_information, (values['url'] + 'Documentation/ChangeLog', None)))
            thread_pool.add_job((request.version_information, (values['url'] + 'Documentation/Index.rst', None)))
            thread_pool.add_job((request.version_information, (values['url'] + 'composer.json', '(?:"dev-master":|"version":)\s?"([0-9]+\.[0-9]+\.?[0-9x]?[0-9x]?)')))
            thread_pool.add_job((request.version_information, (values['url'] + 'Index.rst', None)))
            thread_pool.add_job((request.version_information, (values['url'] + 'doc/manual.sxw', None)))
            thread_pool.add_job((request.version_information, (values['url'] + 'ChangeLog', None)))
            thread_pool.add_job((request.version_information, (values['url'] + 'CHANGELOG.md', None)))
            thread_pool.add_job((request.version_information, (values['url'] + 'ChangeLog.txt', None)))
        
        thread_pool.start(threads, version_search=True)

        for version_path in thread_pool.get_result():
            path = version_path[0][0]
            version = version_path[1]
            name = version_path[0][0]
            if 'Documentation/' in name:
                name = name[:name.rfind('Documentation/')+1]
            if 'doc/' in name:
                name = name[:name.rfind('doc/')+1] 
            name = name[name.find('ext/')+4:name.rfind('/')]
            found_extensions[name]['version'] = version
            found_extensions[name]['file'] = path
        return found_extensions


    def output(self, extension_dict, database):
        conn = sqlite3.connect(database)
        c = conn.cursor()
        print('\n\n [+] Extension Information')
        print(' -------------------------')
        json_list = {}
        for extension,info in extension_dict.items():
            c.execute('SELECT title,version,state FROM extensions where extensionkey=?', (extension,))
            data = c.fetchone()
            print(Style.BRIGHT + '  [+] {}'.format(Fore.GREEN  + extension + Style.RESET_ALL))
            if data is None:
                print('   \u251c Extension ({}) is unknown'.format(extension))
                continue
            print('   \u251c Extension Title: '.ljust(28) + '{}'.format(data[0]))
            print('   \u251c Extension Repo: '.ljust(28) + 'https://extensions.typo3.org/extension/{}'.format(extension))
            print('   \u251c Current Version: '.ljust(28) + '{} ({})'.format(data[1], data[2]))
            json_list[extension] = {'Title': data[0], 'Repo': 'https://extensions.typo3.org/extension/{}'.format(extension), 'Current': '{} ({})'.format(data[1], data[2]), 'Version': '', 'Vulnerabilities':''}
            if info['version']:
                json_list[extension].update(Version = info['version'])
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
                            vuln_list.append('      \u2514 Advisory URL:'.ljust(28) + 'https://typo3.org/security/advisory/{}\n'.format(vulnerability[0].lower()))
                            vuln[vulnerability[0]] = {'Type': vulnerability[1], 'Affected': '{} - {}'.format(vulnerability[2], vulnerability[3]), 'Advisory': 'https://typo3.org/security/advisory/{}'.format(vulnerability[0].lower())}
                    json_list[extension].update(Vulnerabilities = vuln)
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
        conn.close()
        return json_list
