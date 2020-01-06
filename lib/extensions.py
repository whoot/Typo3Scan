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
from colorama import Fore
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
            thread_pool.add_job((request.version_information, (values['url'] + 'composer.json', '(?:"dev-master":|"version":)\s?"([0-9]+\.[0-9]+\.[0-9x][0-9x]?)')))
            thread_pool.add_job((request.version_information, (values['url'] + 'Index.rst', None)))
            thread_pool.add_job((request.version_information, (values['url'] + 'doc/manual.sxw', None)))
            thread_pool.add_job((request.version_information, (values['url'] + 'ChangeLog', None)))
            thread_pool.add_job((request.version_information, (values['url'] + 'CHANGELOG.md', None)))
            thread_pool.add_job((request.version_information, (values['url'] + 'ChangeLog.txt', None)))
            thread_pool.add_job((request.version_information, (values['url'] + 'Readme.txt', None)))
            thread_pool.add_job((request.version_information, (values['url'] + 'README.md', None)))
            thread_pool.add_job((request.version_information, (values['url'] + 'README.rst', None)))
        
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
        print('\n  |\n [+] Extension information\n  \\')
        for extension,info in extension_dict.items():
            c.execute('SELECT title FROM extensions where extensionkey=?', (extension,))
            title = c.fetchone()[0]
            print('  [+] Name: {}'.format(Fore.GREEN + extension + Fore.RESET))
            print('   \u251c Title: {}'.format(title))
            if info['version']:
                c.execute('SELECT advisory, vulnerability, affected_version_max, affected_version_min FROM extension_vulns WHERE (extensionkey=? AND ?<=affected_version_max AND ?>=affected_version_min)', (extension, info['version'], info['version'],))
                data = c.fetchall()
                print('   \u251c Version: {}'.format(Fore.GREEN + info['version'] + Fore.RESET))
                if data:
                    print('   \u251c see: {}'.format(info['file']))
                    print('   \u2514 Known vulnerabilities\n      \\')
                    for vuln in data:
                        if parse_version(info['version']) <= parse_version(vuln[2]):
                            print('     [!] {}'.format(Fore.RED + vuln[0] + Fore.RESET))
                            print('      \u251c Vulnerability Type:'.ljust(29), vuln[1])
                            print('      \u2514 Affected Versions:'.ljust(29), '{} - {}'.format(vuln[2], vuln[3]))
                else:
                    print('   \u2514 see: {}'.format(info['file']))
            else:
            	print('   \u2514 Version: -unknown-')
            print()
        conn.close()