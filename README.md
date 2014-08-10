Typo3-Enumerator
===============

Typo3-Enumerator is an open source penetration testing tool that automates the process of detecting the [Typo3](https://typo3.org) CMS and its installed [extensions](https://typo3.org/extensions/repository/?id=23&L=0&q=&tx_solr[filter][outdated]=outdated%3AshowOutdated) (also the outdated ones!).
If the --top parameter is set to a value, only the specified most downloaded extensions are tested.

It is possible to do all requests through the [TOR Hidden Service](https://www.torproject.org/) network, with the help of [Privoxy](www.privoxy.org), in order to prevent DNS leakage.

Installation
----

You can download the latest tarball by clicking [here](https://github.com/whoot/Typo-Enumerator/tarball/master) or latest zipball by clicking  [here](https://github.com/whoot/Typo-Enumerator/zipball/master).

Preferably, you can download Type-Enumerator by cloning the [Git](https://github.com/whoot/Typo-Enumerator) repository:

    git clone https://github.com/whoot/Typo-Enumerator.git

Typo-Enumerator works with [Python](http://www.python.org/download/) version **2.6.x** and **2.7.x** on Debian/Ubuntu platform.

If you want to use Typo-Enumerator with TOR, you need the [SocksiPy](http://socksipy.sourceforge.net/) module.
On Debian/Ubuntu you can install it with apt-get:

	sudo apt-get install python-socksipy

Usage
----

To get a list of all options use:

    python typoenum.py -h

You can use Typo3-Enumerator with domains:

	python typoenum.py -d DOMAIN [DOMAIN ...] [--user_agent USER-AGENT] [--top VALUE] [-v] [--tor]

Or with a file with a list of domains:

	python typoenum.py -f FILE [--user_agent USER-AGENT] [--top VALUE] [-v] [--tor]

Example:
Test if Typo3 and top 20 downloaded extensions are installed on localhost:

	python typoenum.py -d 127.0.0.1 --top 20

Bug Reporting
----
Bug reports are welcome! Please report all bugs on the [issue tracker](https://github.com/whoot/Typo-Enumerator/issues).

Links
----

* Download: [.tar.gz](https://github.com/whoot/Typo-Enumerator/tarball/master) or [.zip](https://github.com/whoot/Typo-Enumerator/archive/master)
* Changelog: [Here](https://github.com/whoot/Typo-Enumerator/blob/master/doc/CHANGELOG.md)
* TODO: [Here](https://github.com/whoot/Typo-Enumerator/blob/master/doc/TODO.md)
* Issue tracker: https://github.com/whoot/Typo-Enumerator/issues
