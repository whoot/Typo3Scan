Typo-Enumerator
===============

Find out the Typo3 Version, Login-URL and Extensions

This tool allows you to check, if a domain uses Typo3.<br>
If so, it will try to find out the Typo3 version and the installed extensions.<br>
If the --top parameter is set to a value, only the [value] top downloaded extensions are tested.<br><br>
Usage:<br>
./typoenum.py -d DOMAIN [DOMAIN ...] [--user_agent USER-AGENT] [--top VALUE] [-v] <br>
or <br>
./typoenum.py -f FILE [--user_agent USER-AGENT] [--top VALUE] [-v]
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
