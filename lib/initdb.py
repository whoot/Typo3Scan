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
            #c.execute('''DROP TABLE IF EXISTS core_versions''')
            #c.execute('''DROP TABLE IF EXISTS UserAgents''')
            conn.commit()

            # Create table extensions
            c.execute('''CREATE TABLE IF NOT EXISTS extensions
                         (extensionkey text PRIMARY KEY, title text, description text, version text, state text)''')

            # Create table extension_vulns
            c.execute('''CREATE TABLE IF NOT EXISTS extension_vulns
                         (advisory text, extensionkey text, vulnerability text, affected_version_max text, affected_version_min text)''')

            # Create table core_vulns
            c.execute('''CREATE TABLE IF NOT EXISTS core_vulns
                         (advisory text, vulnerability text, subcomponent text, affected_version_max text, affected_version_min text, cve text, severity text)''')

            # Create table core_versions
            #c.execute('''CREATE TABLE IF NOT EXISTS core_versions
            #             (hash text, file text, version text)''')

            # Create table UserAgents
            #c.execute('''CREATE TABLE IF NOT EXISTS UserAgents
            #             (userAgent text)''')
            
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
