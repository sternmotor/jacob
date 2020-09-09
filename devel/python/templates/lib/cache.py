#!/usr/bin/env python3
"""inventory cache functions"""


# MODULE SETUP

import os.path
import time
import logging
from lib.error import KnownError
log = logging.getLogger('cache')


# objects exported from this module file
__all__ = (
    'is_outdated',        
)

# CONSTANTS

# max number of age limit for cache file = 10 years 
MAX_CACHE_AGE = 10 * 365 * 24 * 60 * 60
MIN_CACHE_AGE = 1



# MAIN FUNCTIONS

def is_outdated(raw_path, raw_timeout):
    """
    return True if file at path is older than timeout or cache file has not
    been produced, yet
    """

    # validate input
    timeout = validate_timeout(raw_timeout)

    # cache file not found?
    path = os.path.expanduser(raw_path)
    try:
        mtime = os.path.getmtime(path)
        log.debug('file "{}" exists, timestamp {}'.format(path, int(mtime)))
    except FileNotFoundError:
        log.debug('file "{}" not found'.format(path))
        return True

    # check cache file date
    else:
        return mtime < time.time() - timeout


# SUPPORT FUNCTIONS


def validate_timeout(timeout):
    """Check if timeout value is ok, raise KnownError otherwise"""


    # catch exception from int() *or* MIN|MAX_CACHE_AGE
    try:
        if not MIN_CACHE_AGE <= int(timeout) <= MAX_CACHE_AGE:
            raise ValueError
    except ValueError:
        raise KnownError(
            'Bad specified cache timeout parameter "{0}", should be number '
            'between {2} and {1}'.format(timeout, MAX_CACHE_AGE, MIN_CACHE_AGE)
        )
    # fine
    else:
        return int(timeout)


# MODULE TESTS

if __name__ == '__main__':

    import os
    import sys
    import config as config_loader
    logging.basicConfig(level=logging.DEBUG)

    # get config
    SCRIPT_DIR = os.path.realpath('..')
    CONFIG_FILE = os.path.join(SCRIPT_DIR, 'loader.yml')
    config = config_loader.load(CONFIG_FILE)

    # check main functions
    print(is_outdated(config['cache_file'], 2))

