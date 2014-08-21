#!/usr/bin/env python

"""
Copyright (c) 2014 Jan Rude
"""

from Queue import Queue
from threading import Thread, Lock

# Domain to check
# Valid: string
DOMAIN = ""

# Maximum number of threads (avoiding connection issues and/or DoS)
MAX_NUMBER_OF_THREADS = 10

# Default port used by Tor
DEFAULT_TOR_PORT = 9050

# Default ports used in Tor proxy bundles
DEFAULT_PRIVOXY_PORT = 8118

# List with selected extensions
EXTENSION_LIST = []

# List with extensions, where no versioninformation is available
NO_VERSIONINFO = ['wt_spamshield', 'introduction'] #introduction has ChangeLog, but will use "Typo3 4.5.0" as version info!

# Check only top X extensions
# Default: all
TOP_EXTENSION = 'all'

# HTTP User-Agent header value. Useful to fake the HTTP User-Agent header value at each HTTP request
# Default: Mozilla/5.0
user_agent = {'User-Agent' : "Mozilla/5.0"}

# Maximum number of concurrent HTTP(s) requests (handled with Python threads)
# Valid: integer
# Default: 7
THREADS = 7

# Verbosity.
verbose = False

#Input and output queues
in_queue = ""
out_queue = ""

# Seconds to wait before timeout connection.
# Valid: int
# Default: 20
TIMEOUT = 20

# Possible paths to Typo3 loginpage !! not used atm !!
LOGIN_PATHS = ()

# Possible paths and regex to typo3 version information
TYPO3_VERSION_INFO = {'/typo3_src/ChangeLog':'RELEASE] Release of TYPO3 (.*)', '/typo3_src/NEWS.txt':'http://wiki.typo3.org/TYPO3_(\d{1,2}\.\d{1,2})', '/typo3_src/NEWS.md':"(.*) - WHAT'S NEW", 
'/ChangeLog':'RELEASE] Release of TYPO3 (.*)', '/NEWS.txt':'http://wiki.typo3.org/TYPO3_(\d{1,2}\.\d{1,2})', '/NEWS.md':"(.*) - WHAT'S NEW"}

# Typo3 verision details
TYPO_VERSION = None

# Possible paths to an extension
EXTENSION_PATHS = ('/typo3conf/ext/', '/typo3/sysext/')

# Possible version info file
EXTENSION_VERSION_INFO = ('ChangeLog', 'README.txt')

EXTENSIONS_FOUND = 0



## Not used atm ##

# Maximum total number of redirections (regardless of URL) - before assuming we're in a loop
MAX_TOTAL_REDIRECTIONS = 10

# Maximum number of connection retries (to prevent problems with recursion)
MAX_CONNECT_RETRIES = 100

# Delay in seconds between each HTTP request.
# Valid: float
# Default: 0
delay = 0

# Maximum number of retries when the HTTP connection timeouts.
# Valid: integer
# Default: 3
retries = 3

# Use persistent HTTP(s) connections.
KEEPALIVE = False