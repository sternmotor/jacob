#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""                                                                     
DESCRIPTION    tar module enhancment for use in shell scripts

USAGE          see __doc__ strings or test section for example use
      
TODO
"""
#----------------------------------------------------------------------------
# module handling
#----------------------------------------------------------------------------

__version__ = "$Revision: 0.1.2010-02-12 $"
# $Source$

# module export
__all__ = [
    'TarError',
    'compress',
    'decompress',
]

# standard
import tarfile
import os
import logging
log = logging.getLogger( __name__ )

# constants
COMPRESS_MODE = 'bz2'   # bz2, gz
 
#----------------------------------------------------------------------------
# error classes                                                          {{{1
#----------------------------------------------------------------------------
class TarError(BaseException):
    """Error Decompressing ascii stream"""

#----------------------------------------------------------------------------
# main funtions                                                             {{{1
#----------------------------------------------------------------------------
def compress( source_pathes, target_path=None, compress_mode=COMPRESS_MODE ):
    """ 
    Generate tar file from source file(s) or directorie(s).
    In case target_path is not given, a file name is created from 
    source names.

    Behaviour differs from standard tar: only last dir or file in path
    is beeing zipped
    """

    # check source input
    if type(source_pathes) is not type([]):
        source_pathes = [source_pathes]

    # check target input: create tar file name
    if target_path is None:
        target_path = "%s.tar.%s" % (
            '_'.join( [os.path.basename (path) for path in source_pathes]),
            compress_mode,
        )
    target_path.replace(' ','_')

    # generate gzip tar file
    try:
        tar = tarfile.open( target_path, "w:%s" % compress_mode)
    except IOError, emsg:
        raise TarError(
            "Error creating tar file '%s'!\n%s" % (target_path, emsg)
        )
    for source in source_pathes:

        source_path = os.path.dirname( source )
        source_file = os.path.basename( source )

        # cd to source dir, store path where caller came from
        try:
            if source_path: 
                old_path = os.getcwd()
                os.chdir(source_path)
        except OSError:
            raise TarError(
                "Could not enter directory '%s'" % source_path
             )
        # pack stuff
        try:
            tar.add(source_file)
        except OSError, emsg:
            raise TarError(
                "Could not open target path '%s'\n%s" 
                % (source, emsg)
            )
        except IOError, emsg:
            raise TarError(
                "Error compressing '%s'\n%s" % (source, emsg)
            )
        # cd back to where caller came from
        if source_path:
            os.chdir(old_path)
    tar.close()

def decompress( tar_file, target_dir=None, compress_mode=COMPRESS_MODE ):
    """ unpack tar file  to target dir (if specified)"""

    # check input
    try:
        if not tarfile.is_tarfile(tar_file):
            raise TarError( 
                "File '%s' does not look like a tar file!" % tar_file
            )
    except IOError, emsg:
        print os.listdir('.')
        raise TarError( "Error reading tar file: %s" % emsg )

    # check target location
    if target_dir is not None:
        if os.path.isdir(target_dir):
        # cd to target dir, store path where caller came from
            old_path = os.getcwd()
            os.chdir(target_dir)
        else:
            raise TarError(
                "Could not enter target dir '%s', check destination!"
                % target_dir
            )

    try:
        tar = tarfile.open( tar_file, "r:%s" % compress_mode)
    except IOError, emsg:
        raise TarError(
            "Could not open tar file '%s'\n%s"
            % ( tar_file, emsg )
        )

    try:
        tar.extractall()
    except IOError, emsg:
        raise TarError( "Error extracing file '%s'\n%s" % ( tar_file, emsg ) )
    tar.close()

    # cd back to where caller came from
    if target_dir is not None:
        os.chdir(old_path)




#----------------------------------------------------------------------------
# tests and example invocation                                           {{{1
#----------------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    import os
    import pt.terminal # flush buffers, colors, terminal size
    import pt.logger   # set up logger

#    # initialize logger
#    log = pt.logger.Logger(
#        style = "plain",
#        #name         = __name__ , # __name__ or self.__class__.__name__ 
#        name         = None , # None = root logger
#        level        = logging.DEBUG,  
#        file_file    = None,      # None = no file logging
#        file_level   = logging.DEBUG,         
#    )

    try:
        compress( '/etc/hosts')
    except TarError, emsg:
        print emsg
        sys.exit(1)

    try:
        decompress( 'hosts.tar.%s' % COMPRESS_MODE)
    except TarError, emsg:
        print emsg
        sys.exit(1)
