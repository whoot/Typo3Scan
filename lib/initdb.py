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
            c.execute('''DROP TABLE IF EXISTS settings''')
            conn.commit()

            # Create table extensions
            c.execute('''CREATE TABLE IF NOT EXISTS extensions
                         (title text, extensionkey text PRIMARY KEY, description text, version text, state text)''')

            # Create table extension_vulns
            c.execute('''CREATE TABLE IF NOT EXISTS extension_vulns
                         (advisory text, extensionkey text, vulnerability text, branch_max integer, affected_version_max text, branch_max integer, affected_version_min text)''')

            # Create table core_vulns
            c.execute('''CREATE TABLE IF NOT EXISTS core_vulns
                         (advisory text, vulnerability text, subcomponent text, branch_max integer, affected_version_max text, branch_max integer, affected_version_min text, cve text)''')

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

        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            print(e)
            sys.exit(-1)

        finally:
            if conn:
                conn.close()
            print('\n[+] Database resetted')
            print('[!] Please update (-u) the database before using Typo3Scan.\n')
