#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""                                                                     
DESCRIPTION    convert bin files and to asci and back

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
    'Asc2BinError',
    'asc2bin',
    'bin2asc',
]

# default length for ascii lines
DEFAULT_LINE_LENGTH=76


# standard
import base64
import logging
log = logging.getLogger( __name__ )

#----------------------------------------------------------------------------
# error classes                                                          {{{1
#----------------------------------------------------------------------------
class Asc2BinError(BaseException):
    """Some Error"""

#----------------------------------------------------------------------------
# main class                                                             {{{1
#----------------------------------------------------------------------------

def bin2asc( input_fh, output_fh, line_length=DEFAULT_LINE_LENGTH):
    """
    Decode to file from urlsafe base64 encoded input
    url-safe means: + replaced by -, / replaced by _
    """

    max_bin_size = (line_length//4)*3

    while True:
        s = input_fh.read(max_bin_size)
        if not s:
            break
        while len(s) < max_bin_size:
            ns = input_fh.read(max_bin_size-len(s))
            if not ns:
                break
            s += ns
        base64_line = base64.urlsafe_b64encode(s)
        output_fh.write( "%s\n" %  base64_line)


def asc2bin( input_fh, output_fh ):
    """
    Decode to file from urlsafe base64 encoded input
    url-safe means: + replaced by -, / replaced by _
    """

    while True:
        line = input_fh.readline()
        if not line:
            break
        s = base64.urlsafe_b64decode(line)
        output_fh.write(s)
    


#----------------------------------------------------------------------------
# tests and example invocation                                           {{{1
#----------------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    import os
    import pt.terminal # flush buffers, colors, terminal size
    import tempfile

    # show ascii output
    bin_fh = open( '/bin/ls', 'r')
#    bin2asc( bin_fh, sys.stdout)

    # write to tmp file
    asc_tmp_fh =  open( 'ls_asc', 'w')
    bin2asc( bin_fh, asc_tmp_fh)
    asc_tmp_fh.close()

    # recreate from tmp file    
    asc_tmp_fh = open( 'ls_asc', 'r')
    new_bin_fh = open( 'ls_new', 'w:b')
    asc2bin( asc_tmp_fh, new_bin_fh)

    bin_fh.close() 
    asc_tmp_fh.close()
    new_bin_fh.close()

    

