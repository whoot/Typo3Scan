#!/usr/bin/env python
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

import os.path
from pkg_resources import parse_version
import xml.etree.ElementTree as ElementTree
import re, os, sys, gzip, urllib.request, sqlite3, requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

database = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'typo3scan.db')
conn = sqlite3.connect(database)
c = conn.cursor()

class Update:
    """
    This class updates the extension and vulnerability database

    It will download the extension file from the official repository, 
    unpack it and insert the extensions in the database.
    Vulnerabilities will be parsed from the official homepage.
    """
    def __init__(self):
        self.load_core_vulns()
        self.download_ext()
        self.load_extensions()
        self.load_extension_vulns()

    def load_core_vulns(self):
        """
            Grep the CORE vulnerabilities from the security advisory website
            
            Search for advisories and maximum pages
            Request every advisory and get:
                Advisory Title
                Vulnerability Type
                Subcomponent(s)
                Affected Versions
                CVE Numbers
        """
        print('\n[+] Searching for new CORE vulnerabilities...')
        update_counter = 0
        response = requests.get('https://typo3.org/help/security-advisories/typo3-cms/page-1')
        pages = re.findall('<a class=\"page-link\" href=\"/help/security-advisories/typo3-cms/page-([0-9]+)\">', response.text)
        last_page = int(pages[-1])

        for current_page in range(1, last_page+1):
            print(' \u251c Page {}/{}'.format(current_page, last_page))
            response = requests.get('https://typo3.org/help/security-advisories/typo3-cms/page-{}'.format(current_page), timeout=6)
            advisories = re.findall('TYPO3-CORE-SA-[0-9][0-9][0-9][0-9]-[0-9][0-9][0-9]', response.text)
            for advisory in advisories:
                vulnerabilities = []
                affected_version_max = '0.0.0' 
                affected_version_min = '0.0.0'
                html = requests.get('https://typo3.org/security/advisory/{}'.format(advisory.lower()))
                beauty_html = html.text
                beauty_html = beauty_html[beauty_html.index('Component Type'):]
                beauty_html = beauty_html[:beauty_html.index('General ')]
                beauty_html = beauty_html.replace('\xa0', ' ')
                beauty_html = beauty_html.replace('</strong>', '')
                beauty_html = beauty_html.replace('&nbsp;', ' ')
                beauty_html = beauty_html.replace('&amp;', '&')

                # set as global versions
                advisory_items = {}
                subcomponents = re.findall('([sS]ubcomponent\s?#?[0-9]?:\s?(.*?))<', beauty_html)
                # if no subcomponent / CORE vuln
                if len(subcomponents) == 0:
                    missed = re.search('Component Type:\s?(.*?)<', beauty_html).group(1)
                    advisory_items[missed] = []
                    advisory_items[missed].append(beauty_html)
                subcomponents.reverse()
                try:
                    for subcomponent in subcomponents:
                        index = beauty_html.rfind(subcomponent[0])
                        item_text = subcomponent[1]
                        if item_text in advisory_items:
                            item_text = item_text + ' (2)'
                        advisory_items[item_text] = []
                        advisory_items[item_text].append(beauty_html[index:])
                        beauty_html = beauty_html[:index]

                    for subcomponent, entry in advisory_items.items():
                        vulnerability_items = {}
                        vulnerability_type = re.findall('(Vulnerability Type:\s?(.*?)<)', entry[0])
                        vulnerability_type.reverse()
                        for type_entry in vulnerability_type:
                            index = entry[0].rfind(type_entry[0])
                            vulnerability_items[type_entry[1]] = []
                            vulnerability_items[type_entry[1]].append(entry[0][index:])
                            entry[0] = entry[0][:index]

                        for vuln_type, vuln_description in vulnerability_items.items():
                            cve = re.search(':\s?(CVE-.*?)(<|\"|\()', vuln_description[0])
                            if cve:
                                cve = cve.group(1)
                            else:
                                cve = 'None assigned'
                            search_affected = re.search('Affected Version[s]?:\s?(.+?)<', vuln_description[0])
                            if search_affected:
                                affected_versions = search_affected.group(1)
                            else:
                                affected_versions = re.search('Affected Version[s]?:\s?(.+?)<', beauty_html).group(1)
                            # separate versions
                            affected_versions = affected_versions.replace("and below", " - 0.0.0")
                            affected_versions = affected_versions.replace(";", ",")
                            affected_versions = affected_versions.replace(' and', ',')
                            versions = affected_versions.split(', ')
                            for version in versions:
                                version = re.findall('([0-9]+\.[0-9x]+\.?[0-9x]?[0-9x]?)', version)
                                if len(version) == 0:
                                    print("[!] Unknown version info! Skipping...")
                                    print(" \u251c Advisory:", advisory)
                                    print(" \u251c Subcomponent:", subcomponent)
                                    print(" \u251c Vulnerability:", vuln_type)
                                    print(" \u251c Versions:", affected_versions)
                                    break
                                elif len(version) == 1:
                                    version = version[0]
                                    if len(version) == 3: # e.g. version 6.2
                                        version = version + '.0'
                                    affected_version_max = version
                                    affected_version_min = version
                                else:
                                    if parse_version(version[0]) >= parse_version(version[1]):
                                        affected_version_max = version[0]
                                        affected_version_min = version[1]
                                    else:
                                        affected_version_max = version[1]
                                        affected_version_min = version[0]
                                # add vulnerability
                                vulnerabilities.append([advisory, vuln_type, subcomponent, affected_version_max, affected_version_min, cve])
                except Exception as e:
                    print("Error on receiving data for https://typo3.org/security/security-advisory/{}".format(advisory))
                    print(e)
                    exit(-1)

                # Add vulnerability details to database
                for core_vuln in vulnerabilities:
                    c.execute('SELECT * FROM core_vulns WHERE advisory=? AND vulnerability=? AND subcomponent=? AND affected_version_max=? AND affected_version_min=? AND cve=?', (core_vuln[0], core_vuln[1], core_vuln[2], core_vuln[3], core_vuln[4], core_vuln[5],))
                    data = c.fetchall()
                    if not data:
                        update_counter+=1
                        c.execute('INSERT INTO core_vulns VALUES (?,?,?,?,?,?)', (core_vuln[0], core_vuln[1], core_vuln[2], core_vuln[3], core_vuln[4], core_vuln[5]))
                        conn.commit()
                    else:
                        if update_counter == 0:
                            print('[!] Already up-to-date.\n')
                        else:
                            print(' \u2514 Done. Added {} new CORE vulnerabilities to database.\n'.format(update_counter))
                        return True

    def dlProgress(self, count, blockSize, totalSize):
        """
            Progressbar for extension download
        """
        percent = int(count*blockSize*100/totalSize)
        sys.stdout.write('\r \u251c Downloading ' + '%d%%' % percent)
        sys.stdout.flush()

    def download_ext(self):
        """
            Download extensions from server and unpack the ZIP
        """
        print('[+] Getting extension file...')
        try:
            # Maybe someday we need to use mirrors: https://repositories.typo3.org/mirrors.xml.gz
            urllib.request.urlretrieve('https://typo3.org/fileadmin/ter/extensions.xml.gz', 'extensions.xml.gz', reporthook=self.dlProgress)
            with gzip.open('extensions.xml.gz', 'rb') as infile:
                with open('extensions.xml', 'wb') as outfile:
                    for line in infile:
                        outfile.write(line)
            infile.close()
            outfile.close()
        except Exception as e:
            print('\n', e)

    def load_extensions(self):
        """
            Parse the extension file and add extensions in database
        """
        print('\n \u251c Parsing extension file...')
        tree = ElementTree.parse('extensions.xml') 
        root = tree.getroot()

        c.execute('''DROP TABLE IF EXISTS extensions''')
        c.execute('''CREATE TABLE IF NOT EXISTS extensions (extensionkey text PRIMARY KEY, title text, description text, version text, state text)''')

        # for every extension get:
        #     title, extensionkey, description, version, state
        counter = 0
        for extensions in root:
            extensionkey = extensions.get('extensionkey').lower()
            if (extensionkey == 'aaaaa'):
                continue
            title = extensions[1][0].text
            description = extensions[1][1].text
            version = '0.0.0'
            state = extensions[1][2].text

            # search for current version
            for extension in extensions.iter('version'):
                if not(extension.attrib['version'] == ''):
                    try:
                        temp_ver=((extension.attrib['version']).split('-')[0]).strip()
                        if parse_version(temp_ver) > parse_version(version):
                            title = (extension.find('title')).text
                            description = (extension.find('description')).text
                            version = extension.attrib['version']
                            if ((extension.find('ownerusername').text == 'abandoned_extensions') or (extension.find('state').text == 'n/a') or (extension.find('state').text == 'test')):
                                state = 'obsolete'
                            else:
                                state = (extension.find('state')).text
                    except ValueError:
                        pass
            c.execute('INSERT OR REPLACE INTO extensions VALUES (?,?,?,?,?)', (extensionkey, title, description, version, state))
            counter += 1
        conn.commit()
        os.remove('extensions.xml.gz')
        os.remove('extensions.xml')
        print(' \u2514 Done. Added {} extensions to database'.format(counter))

    def load_extension_vulns(self):
        """
            Grep the EXTENSION vulnerabilities from the security advisory website
            
            Search for advisories and maximum pages
            Request every advisory and get:
                Advisory Title
                Extension Name
                Vulnerability Type
                Affected Versions
        """
        print('\n[+] Searching for new extension vulnerabilities...')
        update_counter = 0
        response = requests.get('https://typo3.org/help/security-advisories/typo3-extensions/page-1')
        pages = re.findall('<a class=\"page-link\" href=\"/help/security-advisories/typo3-extensions/page-([0-9]+)\">', response.text)
        last_page = int(pages[-1])

        for current_page in range(1, last_page+1):
            print(' \u251c Page {}/{}'.format(current_page, last_page))
            response = requests.get('https://typo3.org/help/security-advisories/typo3-extensions/page-{}'.format(current_page), timeout=6)
            advisories = re.findall('TYPO3-EXT-SA-[0-9][0-9][0-9][0-9]-[0-9][0-9][0-9]', response.text)
            for advisory in advisories:
                vulnerabilities = []
                affected_version_max = '0.0.0' 
                affected_version_min = '0.0.0'
                # adding vulns with odd stuff on website
                if advisory == 'TYPO3-EXT-SA-2014-018':
                    vulnerabilities.append(['TYPO3-EXT-SA-2014-018', 'phpmyadmin', 'Cross-Site Scripting, Denial of Service, Local File Inclusion', '4.18.4', '4.18.0'])
                elif advisory == 'TYPO3-EXT-SA-2014-015':
                    vulnerabilities.append(['TYPO3-EXT-SA-2014-015', 'dce', 'Information Disclosure', '0.11.4', '0.0.0'])
                elif advisory == 'TYPO3-EXT-SA-2014-013':
                    vulnerabilities.append(['TYPO3-EXT-SA-2014-013', 'cal', 'Denial of Service', '1.5.8', '0.0.0'])
                    vulnerabilities.append(['TYPO3-EXT-SA-2014-013', 'cal', 'Denial of Service', '1.6.0', '1.6.0'])
                elif advisory == 'TYPO3-EXT-SA-2014-009':
                    vulnerabilities.append(['TYPO3-EXT-SA-2014-009', 'news', 'Cross-Site Scripting', '3.0.0', '3.0.0'])
                    vulnerabilities.append(['TYPO3-EXT-SA-2014-009', 'news', 'Cross-Site Scripting', '2.3.0', '2.0.0'])
                else:
                    try:
                        html = requests.get('https://typo3.org/security/advisory/{}'.format(advisory.lower()))
                        beauty_html = html.text.replace('\xa0', ' ')
                        beauty_html = beauty_html.replace('</strong>', '')
                        beauty_html = beauty_html.replace('&nbsp;', ' ')
                        beauty_html = beauty_html.replace('&amp;', '&')
                        advisory_info = re.search('<title>(.*)</title>', beauty_html).group(1)
                        vulnerability = re.findall('Vulnerability Type[s]?:\s?(.*?)<', beauty_html)
                        affected_versions = re.findall('Affected Version[s]?:\s?(.+?)<', beauty_html)
                        extensionkey = re.findall('Extension[s]?:\s?(.*?)<', beauty_html)
                        # Sometimes there are multiple extensions in an advisory
                        if len(extensionkey) == 0: # If only one extension affected
                            if not '(' in advisory_info:
                                extensionkey = [advisory_info[advisory_info.rfind(' ')+1:]]
                            else:
                                extensionkey = [advisory_info[advisory_info.find('('):]]
                        for item in range (0, len(extensionkey)):
                            extensionkey_item = extensionkey[item]
                            if '(' in extensionkey_item:
                                extensionkey_item = extensionkey_item[extensionkey_item.rfind('(')+1:extensionkey_item.rfind(')')]
                            description = vulnerability[item]
                            version_item = affected_versions[item]
                            version_item = version_item.replace("and all versions below", "- 0.0.0")
                            version_item = version_item.replace("and all version below", "- 0.0.0") # typo
                            version_item = version_item.replace("and alll versions below", "- 0.0.0") # typo
                            version_item = version_item.replace("and below of", "-")
                            version_item = version_item.replace("and below", "- 0.0.0")
                            version_item = version_item.replace("&nbsp;", " ")
                            version_item = version_item.replace(";", ",")
                            version_item = version_item.replace(' and', ',')
                            versions = version_item.split(', ')
                            for version in versions:
                                version = re.findall('([0-9]+\.[0-9x]+\.[0-9x]+)', version)
                                if len(version) == 1:
                                    affected_version_max = version[0]
                                    affected_version_min = version[0]
                                else:
                                    if parse_version(version[0]) >= parse_version(version[1]):
                                        affected_version_max = version[0]
                                        affected_version_min = version[1]
                                    else:
                                        affected_version_max = version[1]
                                        affected_version_min = version[0]
                                vulnerabilities.append([advisory, extensionkey_item, description, affected_version_max, affected_version_min])
                    except Exception as e:
                        print("Error on receiving data for https://typo3.org/security/advisory/{}".format(advisory))
                        print(e)
                        exit(-1)

                # Add vulnerability details to database
                for ext_vuln in vulnerabilities:
                    c.execute('SELECT * FROM extension_vulns WHERE advisory=? AND extensionkey=? AND vulnerability=? AND affected_version_max=? AND affected_version_min=?', (ext_vuln[0], ext_vuln[1], ext_vuln[2], ext_vuln[3], ext_vuln[4],))
                    data = c.fetchall()
                    if not data:
                        update_counter+=1
                        c.execute('INSERT INTO extension_vulns VALUES (?,?,?,?,?)', (ext_vuln[0], ext_vuln[1], ext_vuln[2], ext_vuln[3], ext_vuln[4]))
                        conn.commit()
                    else:
                        if update_counter == 0:
                            print('[!] Already up-to-date.\n')
                        else:
                            print(' \u2514 Done. Added {} new EXTENSION vulnerabilities to database.\n'.format(update_counter))
                        return True
