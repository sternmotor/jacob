#!/usr/bin/env python3
"""inventory loader config functions"""


# MODULE SETUP

import yaml
import logging
from lib.error import KnownError

log = logging.getLogger('config')


# objects exported from this module file
__all__ = (
    'load',        
)


# MAIN FUNCTIONS

def load(path):
    """load config from file"""

    # load
    log.debug('Retrieving yaml config from "{}"'.format(path))
    try: 
        with open(path, 'r') as config_file:
            return yaml.load(config_file)
    except FileNotFoundError:
        raise KnownError('Config file "{}" not found !'.format(path))


# SUPPORT FUNCTIONS


# MODULE TESTS

if __name__ == '__main__':

    import os
    import pprint
    import sys
    logging.basicConfig(level=logging.DEBUG)

    SCRIPT_DIR = os.path.realpath('..')
    CONFIG_FILE = os.path.join(SCRIPT_DIR, 'loader.yml')
    pprint.pprint(load(CONFIG_FILE))

