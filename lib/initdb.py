#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Typo3 Enumerator - Automatic Typo3 Enumeration Tool
# Copyright (c) 2014-2021 Jan Rude
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
import sqlite3, os.path

class DB_Init:
    """
    This class will empty the database, create tables and insert User-Agents
    """
    def __init__(self):
        database = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'typo3scan.db')
        try:
            conn = sqlite3.connect(database)
            c = conn.cursor()
            
            # Delete all tables
            c.execute('''DROP TABLE IF EXISTS extensions''')
            c.execute('''DROP TABLE IF EXISTS extension_vulns''')
            c.execute('''DROP TABLE IF EXISTS core_vulns''')
            c.execute('''DROP TABLE IF EXISTS core_versions''')
            c.execute('''DROP TABLE IF EXISTS UserAgents''')
            conn.commit()

            # Create table extensions
            c.execute('''CREATE TABLE IF NOT EXISTS extensions
                         (title text, extensionkey text PRIMARY KEY, description text, version text, state text)''')

            # Create table extension_vulns
            c.execute('''CREATE TABLE IF NOT EXISTS extension_vulns
                         (advisory text, extensionkey text, vulnerability text, affected_version_max text, affected_version_min text)''')

            # Create table core_vulns
            c.execute('''CREATE TABLE IF NOT EXISTS core_vulns
                         (advisory text, vulnerability text, subcomponent text, affected_version_max text, affected_version_min text, cve text)''')

            # Create table core_versions
            c.execute('''CREATE TABLE IF NOT EXISTS core_versions
                         (hash text, file text, version text)''')

            # Create table UserAgents
            c.execute('''CREATE TABLE IF NOT EXISTS UserAgents
                         (userAgent text)''')
            conn.commit()

            # add some User-Agents from http://www.useragentstring.com/pages/useragentstring.php
            c.execute('INSERT INTO UserAgents VALUES (?)', ('Mozilla/5.0 (X11; Linux i686; rv:64.0) Gecko/20100101 Firefox/64.0',))
            c.execute('INSERT INTO UserAgents VALUES (?)', ('Mozilla/5.0 (Windows NT 6.1; WOW64; rv:64.0) Gecko/20100101 Firefox/64.0',))
            c.execute('INSERT INTO UserAgents VALUES (?)', ('Mozilla/5.0 (X11; Linux i586; rv:63.0) Gecko/20100101 Firefox/63.0',))
            c.execute('INSERT INTO UserAgents VALUES (?)', ('Mozilla/5.0 (Windows NT 6.2; WOW64; rv:63.0) Gecko/20100101 Firefox/63.0',))
            c.execute('INSERT INTO UserAgents VALUES (?)', ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',))
            c.execute('INSERT INTO UserAgents VALUES (?)', ('Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML like Gecko) Chrome/44.0.2403.155 Safari/537.36',))
            c.execute('INSERT INTO UserAgents VALUES (?)', ('Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',))
            c.execute('INSERT INTO UserAgents VALUES (?)', ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14931',))
            c.execute('INSERT INTO UserAgents VALUES (?)', ('Chrome (AppleWebKit/537.1; Chrome50.0; Windows NT 6.3) AppleWebKit/537.36 (KHTML like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393',))
            c.execute('INSERT INTO UserAgents VALUES (?)', ('Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.9200',))
            c.execute('INSERT INTO UserAgents VALUES (?)', ('Mozilla/5.0 (X11; Linux x86_64; rv:17.0) Gecko/20121202 Firefox/17.0 Iceweasel/17.0.1',))
            c.execute('INSERT INTO UserAgents VALUES (?)', ('Mozilla/5.0 (X11; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1 Iceweasel/15.0.1',))
            c.execute('INSERT INTO UserAgents VALUES (?)', ('Mozilla/5.0 (X11; Linux i686; rv:15.0) Gecko/20100101 Firefox/15.0.1 Iceweasel/15.0.1',))
            c.execute('INSERT INTO UserAgents VALUES (?)', ('Mozilla/5.0 (X11; Linux x86_64; rv:15.0) Gecko/20120724 Debian Iceweasel/15.0',))
            c.execute('INSERT INTO UserAgents VALUES (?)', ('Mozilla/5.0 (X11; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0 Iceweasel/15.0',))
            c.execute('INSERT INTO UserAgents VALUES (?)', ('Opera/9.80 (X11; Linux i686; Ubuntu/14.10) Presto/2.12.388 Version/12.16',))
            c.execute('INSERT INTO UserAgents VALUES (?)', ('Opera/9.80 (Macintosh; Intel Mac OS X 10.14.1) Presto/2.12.388 Version/12.16',))
            c.execute('INSERT INTO UserAgents VALUES (?)', ('Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14',))
            c.execute('INSERT INTO UserAgents VALUES (?)', ('Mozilla/5.0 (Windows NT 6.0; rv:2.0) Gecko/20100101 Firefox/4.0 Opera 12.14',))
            c.execute('INSERT INTO UserAgents VALUES (?)', ('Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0) Opera 12.14',))
            c.execute('INSERT INTO UserAgents VALUES (?)', ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A',))
            c.execute('INSERT INTO UserAgents VALUES (?)', ('Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5355d Safari/8536.25',))
            c.execute('INSERT INTO UserAgents VALUES (?)', ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/537.13+ (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2',))
            conn.commit()

            # add core_versions infos
            c.execute('INSERT INTO core_versions VALUES (?,?,?)', ('e96f099821a3ff61b58ff583a8dac611', '/NEWS.txt', '4.0'))
            c.execute('INSERT INTO core_versions VALUES (?,?,?)', ('f215556dc5952c7cd96a963259b1f846', '/NEWS.txt', '4.1'))
            c.execute('INSERT INTO core_versions VALUES (?,?,?)', ('c24bb9fb057314e8281eb322ce2b933d', '/NEWS.txt', '4.2'))
            c.execute('INSERT INTO core_versions VALUES (?,?,?)', ('8c2b17cc89a518ede434bb052bad04b8', '/typo3/cli_dispatch.phpsh', '4.2'))
            c.execute('INSERT INTO core_versions VALUES (?,?,?)', ('8fafa862e9c9d40b8c441f08fea26bf2', '/NEWS.txt', '4.3'))
            c.execute('INSERT INTO core_versions VALUES (?,?,?)', ('a960d13e6f65122e44972dce58d54efb', '/NEWS.txt', '4.4'))
            c.execute('INSERT INTO core_versions VALUES (?,?,?)', ('1b99e5db8eb075025c905d1cb8fb9b59', '/typo3/sysext/em/res/js/em_repositorylist.js', '4.5'))
            c.execute('INSERT INTO core_versions VALUES (?,?,?)', ('fb5304c15b5284e4d619b3efba7836d1', '/typo3/cli_dispatch.phpsh', '4.6'))
            c.execute('INSERT INTO core_versions VALUES (?,?,?)', ('8cbf762a8445dd5374e018bcaa89f077', '/typo3/sysext/em/res/js/em_repositorylist.js', '4.6'))
            c.execute('INSERT INTO core_versions VALUES (?,?,?)', ('6bf302fe9b4484ec740841aae4992898', '/typo3/sysext/em/res/js/em_repositorylist.js', '4.7'))
            c.execute('INSERT INTO core_versions VALUES (?,?,?)', ('96eb884ba78b3da29ecec89fc7c71f57', '/typo3/cli_dispatch.phpsh', '6.0'))
            c.execute('INSERT INTO core_versions VALUES (?,?,?)', ('890cda3f09ac47cc39ec0d1bb39c5979', '/typo3/cli_dispatch.phpsh', '6.1'))
            c.execute('INSERT INTO core_versions VALUES (?,?,?)', ('fb6a9f8040b36f2218456bb9a98357d1', '/typo3/sysext/belog/composer.json', '7.6'))
            c.execute('INSERT INTO core_versions VALUES (?,?,?)', ('e43e84c986975903fbae13e7912252ed', '/typo3/cli_dispatch.phpsh', '8.7'))
            conn.commit()

        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            print(e)
            exit(-1)

        finally:
            if conn:
                conn.close()
            print('\n[+] Database resetted')
            print('[!] Please update (-u) the database before using Typo3Scan.\n')
