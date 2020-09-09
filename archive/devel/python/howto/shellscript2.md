Python Module
see http://python-packaging.readthedocs.io/en/latest/dependencies.html

"""
logging
option parser
signal handling
error class for proper shell exit codes
system calls
"""

import argparse
import logging
import subprocess

logging.basicConfig(level=logging.INFO, format='%(message)s')


ERROR_NOTFOUND = (2, 'Device could not be found')

def main()
    arparse(Description)
        --debug
        -q --quiet
    if args.debug:
        logging.basicConfig(level=logging.DEBUG, format='%(message)s')
    if args.quiet:
        stdout. dev null
        logging.basicConfig(level=logging.WARNING, format='Error: %(message)s')

        
        
        
# translate exceptions into shell exit codes
if __name__ == "__main__":
    try:
        main()