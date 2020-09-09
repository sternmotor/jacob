#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
 DESCRIPTION  some shell tools for python scripts
    remove( path )
    touch( path )
    create( path )
    tail(filepath, nol=30, read_size = 4096)
    grep( path, string )
    grep_bigfile( path, string )

 CHANGELOG    
 TODO
 
 THANKS TO

"""



import os
import shutil
import dir

#------------------------------------------------------------------------------
# general error class
#------------------------------------------------------------------------------
class FsError(Exception):
    pass

def remove( path ):

    try:
        os.remove( path )
    except OSError, emsg:
        if emsg[0] == 2:
            pass
        elif os.path.isdir( path ):
            raise FsError(
                    "'%s' looks like a directory, expected single file" 
                    % path 
            )
        else:
            raise FsError(
                    "Could not remove file '%s' (OSError %d, %s)"
                    % ( path, emsg[0], emsg[1] )
            )

def touch( path ):
    """Make sure file exists and set modification time to current time"""
    create( path )
    os.utime( new_path, None)
    return True

def create( path ):
    """
    Create a file and the whole path necessary for creation.

    Expects a unix path as argument. In case the file exists,
    already, nothing is done.
    """

    # check file
    if os.path.exists(path):
        if os.path.isfile(path):
            return True
        else:
            raise FsError( 
                "'%s' exists already but is no file - remove manually!" 
                % path 
            )
    else:
        # get directory info from path, check dir ...
        dir  = os.path.dirname(path)
        try:
            fs.dir.create( dir )
        except FsError, emsg:
            raise FsError( 
                "Could not create directory '%s\n%s" 
                % (dir, emsg) 
            )

        # ... and create file
        try:
            open(path, 'w').close()
        except IOError, emsg:
            raise FsError( 
                "Could not write to file '%s'\n%s" % ( path, emsg)
            )

def tail(filepath, nol=30, read_size = 4096):
  """
  This function returns the last "nol" lines of a file.
  Args:
    filepath: path to file
    nol: number of lines to print
    read_size:  data is read in chunks of this size (optional, default=1024)
  Raises:
    IOError if file cannot be processed.
  """
  f = open(filepath, 'rU')    # U is to open it with Universal newline support
  offset = read_size
  f.seek(0, 2)
  file_size = f.tell()
  while 1:
    if file_size < offset:
      offset = file_size
    f.seek(-1*offset, 2)
    read_str = f.read(offset)
    # Remove newline at the end
    if read_str[offset - 1] == '\n':
      read_str = read_str[:-1]
    lines = read_str.split('\n')
    if len(lines) >= nol:  # Got nol lines
      return "\n".join(lines[-nol:])
    if offset == file_size:   # Reached the beginning
      return read_str
    offset += read_size
  f.close()


def grep( path, string ):
    """
    Very simple grep implementation: returns matching lines 
    in case file contains string
    """
    matches = []
    for line in grep_bigfile(path, string):
            matches.append(line)

    if len( matches ) > 0:
        return matches
    else:
        return None
    

def grep_bigfile( path, search_string ):
    """
    grep generator, for usage see grep function above
    """
    fh = open (path, 'r' )
    for line in fh.readlines():
        if search_string in line:
            yield line
    fh.close()


#------------------------------------------------------------------------------
# test structure
#------------------------------------------------------------------------------
if __name__ == "__main__":
    import symlink

    print grep( '/etc/fstab', '' )

    file_name = '/tmp/src'
    create(file_name)
    symlink.create( file_name, "%s_link" % file_name )
    symlink.remove(file_name)




