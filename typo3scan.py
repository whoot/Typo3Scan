#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Typo3Scan - Automatic Typo3 Enumeration Tool
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

__version__ = '1.0.2'
__program__ = 'Typo3Scan'
__description__ = 'Automatic Typo3 enumeration tool'
__author__ = 'https://github.com/whoot'

import sys
import json
import sqlite3
import os.path
import argparse
from lib.domain import Domain
from lib.extensions import Extensions
from pkg_resources import parse_version
from colorama import Fore, init, deinit, Style
init(strip=False)

class Typo3:
    def __init__(self, domain_list, threads, timeout, cookie, basic_auth, user_agent, json_out, force, vuln, no_interaction):
        self.__database = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib', 'typo3scan.db')
        self.__extensions = []
        self.__domain_list = domain_list
        if json_out.endswith('/'):
            self.__json = json_out + 'typo3scan.json'
        elif json_out.endswith('.json'):
            self.__json = json_out
        else:
            self.__json = json_out + '/typo3scan.json'
        self.__json_log = {}
        self.__force = force
        self.__vuln = vuln
        if not user_agent:
            conn = sqlite3.connect(self.__database)
            c = conn.cursor()       
            c.execute('SELECT * FROM UserAgents ORDER BY RANDOM() LIMIT 1;')
            user_agent = c.fetchone()[0]
            c.close()
        self.__custom_headers = {'User-Agent' : user_agent}
        self.__cookies = {}
        if cookie:
            name = cookie.split('=')[0]
            value = cookie.split('=')[1]
            self.__cookies = {name: value}
        self.__basic_auth = False
        if basic_auth:
            self.__basic_auth = (basic_auth.split(':')[0], basic_auth.split(':')[1])
        self.__config = {'threads': threads, 'timeout': timeout, 'auth': self.__basic_auth, 'cookies': self.__cookies, 'headers': self.__custom_headers, 'no_interaction': no_interaction}

    def run(self):
        try:
            for domain in self.__domain_list:
                print(Fore.CYAN + Style.BRIGHT + '\n\n[ Checking {} ]\n'.format(domain) + '-'* 73  + Fore.RESET + Style.RESET_ALL)
                check = Domain(domain, self.__config)
                root = check.check_root()
                if not root:
                    check_404 = check.check_404()
                if not check.is_typo3() and self.__force is False:
                    print(Fore.RED + '\n[x] It seems that Typo3 is not used on this domain\n' + Fore.RESET)
                else:
                    # check for typo3 information
                    print('\n [+] Core Information')
                    print(' --------------------')
                    check.search_login()
                    check.search_typo3_version()

                    # Search extensions
                    print('\n [+] Extension Search')
                    if not self.__extensions:
                        conn = sqlite3.connect(self.__database)
                        c = conn.cursor()
                        if self.__vuln:
                            for row in c.execute('SELECT extensionkey FROM extension_vulns'):
                                self.__extensions.append(row[0])
                            self.__extensions = set(self.__extensions)
                        else:
                            for row in c.execute('SELECT extensionkey FROM extensions'):
                                self.__extensions.append(row[0])
                        conn.close()
                    print ('  \u251c Brute-Forcing {} Extensions'.format(len(self.__extensions)))
                    extensions = Extensions(check.get_path(), self.__extensions, self.__config)
                    ext_list = extensions.search_extension()
                    json_ext = []
                    if ext_list:
                        print ('\n  \u251c Found {} extensions'.format(len(ext_list)))
                        print ('  \u251c Brute-Forcing Version Information'.format(len(self.__extensions)))
                        ext_list = extensions.search_ext_version(ext_list)
                        json_ext = extensions.output(ext_list)
                    else:
                        print ('\n [!] No extensions found.\n')
                    self.__json_log[domain] = {'Backend': check.get_backend(), 'Version': check.get_typo3_version(), 'Vulnerabilities':check.get_typo3_vulns(), 'Extensions': json_ext}
            if self.__json:
                json.dump(self.__json_log, open(self.__json, 'w'))
        except KeyboardInterrupt:
            print('\nReceived keyboard interrupt.\nQuitting...')
            exit(-1)
        finally:
            deinit()
        
