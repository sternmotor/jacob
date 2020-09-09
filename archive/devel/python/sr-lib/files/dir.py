#!/usr/bin/env python
# -*- coding: utf-8 -*-
#vim:fdm=marker
# unlock vim folding via zR, zo and lock folding via zM, zc
#----------------------------------------------------------------------------
"""                                                                     
DESCRIPTION    simple directory handler functions                         {{{1

USAGE          call this script with -h or --help option
      
CHANGELOG    
   10-02-12    * creation, copied from fstools.py

TODO

THANKS TO

"""

__version__ = "$Revision: 0.1.2010-02-12 $"
# $Source$


#----------------------------------------------------------------------------
# modules import, constants                                              {{{1
#----------------------------------------------------------------------------
# standard
import shutil
import os
import logging
import validate
log = logging.getLogger( __name__ )

# extra modules
 
# constants, default values
 
#------------------------------------------------------------------------------
# error class
#------------------------------------------------------------------------------
class FsDirError(BaseException):
    pass

#------------------------------------------------------------------------------
# remove dir
#------------------------------------------------------------------------------
def remove( path ):
    try:
        shutil.rmtree( path )
    except OSError, emsg:
        if emsg[0] == 2:
            pass
        elif os.path.isfile( path ):
            raise FsDirError(
                "'%s' looks like a file, expected directory" % path 
            )
        else:
            raise FsDirError(
                "Could not remove directory '%s'\n%s" % ( path, emsg )
            )
    else:
        log.debug( "removed dir '%s'" % path )


#------------------------------------------------------------------------------
# set time stamp at path after creating if needed
#------------------------------------------------------------------------------
def touch( path ):
    """Make sure directory exists and set mod time to current time"""
    create( path )
    os.utime( path, None)
    return 


#------------------------------------------------------------------------------
# check if dir exists. create if necessary
#------------------------------------------------------------------------------
def create( path ):
    """
    Create a directory in case it does not exist, already.

    Expects a unix path as argument. An exception is raised
    in case a non-directory exists where the directory should be created

    or the direcotry is not writeable
    """

    # check input
#    try:
#        validate.is_string(path)
#    except validate.ValidateError, emsg:
#        raise FsDirError("Path not specified properly (%s)", emsg )

    # check if dir exists, create if necessary
    if not os.path.exists( path ):
        try:
            os.makedirs( path )
        except OSError, emsg:
            if emsg[0] == 13:
                raise FsDirError( 
                    "Permission denied creating dir '%s' ([Errno 13])!" 
                    % path
                )
            else:
                raise FsDirError(emsg)
        else:
            log.debug( "Success creating dir '%s'" % path )
            return True
    else:
        if os.path.isdir(path):
            log.debug( "Directory '%s already exists'" % path )
            return  True
        else:
            raise FsDirError( "Some file already exists at '%s'!" % path )



#----------------------------------------------------------------------------
# test structure                                                         {{{1
#----------------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    import os
    import errno
    import logging

    create ('/tmpy/test')
