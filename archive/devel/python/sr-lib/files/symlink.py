#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
 DESCRIPTION  some shell tools for python scripts

 forceSymlink - Create a symlink despite target exists, already
 createDir    - Create a directory in case it does not exist, already.
 createFile   - Create a file and the whole path necessary for creation.
 
 CHANGELOG    
    10-02-03  * split up into mount and file/dir tools
    09-09-01  * finished createFile function, removed checkpath
    09-06-23  * combined mount, symlink, print stuff from pylin

 TODO
 
 THANKS TO

"""



import  os
import  shutil
import  errno                       # error code handler
import file as files

#------------------------------------------------------------------------------
# general error class
#------------------------------------------------------------------------------
class FsError(BaseException):
    pass

#------------------------------------------------------------------------------
# symlink creator
#------------------------------------------------------------------------------
class SymlinkError(FsError):
    """Errors raised when processing forced symlink creation"""
    pass

def create(source_path, target_path, valid_source_only=True):
    """
    Create a symlink despite target exists, already. 
    Check if source exists if needed.
    """

    # check source
    if valid_source_only is True:
        # check if source exists at all
        if not os.path.exists( source_path ):
            raise SymlinkError( 
                "Source file '%s' no found but valid_source_only=True!" 
                % source_path 
            )

    try:
        os.symlink(source_path, target_path)
    except OSError, emsg:
        if emsg.errno == errno.EEXIST:
            # remove old file
            try:
                os.remove(target_path)
            except Exception, emsg:
                raise SymlinkError(
                    "Error removing file in place where symlink shall get "
                    "created (%s)" % emsg
                )
            # create new link
            try:
                os.symlink(source_path, target_path)
            except Exception, emsg:
                raise SymlinkError("Error creating new symlink (%s)" % emsg)
        elif emsg[0] == 2:
            # directory does not exist
            raise SymlinkError(
                "Target directory '%s' not found!" 
                % os.path.dirname( target_path ) 
            )
        else:
            raise


#------------------------------------------------------------------------------
# remove symlink
#------------------------------------------------------------------------------
def remove( path ):

    if not os.path.islink( path):
        raise FsError( "No symbolic link found at '%s'" % path )
    else:
        files.remove( path )


#------------------------------------------------------------------------------
# test structure
#------------------------------------------------------------------------------
if __name__ == "__main__":
    create( "/tmp/lala" , "/tmp/lulu")

#    createFile("/tmp/jaja")