if __name__ == '__main__':
    print('\n' + 73*'=' + Style.BRIGHT)
    print(Fore.CYAN)
    print('________                   ________   _________                     '.center(73))
    print('\_    _/__ __ ______  _____\_____  \ /   _____/ ____ _____    ___  '.center(73))
    print('  |  | |  |  |\____ \|  _  | _(__  < \_____  \_/ ___\\\\__  \  /   \ '.center(73))
    print('  |  | |___  ||  |_) | (_) |/       \/        \  \___ / __ \|  |  \ '.center(73))
    print('  |__| / ____||   __/|_____|________/_________/\_____|_____/|__|__/ '.center(73))
    print('       \/     |__|                                                  '.center(73))
    print(Fore.RESET + Style.RESET_ALL)
    print(__description__.center(73))
    print(('Version ' + __version__).center(73))
    print((__author__).center(73))
    print(73*'=')    

    def print_help():
        print(
"""\nUsage: python typo3scan.py [options]

Options:
  -h, --help         Show this help message and exit.

  Target:
   At least one of these options has to be provided to define the target(s):

    --domain | -d <target url>  The Typo3 URL(s)/domain(s) to scan.
    --file   | -f <file>        Parse targets from file (one domain per line).


  Optional:
   You dont need to specify this arguments, but you may want to

    --vuln              Check for extensions with known vulnerabilities only.
              
    --timeout TIMEOUT   Request Timeout.
                        Default: 10 seconds
              
    --auth USER:PASS    Username and Password for HTTP Basic Authorization.
    
    --cookie NAME=VALUE Can be used for authenticiation based on cookies.

    --agent USER-AGENT  Set custom User-Agent for requests.
         
    --threads THREADS   The number of threads to use for enumerating extensions.
                        Default: 5

    --json PATH         Path for json output file.
                        Default: current working directory

    --force             Force enumeration.

    --no-interaction    Do not ask any interactive question.

  General:
    -u | --update       Update extensions and vulnerability database.
    -r | --reset        Reset the database.
    --core VERSION      Show all known vulnerabilities for given Typo3 version.
    --ext EXT:VERSION   Show all known vulnerabilities for given extension and version.
""")

    parser = argparse.ArgumentParser(add_help=False)
    group = parser.add_mutually_exclusive_group()
    help = parser.add_mutually_exclusive_group()
    group.add_argument('-f', '--file', dest='file')
    group.add_argument('-d', '--domain', dest='domain', type=str, nargs='+')
    group.add_argument('-u', '--update', dest='update', action='store_true')
    group.add_argument('-r', '--reset', dest='reset', action='store_true')
    group.add_argument('--core', dest='core', type=str)
    group.add_argument('--ext', dest='extension', type=str)
    parser.add_argument('--force', dest='force', action='store_true')
    parser.add_argument('--vuln', dest='vuln', action='store_true')
    parser.add_argument('--threads', dest='threads', type=int, default=5)
    parser.add_argument('--auth', dest='basic_auth', type=str, default='')
    parser.add_argument('--cookie', dest='cookie', type=str, default='')
    parser.add_argument('--agent', dest='user_agent', type=str, default='')
    parser.add_argument('--timeout', dest='timeout', type=int, default=10)
    parser.add_argument('--json', dest='json', type=str, default=os.path.join(os.getcwd(), 'typo3scan.json'))
    parser.add_argument('--no-interaction', dest='no_interaction', action='store_true')
    
    help.add_argument( '-h', '--help', action='store_true')
    args = parser.parse_args()

    if args.help or not len(sys.argv) > 1:
        print_help()

    elif args.reset:
        from lib.initdb import DB_Init
        DB_Init()

    elif args.update:
        from lib.update import Update
        Update()

    elif args.core:
        database = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib', 'typo3scan.db')
        conn = sqlite3.connect('lib/typo3scan.db')
        c = conn.cursor()
        c.execute('SELECT advisory, vulnerability, subcomponent, affected_version_max, affected_version_min FROM core_vulns WHERE (?<=affected_version_max AND ?>=affected_version_min)', (args.core, args.core,)) 
        data = c.fetchall()
        json_list = {}
        if data:
            for vulnerability in data:
                if parse_version(args.core) <= parse_version(vulnerability[3]):
                    json_list[vulnerability[0]] = {'Type': vulnerability[1], 'Subcomponent': vulnerability[2], 'Affected': '{} - {}'.format(vulnerability[3], vulnerability[4]), 'Advisory': 'https://typo3.org/security/advisory/{}'.format(vulnerability[0].lower())}
            if json_list:
                print(Style.BRIGHT + '\n[+] Known Vulnerabilities for Typo3 v{}\n'.format(args.core) + Style.RESET_ALL)
                for vulnerability in json_list.keys():
                    print(Style.BRIGHT + '   [!] {}'.format(Fore.RED + vulnerability + Style.RESET_ALL))
                    print('    \u251c Vulnerability Type:'.ljust(28) + json_list[vulnerability]['Type'])
                    print('    \u251c Subcomponent:'.ljust(28) + json_list[vulnerability]['Subcomponent'])
                    print('    \u251c Affected Versions:'.ljust(28) + json_list[vulnerability]['Affected'])
                    print('    \u2514 Advisory URL:'.ljust(28) + json_list[vulnerability]['Advisory'] + '\n')
        if not json_list:
            print('\n' + Fore.GREEN + Style.BRIGHT + '[+] Typo3 v{} has no known vulnerabilities\n'.format(args.core) + Style.RESET_ALL)

    elif args.extension:
        database = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib', 'typo3scan.db')
        conn = sqlite3.connect('lib/typo3scan.db')
        c = conn.cursor()
        name = ''
        version = ''
        if not ':' in args.extension:
            name = args.extension
            version = '0.0.0'
        else:
            name = (args.extension).split(':')[0]
            version = (args.extension).split(':')[1]
        
        c.execute('SELECT ROWID FROM extensions WHERE extensionkey=?', (name,))
        data = c.fetchall()
        if (len(data) == 0):
            print('\n' + Fore.RED + Style.BRIGHT + '[!] Extension \'{}\' does not exist\n'.format(name) + Style.RESET_ALL)
            sys.exit(-1)
        else:
            c.execute('SELECT advisory, vulnerability, affected_version_max, affected_version_min FROM extension_vulns WHERE (extensionkey=? AND ?<=affected_version_max AND ?>=affected_version_min)', (name, version, version,))
            data = c.fetchall()
        json_list = {}
        if data:
            for vulnerability in data:
                if parse_version(version) <= parse_version(vulnerability[2]):
                    json_list[vulnerability[0]] = {'Type': vulnerability[1], 'Affected': '{} - {}'.format(vulnerability[2], vulnerability[3]), 'Advisory': 'https://typo3.org/security/advisory/{}'.format(vulnerability[0].lower())}
            if json_list:
                if version == '0.0.0':
                    print(Style.BRIGHT + '\n[+] Known vulnerabilities for \'{}\'\n'.format(name) + Style.RESET_ALL)
                else:
                    print(Style.BRIGHT + '\n[+] Known vulnerabilities for \'{}\' v{}\n'.format(name, version) + Style.RESET_ALL)
                for vulnerability in json_list.keys():
                    print(Style.BRIGHT + '   [!] {}'.format(Fore.RED + vulnerability + Style.RESET_ALL))
                    print('    \u251c Vulnerability Type: '.ljust(28) + json_list[vulnerability]['Type'])
                    print('    \u251c Affected Versions: '.ljust(28) + '{}'.format(json_list[vulnerability]['Affected']))
                    print('    \u2514 Advisory URL:'.ljust(28) + '{}\n'.format(json_list[vulnerability]['Advisory'].lower()))
        if not json_list:
            print('\n' + Fore.GREEN + Style.BRIGHT + '[+] \'{}\' v{} has no known vulnerabilities\n'.format(name, version) + Style.RESET_ALL)

    else:
        if args.force:
           print('\n' + Fore.RED + Style.BRIGHT + '!! FORCE MODE ENABLED !!'.center(73))
           print('!! Expect False Positives !!'.center(73) + Style.RESET_ALL)
        
        domain_list = list()
        if args.domain:
            for dom in args.domain:
                domain_list.append(dom)
        elif args.file:
            if not os.path.isfile(args.file):
                print(Fore.RED + '\n[x] File not found: {}\n |  Aborting...'.format(args.file) + Fore.RESET)
                sys.exit(-1)
            else:
                with open(args.file, 'r') as f:
                    for line in f:
                        domain_list.append(line.strip())

        main = Typo3(domain_list, args.threads, args.timeout, args.cookie, args.basic_auth, args.user_agent, args.json, args.force, args.vuln, args.no_interaction)
        main.run()
