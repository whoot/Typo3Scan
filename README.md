Typo3-Enumerator
===============

Typo3-Enumerator is an open source penetration testing tool that automates the process of detecting the [Typo3](https://typo3.org) CMS and it's installed [extensions](https://typo3.org/extensions/repository/?id=23&L=0&q=&tx_solr[filter][outdated]=outdated%3AshowOutdated) (also the outdated ones).
If the --top parameter is set to a value, only the specified most downloaded extensions are tested.

It is possible to do all requests through the [TOR Hidden Service](https://www.torproject.org/) network.

Installation
----

You can download the latest tarball by clicking [here](https://github.com/whoot/Typo-Enumerator/tarball/master) or latest zipball by clicking  [here](https://github.com/whoot/Typo-Enumerator/zipball/master).

Preferably, you can download Type-Enumerator by cloning the [Git](https://github.com/whoot/Typo-Enumerator) repository:

    git clone https://github.com/whoot/Typo-Enumerator.git

Typo-Enumerator works with [Python](http://www.python.org/download/) version **3.x** on Debian/Ubuntu, RedHat and Windows platforms.

You might need to install following packages:

* [Requests](https://pypi.python.org/pypi/requests/)
* [Colorama](https://pypi.python.org/pypi/colorama)

On Debian/Ubuntu you can install the packages with apt-get:

	apt-get install python3-requests python3-colorama

On Redhat you can install all needed packages with easy_install:

	easy_install argparse
	easy_install requests
	easy_install colorama

If you want to use Typo-Enumerator with TOR, you need the [SocksiPy](https://code.google.com/p/socksipy-branch/) module.

Usage
----

To get a list of all options use:

    python3 typoenum.py -h

You can use Typo3-Enumerator with domains:

	python3 typoenum.py -d DOMAIN [DOMAIN ...] [--top VALUE]

Or with a file with a list of domains:

	python3 typoenum.py -f FILE [--top VALUE]

Example:
Test if Typo3 and top 200 downloaded extensions are installed on 192.168.0.24:

	python3 typoenum.py -d 192.168.0.24/testsite --top 200
	
![ScreenShot](/doc/Screenshot.jpg)

Bug Reporting
----
Bug reports are welcome! Please report all bugs on the [issue tracker](https://github.com/whoot/Typo-Enumerator/issues).

Links
----

* Download: [.tar.gz](https://github.com/whoot/Typo-Enumerator/tarball/master) or [.zip](https://github.com/whoot/Typo-Enumerator/archive/master.zip)
* Changelog: [Here](https://github.com/whoot/Typo-Enumerator/blob/master/doc/CHANGELOG.md)
* TODO: [Here](https://github.com/whoot/Typo-Enumerator/blob/master/doc/TODO.md)
* Issue tracker: [Here](https://github.com/whoot/Typo-Enumerator/issues)

# License

Typo3 Enumerator - Automatic Typo3 Enumeration Tool

Copyright (c) 2015 Jan Rude

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see [http://www.gnu.org/licenses/](http://www.gnu.org/licenses/)