Typo-Enumerator
===============

Find out the Typo3 Version, Login-URL and Extensions

This tool allows you to check, if a domain uses Typo3.<br>
If so, it will try to find out the Typo3 version and the installed extensions.<br>
If the --top parameter is set to a value, only the [value] top downloaded extensions are tested.<br><br>
Usage:<br>
./typoenum.py -d DOMAIN [DOMAIN ...] [--user_agent USER-AGENT] [--top VALUE] [-v] [--tor] <br>
or <br>
./typoenum.py -f FILE [--user_agent USER-AGENT] [--top VALUE] [-v] [--tor]
<br>
<br>

## ChangeLog:
v0.1 Prototype   			             
v0.2 Added version search for Typo3 	     
v0.3 Added version guessing		     	     
v0.4 Optimized requests 		     		       
v0.5 Added support for Typo v6.X  	       
v0.6 Added extension search		     	     
v0.7 Added version search for extensions  
v0.8 Added support for Privoxy and TOR
```
-> It is now possible to use Typo-Enumerator with Privoxy and TOR (--tor)
   Privoxy is used to prevent dns leakage ;)
   Please make sure the Privoxy config (/etc/privoxy/config) is set to something like:
      listen-address   127.0.0.1:8118
      forward-socks5 / 127.0.0.1:9050 .
   These are the standart ports for Privoxy and TOR
   If TOR is used, threads will be set to 2 in order to minimize errors
   
-> All requests (except of the update download) are now made with urllib2

-> Version search for extensions is now more reliable
```
