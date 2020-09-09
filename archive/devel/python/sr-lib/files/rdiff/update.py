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

__version__ = "$Revision: 0.1.2010-02-12 $"
# $Source$


#----------------------------------------------------------------------------
# modules import, constants                                              {{{1
#----------------------------------------------------------------------------

# module export
__all__ = [
    'RdiffUpdate',
    'RdiffUpdateError',
]

# standard
import logging
log = logging.getLogger( __name__ )
import os


# extra modules
#import pt.syscmd  # shell command handler ( subprocess )
from pt.files import validate_file
from pt.data  import validate   # data validator
from rdiff import *
#from pt.syscmd import syscmd
import pexpect


#----------------------------------------------------------------------------
# error classes                                                          {{{1
#----------------------------------------------------------------------------
# imported from rdiff
class RdiffUpdateError(RdiffError):
    """Error running rdiff-backup update action"""


#----------------------------------------------------------------------------
# main class                                                             {{{1
#----------------------------------------------------------------------------
class RdiffUpdate(Rdiff):
    """
    DESCRIPTION
      rdiff-backup wrapper for starting one backup action


    FEATURES
        * useful default excludes

    OPTIONS
        excludes = array of rdiff-backup --exclude-regexp expressions
        includes = --include-regexp expressions
        rdiff_extra_options=[], array of rdiff-backup extra options
    
    METHODS
        update(source, target, as_date) 
            * Copy next increment resp. create backup repository
            * run check
            
        
            path, source, target 
            * directories or remote location where to run action
                [[user[%passwd]@]host::]PATH
         stop(), cleanup(), bwu(), bwd() see rdiff.py

    EXCEPTIONS
    LOGGING
    EXAMPLE
    """

    EXCLUDES = [
        '/proc/*'
        '/sys/*'
        ]

    REGEXP_EXCLUDES = [
        r'/proc'        ,
        r'/sys'         ,
        r'rdiff-backup-data',
        r'lost+found' ,
        r'.Trashes'   ,
        r'System Volume Information',
        r'RECYCLER'   ,
        r'RECYCLE.BIN',
        r'.recycle'   ,
        r'.Thumbs.db' ,
    ]

    # these options are applied for each command
    RDIFF_UPDATE_OPTIONS= [
        r'--print-statistics'       ,
        r'--backup-mode'            ,
        r'--restrict-read-only'     ,
        r'--exclude-sockets'        ,
    ]


    def __init__(self,
        excludes        = [],
        regexp_excludes = [],
        includes        = [],
        regexp_includes = [],
        rdiff_extra_options   = [],
        **kwargs
    ):
        """
        Check some options an prerequisites. See class __doc__ for OPTIONS
        description.
        """
          
        print kwargs
        # initialise parent class
        Rdiff.__init__(
            self, kwargs
        )


        # validate input parameters, store in class
        self.excludes           = validate.is_string_list(
                                    excludes + self.EXCLUDES
                                )
        self.includes           = validate.is_string_list( includes )
        self.regexp_excludes    = validate.is_string_list( 
                                    regexp_excludes + self.REGEXP_EXCLUDES
                                )
        self.regexp_includes    = validate.is_string_list( regexp_includes )
        self.rdiff_extra_options  = validate.is_string_list( rdiff_options )
#        # verbosity tests
#        self.rdiff_options.append( 
#            "--verbosity=%s" % validate.is_integer( rdiff_verb, 0, 9 ) 
#        )


    def update(self, source=None, target=None, current_date=None, timeout=None ):
        """ run backup"""

        # check if current date must be changed
        # FIXME
        
      


        # set up source and target   
        if target is None or source is None:
            raise RdiffOptionsError(
                "Both source and target must be defined here, found"
                "\nsource: '%s' \ntarget: '%s'" % (source, target)
            )

        # stack together options array
        options = self.RDIFF_START_OPTIONS 
        options += self.rdiff_options
        options += self._check_clude( self.excludes, '--exclude')
        options += self._check_clude( self.regexp_excludes, '--exclude-regexp')
        options += self._check_clude( self.includes, '--include')
        options += self._check_clude( self.regexp_includes, '--regexp-include')

        # analyse given source and target
        self.source = self._analyseaddr( source ) 
        self.target = self._analyseaddr( target ) 

        # set up target temp dir, return option string for local or remote tmp
        options += self._get_tmp_dir()

        # set up ssh and bw limit options
        if   self.source['is_remote'] is True:
            options.append ( self._get_ssh_options( self.source) )
            if self.target['is_remote'] is True:
                log.warning( 
                    "Both source and target are remote, applying "
                    "remote settings to source, only"
                )
        elif self.target['is_remote'] is True:
                options.append ( self._get_ssh_options( self.target) )

        self._run_rdiff_exe( 
            options,
            self.source['addr_path'], 
            self.target['addr_path'],
            timeout,
            )

        
    def _check_clude(self, cludes, option_string):
        return_array = []
        for clude in cludes:
            return_array.append( "%s=%s" % (option_string, clude) )
        return return_array


##!/usr/bin/env python
#import pexpect
#
#ssh_newkey = 'Are you sure you want to continue connecting'
## my ssh command line
#p=pexpect.spawn('ssh mysurface@192.168.1.105 uname -a')
#
#i=p.expect([ssh_newkey,'password:',pexpect.EOF])
#if i==0:
#    print "I say yes"
#    p.sendline('yes')
#    i=p.expect([ssh_newkey,'password:',pexpect.EOF])
#if i==1:
#    print "I give password",
#    p.sendline("mypassword")
#    p.expect(pexpect.EOF)
#elif i==2:
#    print "I either got key or connection timeout"
#    pass
#print p.before # print out the result




#----------------------------------------------------------------------------
# tests and example invocation                                           {{{1
#----------------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    import os
    import pt.terminal # flush buffers, colors, terminal size
    import pt.logger   # set up logger
    import pt.terminal

    # initialize logger
    log = pt.logger.Logger(
#        style = "plain",
        name         = None, # __name__ or self.__class__.__name__ 
        level        = logging.DEBUG,  
        file_file    = None,      # None = no file logging
        file_level   = logging.DEBUG,         
    )

    rd=RdiffUpdate( fast_ssh=1, bwu=200000)
    rd.update(source = "/etc", target = "/tmp/delme", timeout = None )
