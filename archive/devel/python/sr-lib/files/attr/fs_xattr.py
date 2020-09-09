#!/usr/bin/python
"""
Module handling file "extended attribute" entries. 

set()
    Set a xattr entry

get()
    Returns xattr value stored in file. Raises XattrError in case 
    the entry does not exist.

rem()
    Deletes an xattr entry.

igetall()
    Returns all key, value pairs as iterator

In case a file or directory does not exist, XattrError is raised.
"""

# clear import path so this xattr does not get confused

import os
try:
    import xattr
except ImportError, emsg:
    raise ImportError(
        "Please run 'sudo aptitude install -y python-pyxattr' !\n%s" % emsg
    )

#------------------------------------------------------------------------------
class XattrError(Exception):
#------------------------------------------------------------------------------
    pass


#------------------------------------------------------------------------------
def _checkinput( path, key):
#------------------------------------------------------------------------------
    """check path and key for validity, return proper key"""

#    if not os.path.exists(path):
#        raise XattrError( "Path not found: '%s'" % path )

    if key.startswith('user.'):
        return key
    else:
        return 'user.' + key # You'll only be able to set an attribute whose 
                             # name starts with the user namespace


#------------------------------------------------------------------------------
def set( path, key, value ):
#------------------------------------------------------------------------------
    key = _checkinput( path, key )

    try:
        xattr.set( path, key, value )
    except IOError, emsg:
        raise XattrError( "Xattr's not supported at '%s'" % path \
                          + "or key '%s' is invalid (should " % key \
                          + "look like 'user.test')"
        )

#------------------------------------------------------------------------------
def get( path, key ):
#------------------------------------------------------------------------------
    key = _checkinput( path, key )

    try:
        return xattr.get( path, key )
    except IOError, emsg:
        if emsg[0] == 61:
            # key not available
            raise XattrError("Key not found: '%s' in '%s'" % (key, path) )

#------------------------------------------------------------------------------
def getAll(path):
#------------------------------------------------------------------------------
    """
    Return all xattr keys and it's values as (key, value) pairs.
    """

    _checkinput( path, "" )
    for key in xattr.list( path ):
        yield ( key[5:], xattr.get( path, key ) )

#------------------------------------------------------------------------------
def rem(path, key):
#------------------------------------------------------------------------------
    """
    Remove xattr entry regardless it exists or not
    """
    key = _checkinput( path, key )
    try:
        xattr.remove( path, key )
    except IOError, emsg:
        # ignore error message that entry can not be found
        if emsg[0] == 61:
            pass


#=============================================================================
if __name__ == "__main__":
#=============================================================================
    import sys
    import os

    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
    sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', 0)

    set( "/tmp/tt", "ein3", "wert3")

    
 #   remove("/tmp/tt", "ein1")

    for key, value in igetall( "/tmp/xx",  ):
        print  key, value


