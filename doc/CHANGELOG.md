## Version 0.4

* Using Python 3.x now!
* Using classes and objects
* Better searching algorithm
* Better threading (fixed local network DOS when cheking a lot of extensions)
* Clearer output

## Version 0.3.3

* Extensions are now saved into different files, separated by state (experimental | alpha | beta | stable | outdated | all). This makes it possible to check more specific ones.
* Colorama is only used if installed. It doesn't need to be installed anymore.
* Installed extensions are shown immediately

## Version 0.3.2

* Added support for Windows and Red Hat systems

## Version 0.3.1

* It is now possible to check for specific extensions (-e or --extension).
* Domains must be specified with 'http://' or 'https://' (for example: https://127.0.0.1).
* Login page redirections can be followed or not.
* Fixed the 'all extensions are installed' bug in the summary when using verbose mode.
* Set sleep between threads to 0.5 to fix time out errors when checking a huge amount of extensions.

## Version 0.3

* Using modules instead of one class
* Accepting now strg+c when in multithreaded mode
* Update function will now generate a list with extensions instead of an xml. This list is sorted by default (download count). Loading this file is much faster than parsing the xml everytime.
* It is now possible to use only TOR, Privoxy, or TOR with Privoxy (in order to prevent DNS leakage).
* Max. threads are set to 10 to prevent connection issues and DoS, default threads are now 7.
* Connection timeout can be set with '--timeout VALUE'. Default is 20.
* Verbose mode lists also not installed extensions (but trust me, you don´t want to scroll through over 6400 entries).
* Typo3 version search is more accurate
* If the backend login page could not be found, but Typo3 is used, the user is asked, if he want to proceed. This will mostly lead to "no extensions are installed".

## Version 0.2.1

* Fixed some bugs
* It is now possible to specifiy threads.<br>
  Default is 10.<br>
  I strongly recommend to use only 2 or even 1 thread when using TOR!<br>
  This is because TOR is (extremely) slow and will produce connection errors if too many threads are used.

## Version 0.2

* Added support for Privoxy and TOR
* It is now possible to use Typo-Enumerator with Privoxy and TOR (--tor)<br>
  Privoxy is used to prevent dns leakage ;)<br>
  Please make sure the Privoxy config (/etc/privoxy/config) is set to something like:
 - listen-address   127.0.0.1:8118
 - forward-socks5 / 127.0.0.1:9050 .<br>
  These are the standart ports for Privoxy and TOR<br>
  If TOR is used, threads will be set to 2 in order to minimize errors
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