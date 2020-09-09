#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""                                                                     
DESCRIPTION    block device formatter (ext3 or ext4, highest possible)                       

USAGE          see __doc__ strings or test section for example use
      
TODO
"""
#----------------------------------------------------------------------------
# module handling
#----------------------------------------------------------------------------

__version__ = "$Revision: 0.1.2010-02-12 $"
# $Source$


#TODODEFAULT_MOUNT_OPTIONS=

# module export
__all__ = [
    'FormatError',
    'format',
]

MAX_MOUNT_COUNT =  25
CHECK_INTERVAL  = '4w'  # d m w

# standard
import os.path
import logging
log = logging.getLogger( __name__ )

# extra modules
from pt.data import validate #, ValidateError
import pt.run  # shell command handler ( subprocess )
import pt.files
#import pt.config  # configfile handler

# load config defaults from file relative to module path
# DEFAULT_CONF = "module.conf"
# cfg = pt.config.ConfigFile( DEFAULT_CONF, create_empty=False ) 
 
#----------------------------------------------------------------------------
# error classes                                                          {{{1
#----------------------------------------------------------------------------
class FormattingError(BaseException):
    """Error formating block device"""

#----------------------------------------------------------------------------
# main class                                                             {{{1
#----------------------------------------------------------------------------
def format( device, label, reserved=None, force=False ):
    """
    device: block device to be formatted
    label: 16 bit long label for formatted device
    reserved: 5% by default
    force: set true for formatting dd - created block devices
    TODO: fs usage?
    """

    # check input
    if not pt.files.validate.is_device( device):
        raise FormattingError( 
            "Given path '%s' is not found or no device file !" % device
        )
        
    if len(label) > 16:
        raise FormattingError( 
            "Maximum size for label is 16 bytes but given label '%s' is %s "
            "bytes long!" % (label, len(label) )
        )
    label = validate.is_string( label )
    reserved = reserved and reserved.validate.is_float( 0, 99.999) or 5
    force_option = force and '-F' or ''



    run = pt.run.Run()

    # try ext4 ...
    run.debug( 
        'mkfs.ext4 %s -L %s -m %s %s'  
        %   (
            device, label, reserved, force_option
        )
    )

    # or format ext3 instead
    run.debug( 
        'mkfs.ext3 %s -L %s -m %s -O dir_index %s'  
        %   (
            device, label, reserved, force_option
        )
    )

# -j if ext3 -O dir_index -O extent


#----------------------------------------------------------------------------
# tests and example invocation                                           {{{1
#----------------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    import os
    import pt.terminal # flush buffers, colors, terminal size
    import pt.logger   # set up logger

    # initialize logger
    log = pt.logger.Logger(
#        style = "plain",
        #name         = __name__ , # __name__ or self.__class__.__name__ 
        name         = None , # None = root logger
        level        = logging.DEBUG,  
        file_file    = None,      # None = no file logging
        file_level   = logging.DEBUG,         
    )
