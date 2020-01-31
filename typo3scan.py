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

__version__ = '0.6'
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
from colorama import Fore, init, deinit, Style
init(strip=False)

class Typo3:
    def __init__(self):
        self.__domain_list = []
        self.__path = os.path.dirname(os.path.abspath(__file__))
        self.__extensions = []

    def run(self):
        database = os.path.join(self.__path, 'lib', 'typo3scan.db')
        conn = sqlite3.connect(database)
        c = conn.cursor()       
        c.execute('SELECT * FROM UserAgents ORDER BY RANDOM() LIMIT 1;')
        user_agent = c.fetchone()[0]
        c.close()
        config = {'threads': args.threads, 'timeout': args.timeout, 'cookie': args.cookie, 'auth': args.auth, 'User-Agent': user_agent}
        json.dump(config, open(os.path.join(self.__path, 'lib', 'config.json'), 'w'))
        try:
            if args.domain:
                for dom in args.domain:
                    self.__domain_list.append(dom)
            elif args.file:
                if not os.path.isfile(args.file):
                    print(Fore.RED + '\n[x] File not found: {}\n |  Aborting...'.format(args.file) + Fore.RESET)
                    sys.exit(-1)
                else:
                    with open(args.file, 'r') as f:
                        for line in f:
                            self.__domain_list.append(line.strip())

            for domain in self.__domain_list:
                print(Fore.CYAN + Style.BRIGHT + '\n\n[ Checking {} ]\n'.format(domain) + '-'* 73  + Fore.RESET + Style.RESET_ALL)
                check = Domain(domain)
                check.check_root()
                default_files = check.check_default_files()
                if not default_files:
                    check_404 = check.check_404()
                if not check.is_typo3():
                    print(Fore.RED + '\n[x] It seems that Typo3 is not used on this domain\n' + Fore.RESET)
                else:
                    # check for typo3 information
                    print('\n[+] Typo3 Installation')
                    print('----------------------')
                    check.search_login()
                    check.search_typo3_version()

                    # Search extensions
                    print('\n [+] Extension Search')
                    if not self.__extensions:
                        conn = sqlite3.connect(database)
                        c = conn.cursor()
                        if args.vuln:
                            for row in c.execute('SELECT extensionkey FROM extension_vulns'):
                                self.__extensions.append(row[0])
                            self.__extensions = set(self.__extensions)
                        else:
                            for row in c.execute('SELECT extensionkey FROM extensions'):
                                self.__extensions.append(row[0])
                        conn.close()
                    print ('  \u251c Brute-Forcing {} Extensions'.format(len(self.__extensions)))
                    extensions = Extensions()
                    ext_list = extensions.search_extension(check.get_path(), self.__extensions, args.threads)
                    if ext_list:
                        print ('\n  \u251c Found {} extensions'.format(len(ext_list)))
                        print ('  \u251c Brute-Forcing Version Information'.format(len(self.__extensions)))
                        ext_list = extensions.search_ext_version(ext_list, args.threads)
                        extensions.output(ext_list, database)
                    else:
                        print ('\n  [!] No extensions found.\n')
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
                        Default: all
              
    --timeout TIMEOUT   Request Timeout.
                        Default: 10 seconds
              
    --auth USER:PASS    Username and Password for HTTP Basic Authorization.
    
    --cookie NAME=VALUE Can be used for authenticiation based on cookies.
         
    --threads THREADS   The number of threads to use for enumerating extensions.
                        Default: 5

  General:
    -u | --update       Update the database.
    -r | --reset        Reset the database.
""")

    parser = argparse.ArgumentParser(add_help=False)
    group = parser.add_mutually_exclusive_group()
    help = parser.add_mutually_exclusive_group()
    group.add_argument('-f', '--file', dest='file')
    group.add_argument('-d', '--domain', dest='domain', type=str, nargs='+')
    group.add_argument('-u', '--update', dest='update', action='store_true')
    group.add_argument('-r', '--reset', dest='reset', action='store_true')
    parser.add_argument('--vuln', dest='vuln', action='store_true')
    parser.add_argument('--threads', dest='threads', type=int, default=5)
    parser.add_argument('--auth', dest='auth', type=str, default='')
    parser.add_argument('--cookie', dest='cookie', type=str, default='')
    parser.add_argument('--timeout', dest='timeout', type=int, default=10)
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

    else:
        main = Typo3()
        main.run()
