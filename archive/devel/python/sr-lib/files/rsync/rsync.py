#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TODO
    ssh password handling
"""
#----------------------------------------------------------------------------
# module handling
#----------------------------------------------------------------------------

__version__ = "$Revision: 0.1.2010-02-12 $"
# $Source$

# module export
__all__ = [
    'RsyncError',
    'RsyncSystemError',
    'RsyncRunError',
    'Rsync',
]

# standard
import os
import logging
log = logging.getLogger( __name__ )

# extra modules
import pt.run
from pt.data import validate
import pt.files.dir


#----------------------------------------------------------------------------
# error classes                                                          {{{1
#----------------------------------------------------------------------------
class RsyncError(BaseException):
    """General error running rsync """

class RsyncSystemError(RsyncError):
    """Errors initiating rsync process"""

class RsyncRunError(RsyncError):
    """Errors running rsync session"""

#----------------------------------------------------------------------------
# main class                                                             {{{1
#----------------------------------------------------------------------------
class Rsync:
    """
    Rsync wrapper

    OPTIONS/FEATURES
        * timeout handling
        * standard excludes
        * rsync options assembled to meta- options for this class
          quick     # True:  no checksum, no times, no acls/xattr
          delete    # True:  remove everything at target not existing at source
          recursive # False: sync just one given directory

        rsync_options = [], # extra rdiff options
        excludes      = [], # rsync excludes
        bw_limit  = None,   # None = no bandwidth control, otherwise KBytes /sec
        timeout   = None,   # None = no timeout, otherwise seconds
        verbose   = False,  # True: display extra information
        
        ssh_quiet = False,  # True: run ssh with no output
        ssh_port  = 22,     # Port for ssh connection 
        ssh_user  = None,   # User for ssh connection
        ssh_pass  = None,   # Password for ssh connection NOT IMPLEMENTED
        ssh_fast  = False,  # True: run ssh with weak encrpytion, compressed
    """

    # rsync options
    RSYNC_EXE = 'rsync'
    COMMON_OPTIONS = [
        '--verbose' ,
        '--sparse'  ,
        '--partial' ,
        '--numeric-ids',
        '--links'   ,
        '--hard-links',
        '--devices' ,
        '--specials',
        '--human-readable',
        '--protect-args',      # preserve whitespaces
    ]
    DELETE_OPTIONS =        [ '--delete-during', ] # '--delete-excluded', ] no!!
    QUICK_OPTIONS =         [ '--size-only', ]
    NON_QUICK_OPTIONS =     [
        '--archive'   ,
        '--checksum', 
        '--acls'    ,
        '--xattrs'  ,
        '--modify-window=20',
        '--omit-dir-times'  ,
    ]
    RECURSIVE_OPTIONS =     [ '--recursive', ]
    NON_RECURSIVE_OPTIONS = [ '--no-r', '--dirs', ]
    VERBOSE_OPTIONS =       [
        '--progress',
        '--stats',
        '--itemize-changes',
        '--verbose',
    ]
    BANDWIDTH_OPTION = '--bwlimit='

    # ssh options
    SSH_EXE   = 'ssh'
    SSH_QUIET_OPTIONS    = [ '-q', ]
    SSH_COMMON_OPTIONS   = [ '-o', "Compression no" ]
    SSH_FAST_OPTIONS     = [ '-c', "arcfour,blowfish-cbc,aes192-cbc"    ]
    SSH_NON_FAST_OPTIONS = [ '-c', "blowfish-cbc,aes192-cbc"   ]
    
    def __init__(self,
        source_host   = None,
        target_host   = None,

        rsync_options = [], # extra rdiff options
        excludes      = [], # rsync excludes
        quick     = False,  # True: # no checksum, no times, no acls/xattr
        delete    = True,   # True: remove everything at target not existing at source
        recursive = True,   # False: sync just one given directory
        bw_limit  = None,   # None = no bandwidth control, otherwise KBytes /sec
        timeout   = None,   # None = no timeout, otherwise seconds
        verbose   = False,  # True: display extra information
        contentsonly = True,# True: sync conte
        
        ssh_quiet = False,  # True: run ssh with no output
        ssh_port  = 22,     # Port for ssh connection 
        ssh_user  = None,   # User for ssh connection
        ssh_pass  = None,   # Password for ssh connection NOT IMPLEMENTED
        ssh_fast  = False,  # True: run ssh with weak encrpytion, compressed
    ):

        # rsync executable
        try:
            self.rsync_exe = pt.run.which(self.RSYNC_EXE)
        except pt.run.ExeError, emsg:
            raise RsyncSystemError( emsg )


        # common and user options
        val_str_list = validate.is_string_list
        self.rsync_options      = val_str_list( self.COMMON_OPTIONS         )

        self.rsync_options     += val_str_list( rsync_options               )

        # switches
        if quick: 
            self.rsync_options += val_str_list(self.QUICK_OPTIONS           )
        else:
            self.rsync_options += val_str_list(self.NON_QUICK_OPTIONS       )

        if delete:
            self.rsync_options += val_str_list(self.DELETE_OPTIONS          )

        if recursive:
            self.rsync_options += val_str_list(self.RECURSIVE_OPTIONS       )
        else:
            self.rsync_options += val_str_list(self.NON_RECURSIVE_OPTIONS   )

        if verbose:
            self.rsync_options += val_str_list(self.VERBOSE_OPTIONS         )
        # bwlimit, timeout
        if bw_limit:
            self.rsync_options.append( "%s%s" % (
                self.BANDWIDTH_OPTION,
                validate.is_integer( bw_limit, 1 )
            ) )
        self.timeout = timeout and validate.is_integer( timeout, 1 ) or None


        # sort options except exclude options
        self.rsync_options.sort() 

        # excludes
        for exclude in excludes:
            self.rsync_options.append( 
                "--exclude=%s" % validate.is_string( exclude ) 
            )

        # source and target
        # only one of source or target should be remote
        if source_host and target_host:
            raise RsyncError(
                "Both source and target are remote, sorry can't handle this"
            )

        # remote operation?
        if source_host or target_host:
            # check ssh executable
            try:
                ssh_exe = pt.run.which(self.SSH_EXE)
            except pt.run.ExeError, emsg:
                raise RsyncSystemError( emsg )

            # set ssh options      
            self.ssh_options = [ssh_exe] 
            if ssh_user:
                self.ssh_options.append("-l %s" %  validate.is_string(ssh_user) )
            if ssh_port:
                self.ssh_options.append("-p %s" % validate.is_integer(ssh_port, 1, 65536) )
            if ssh_quiet:
                self.ssh_options.extend( self.SSH_QUIET_OPTIONS )
            if ssh_fast:
                self.ssh_options.extend( self.SSH_FAST_OPTIONS  ) 
            else:
                self.ssh_options.extend( self.SSH_NON_FAST_OPTIONS  ) 
            self.ssh_options.extend( self.SSH_COMMON_OPTIONS ) 

#            self.ssh_options = [
#                ssh_exe, 
#                ssh_user and "-l %s" %  validate.is_string(ssh_user) or '',
#                ssh_port and "-p %s" % validate.is_integer(ssh_port, 1, 65536),
#                ' '.join( self.SSH_COMMON_OPTIONS ),
#                ssh_quiet and ' '.join( self.SSH_QUIET_OPTIONS ) or '',
#                ssh_fast  and ' '.join( self.SSH_FAST_OPTIONS  ) \
#                  or ' '.join(self.SSH_NON_FAST_OPTIONS),
#            ]
        else:
            self.ssh_options = None

        self.source_host = source_host and validate.is_string( source_host ) or None
        self.target_host = target_host and validate.is_string( target_host ) or None

        # create shell executer instance
        self.run = pt.run.Run()

    def istart(self, 
        source_path, 
        target_path, 
    ):
        """ Start rsync run, yield every output line back to caller """
        if not source_path or not target_path:
            raise RsyncError(
                "Source or target path not defined for Rsync.istart()"
            )
    
        # check lokal source 
        if self.source_host:
            source = "%s:%s" % ( self.source_host, source_path)
        else:
                
            if not os.path.exists( source_path):
                raise RsyncError(
                    "Could not find lokal source '%s'" % source_path
                )
            source = source_path

        # check lokal target
        if self.target_host:
            target = "%s:%s" % ( self.target_host, target_path)
        else:
            target_dirname = os.path.dirname( target_path )
            if not os.path.exists( target_dirname):
                log.debug( "Creating path for rsync target: '%s'" % target_dirname )
                try:
                    pt.files.dir.create( target_dirname )
                except pt.files.dir.FsDirError, emsg:
                    raise RsyncError(
                        "Could not access target path '%s':\n%s"  
                        % (target_dirname, emsg)
                    )
            target = target_path

        # start rsync executable
        cmd = "%s %s %s '%s' '%s'" % (
            self.rsync_exe,
            ' '.join(self.rsync_options),
            self.ssh_options and "-e '%s'" % self.run.fix_cmd_string(self.ssh_options) or '',
            source,
            target,
        )
        log.info ( "STARTING '%s'" % cmd.strip() )

        try:
            for line in self.run.start(cmd):
                yield line
        except pt.run.run.RunError, emsg:
            raise RsyncRunError( emsg)


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
        name         = None , # None = root logger
        level        = logging.DEBUG,
        file_file    = None,      # None = no file logging
        file_level   = logging.DEBUG,
    )

    try:
        rs = Rsync(source_host="backup1.bb", ssh_fast=True, ssh_quiet=True, verbose=True)
    except RsyncError, emsg:
        pt.terminal.write_err( emsg)
        sys.exit(1)

    try:
        for line in rs.istart( "/etc/ssl", "/tmp" ):
            print line
    except RsyncError, emsg:
        pt.terminal.write_err( emsg )
        sys.exit(1)
