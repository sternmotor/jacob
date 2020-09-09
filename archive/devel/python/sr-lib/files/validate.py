#!/usr/bin/env python
# -*- coding: utf-8 -*-
#vim:fdm=marker
# unlock vim folding via zR, zo and lock folding via zM, zc
#----------------------------------------------------------------------------
"""                                                                     
DESCRIPTION    simple directory handler functions                        {{{1

USAGE          see __doc__ strings or test section for example use
      
CHANGELOG    
   10-02-12    * creation, copied from fstools.py

TODO

THANKS TO

"""

__version__ = "$Revision: 0.1.2010-11-05 $"
# $Source$


#----------------------------------------------------------------------------
# modules import, constants                                              {{{1
#----------------------------------------------------------------------------

# module export
__all__ = [
    'FileValidateError',
    'is_exe',
    'is_device',
]

# standard
import logging
log = logging.getLogger( __name__ )
import os
import stat
#from stat import st_mode

#----------------------------------------------------------------------------
# error classes                                                          {{{1
#----------------------------------------------------------------------------
class FileValidateError(BaseException):
    """Error validating file or directory"""

#----------------------------------------------------------------------------
# main functions                                                         {{{1
#----------------------------------------------------------------------------

def is_block_device( fpath):
    """
    Return False in case fpath is no block device, True otherwise
    see http://docs.python.org/library/stat.html
    """

    try:
        mode = os.stat( fpath).st_mode
    except OSError, emsg:
        raise FileValidateError( "Path '%s' not found!" % fpath)
    return stat.S_ISBLK(mode)

def is_exe( fpath ):
    """
    Raise FileValidateError in case fpath is no
    executable file  or symlink to some file
    """

    if os.path.isfile(fpath)  \
        and os.access(fpath, os.X_OK) \
        and os.access(fpath, os.R_OK):

        log.debug( "Found executable '%s'" % fpath )
        return True
    else:
        raise FileValidateError(
            "Path or link '%s' does not direct to a file which is readable "
            "and executable!" % fpath
        )

def is_writeable( fpath ):
    """
    Raise FileValidateError in case fpath is not readable
    """

    if os.path.isfile(fpath) and os.access(fpath, os.W_OK):
        return True
    else:
        raise FileValidateError(
            "Path or link '%s' does not direct to a file which is writeable"
            % fpath
        )

def is_readable( fpath ):
    """
    Raise FileValidateError in case fpath is not readable
    """

    if os.path.isfile(fpath) and os.access(fpath, os.R_OK):
        return True
    else:
        raise FileValidateError(
            "Path or link '%s' does not direct to a file which is readable"
            % fpath
        )
#----------------------------------------------------------------------------
# tests and example invocation                                           {{{1
#----------------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    import os
    print is_readable( "/usr/bin/thunderbird" )

    print is_block_device( '/dev/sdg1')
