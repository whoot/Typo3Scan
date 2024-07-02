## version 1.2

* Final release
* Added check for 401 on backend login
* Updated database
* Set to public archive

## Version 1.1.5

* Use python-fake_useragent instead of predefined list in database
* Update database

## Version 1.1.4

* Use rawstrings to avoid warnings in Python 3.12 (thanks @exploide)
* fixed nagative exit codes (thanks @exploide)

## Version 1.1.3

* bugfix: Split basic auth parameter on the first colon only (thanks @c0d3z3r0)
* bugfix: correctly assign version when manual is available
* Add warning for extension version detection
* Database updates

## Version 1.1.2

* Database updates

## Version 1.1.1

* Adapted version regex for extensions

## Version 1.1

* Add severity for core and exention vulns
* Use beautifulsoup to parse html
* Bugfix for version parsing
* Bugfix on detection error
* Remove -r parameter

## Version 1.0.2

* Bugfix for core and extensions advisory URLs

## Version 1.0.1

* json file is now saved each time. --json parameter is now used for specifying path for json file. Default is the current working directory.

## Version 1.0

* Correctly assigning the state for all obsolete extensions
* Adjust version search for extensions
* Small cosmetic changes
* Remove config file

## Version 0.7.3

* Improve database update of extensions

## Version 0.7.2

* JSON output fix

## Version 0.7.1

* Added version detection for Typo3 versions <=11.1.1

## Version 0.7

* Enhanced version detection
* Introduction of *--core* and *--ext* parameter
* Force mode

## Version 0.6.3

* Fixed advisory URLs
* Fixed rootCheck

## Version 0.6.2

* Bugfix in extension vulnerability parsing
* Bugfix on database reset

## Version 0.6.1

* Bugfix of URL determination
* Support for JSON output

## Version 0.6

* Added version regex for composer installations
* Output bugfix

## Version 0.5.2

* Removed 'interesting header' output
* Added output of extension state
* Bugfixes
* Cosmetic output changes

## Version 0.5.1

* Output and version detection fix

## Version 0.5

* Rename to Typo3Scan
* Code cleanup
* Many improvements
* Using database to store extensions, version info and vulnerabilities (Core and Extensions)
* TOR support dropped
* *--top* parameter support dropped. Can not be used anymore, because download counter is not used anymore.
  Instead *--vuln* parameter can be used to check for extensions with known vulnerabilities.

## Version 0.4.5.2

* Fixed error on update
* Fixed version search
* Path to version file(s) is printed
* Support for HTTP Basic Auth is now added (--auth)

## Version 0.4.5.1

* Fixed error on launch when launching from different directory
* IP address restriction for backend login is now shown
* Code cleanup
* Suppress InsecureRequestWarning

## Version 0.4.5

* Version search for Typo3 v8
* Updated Extensions

## Version 0.4.4

* Added support for Typo3 v8
* Clean-up
* Updated extension download URL

## Version 0.4.3

* Added --threads
* Added --user-agent
* Added --timeout
* Added help message (-h, --help)
* No support for privoxy anymore

## Version 0.4.2

* Added new algorithms for Typo3 installation and used path
* Bugfixes

## Version 0.4.1

* Fixed link to socksipy for python 3
* Fixed bug in versionsearch
* Fixed TOR issues
* Bugfixes

## Version 0.4

* Using Python 3 now!
* Using classes and objects
* Better searching algorithm
* Better threading (fixed local network DOS when checking a lot of extensions)
* Clearer output
* Version search for extensions is unreliable and not used atm. Instead a link to the changelog/readme will be given
* Used threads are now always 6

## Version 0.3.3

* Extensions are now saved into different files, separated by state (experimental | alpha | beta | stable | outdated | all). This makes it possible to check more specific ones.

## Version 0.3.2

* Added support for Windows and Red Hat systems

## Version 0.3.1

* It is now possible to check for specific extensions (-e or --extension).
* Domains must be specified with 'http://' or 'https://'.
* Login page redirections can be followed or not.
* Fixed the 'all extensions are installed' bug in the summary when using verbose mode.
* Set sleep between threads to 0.5 to fix time out errors when checking a huge amount of extensions.

## Version 0.3

* Using modules instead of one class
* Accepting now strg+c when in multi-threaded mode
* Update function will now generate a list with extensions instead of an xml. This list is sorted by default (download count). Loading this file is much faster than parsing the xml everytime.
* It is now possible to use only TOR, Privoxy, or TOR with Privoxy (in order to prevent DNS leakage).
* Max. threads are set to 10 to prevent connection issues and DoS, default threads are now 7.
* Connection timeout can be set with '--timeout VALUE'. Default is 20.
* Verbose mode lists also not installed extensions (but trust me, you don´t want to scroll through over 6400 entries).
* Typo3 version search is more accurate
* If the backend login page could not be found, but Typo3 is used, the user is asked, if he want to proceed. This will mostly lead to "no extensions are installed".

## Version 0.2.1

* Fixed some bugs
* It is now possible to specifiy threads.

## Version 0.2

* Added support for Privoxy and TOR
* Version search for extensions is now more reliable

## Version 0.1.6

* Added version search for extensions

## Version 0.1.5

* Added extension search

## Version 0.1.4

* Added support for Typo v6.X

## Version 0.1.3

* Optimized requests

## Version 0.1.2

* Added version guessing

## Version 0.1.1

* Added version search for Typo3

## Version 0.1 

* Prototype
