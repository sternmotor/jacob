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
    'Rdiff',
    'RdiffError'            ,
    'RdiffNetworkError'     ,
    'RdiffTimeoutError'     ,
    'RdiffSshTimeoutError'  ,
    'RdiffOptionsError'     ,
    'RdiffRunError'         ,
    'RdiffBusyError'        ,
    'RdiffSystemError'      ,
]

# standard
import logging
log = logging.getLogger( __name__ )
import os


# extra modules
#import pt.syscmd  # shell command handler ( subprocess )
from pt.files import validate_file
from pt.files import dir
from pt.data  import validate   # data validator
from pt.run   import Run


#----------------------------------------------------------------------------
# error classes                                                          {{{1
#----------------------------------------------------------------------------
class RdiffError(Exception):
    """All Errors during rdiff-backup call"""

# network errors
class RdiffNetworkError(RdiffError):
    """Timeout during ssh connection setup or other network error"""

class RdiffTimeoutError(RdiffError):
    """Timeout during rdiff action"""

class RdiffSshTimeoutError(RdiffError):
    """Timeout during ssh network connection setup"""

class RdiffOptionsError(RdiffError):
    """Wrong options to Rdiff class methods"""

class RdiffRunError(RdiffError):
    """Fatal condition found during rdiff run"""

class RdiffBusyError(RdiffError):
    """Rdiff backup session running on target"""

# errors running shell commands
class RdiffSystemError(RdiffError):
    """Pre - or Post backup command failed at remote site"""


#----------------------------------------------------------------------------
# main class                                                             {{{1
#----------------------------------------------------------------------------
class Rdiff:
    """
    DESCRIPTION
      rdiff-backup wrapper for starting rdiff-backup command

    FEATURES
        * bandwidth control for local and remote operation
        * ssh port, encryption, compression control
        * retry regime for connection setup
        * log analysis, proper error handling, smart job control
        * logging control (log rotation)
        * verbosity settings via python log handler
        * separate error, short and full log
        * temp dir handling: 
            * if target is local, temp dir is rdiff-backup-data/tmp
            * if target is remote, temp dir is rdiff-backup-data/tmp
        * timeout for rdiff-backup command


    OPTIONS
        rdiff_options=[]
            * array of rdiff-backup options
        source, target 
            * directories or remote location where to run action
                [[user[%passwd]@]host::]PATH

        ssh_port
        ssh_user 
        ssh_fast 
            * true: turn compression, encrpytion off
        ssh_timeout 
            * ssh connection timeout
        bwu = BWU,      initial bandwidh limit        # kbyte / sec
        bwd = BWD,     initial bandwidh limit         # kbyte / sec
        max_log_size = MAX_LOG_SIZE,    # Megabytes
            maximum size for backup.log, backup_short.log (Mbyte)
        log_verb = LOG_VERBOSITY,
        dis_verb = DIS_VERBOSITY,
   
   METHODS
        start() start rdiff-backup with options
        stop() try to kill running rdiff-backup session
                (needs target to be lokal)
        cleanup() logrotation, tmp dir creation etc
            this method is run once before and after start() command

        bwd()       
            * Tune read   bandwidth (download) live (kBit/s)
        bwu()       
            * Tune write  bandwidth (upload)   live (kBit/s)

    EXCEPTIONS
    LOGGING
    EXAMPLE
    """

    # class constants:
    CSTREAM_EXE = "/usr/bin/cstream"
    SSH_EXE     = "/usr/bin/ssh"
    RDIFF_EXE   = "/usr/bin/rdiff-backup"
    LOGR_EXE    = "/usr/sbin/logrotate"

    # these options are applied for each command
    RDIFF_OPTIONS= [
        r'--preserve-numerical-ids'  ,
        r'--no-compare-inode'        ,
    ]

    # when one of these words is found in log, raise exception immediately
    ERROR_LOG_ENTRIES = [
        'Fatal',
    ]

    # default options
    SSH_MAX_PORT = 65536
    FAST_SSH_CIPHERS = [ "arcfour", "blowfish-cbc", "aes192-cbc" ]
    SSH_FAST     = "no"
    SSH_TIMEOUT   = None  # ConnectTimeout in s
    BWU = 0
    BWD = 0
    MAX_LOG_SIZE = 100
    RDIFF_VERBOSITY = 5     # verbosity for log analysis 
    RDIFF_TMP_DIR = "rdiff-backup-data/tmp"


    def __init__(self,
        timeout = None,                 # timeout for whole rdiff-command
        ssh_timeout = SSH_TIMEOUT,       # ssh connection timeout
        ssh_port = None,
        ssh_user = None,
        ssh_pass = None,                # password for interactive ssh login
        fast_ssh = SSH_FAST,            # true, on, yes, 1 false, off, no, 0
        bwu      = BWU,                 # kbyte / sec
        bwd      = BWD,                 # kbyte / sec
        max_log_size = MAX_LOG_SIZE,    # Megabytes
        rdiff_verb = RDIFF_VERBOSITY,
    ):
        """
        Check some options an prerequisites. See class __doc__ for OPTIONS
        description.
        """
        # inital options   
        self.rdiff_options = self.RDIFF_OPTIONS

        # standard executables
        for exe in [self.LOGR_EXE, self.RDIFF_EXE]:
            if not validate_file.is_exe( exe ):
                raise RdiffSystemError(
                    "No read/exec access to '%s', check permissions and "
                    "installed packages." % exe
                )

        # bw limit: check cstream exe
        if bwu > 0 or bwd > 0:
            self.do_bwlimit = False
            if not validate_file.is_exe( self.CSTREAM_EXE ):
                raise RdiffSystemError(
                    "No read/exec access to '%s', check permissions and "
                    "installed packages!" % self.CSTREAM_EXE
                )

        self.error_log_entries  = validate.is_string_list( 
                                    self.ERROR_LOG_ENTRIES 
                                )
        self.bwd                \
            = bwd and validate.is_integer( bwd, 0 ) or None
        self.bwu                \
            = bwu and validate.is_integer( bwu, 0 ) or None
        self.max_log_size       = validate.is_integer( max_log_size )

        # verbosity options
        self.rdiff_options.append( 
            "--verbosity=%s" % validate.is_integer( rdiff_verb, 0, 9 ) 
        )

        # ssh options
        self.ssh_timeout = \
            ssh_timeout and validate.is_integer( ssh_timeout, 0 ) or None
        self.ssh_port    = \
            ssh_port and validate.is_integer( ssh_port, 0, self.SSH_MAX_PORT ) or None
        self.ssh_user    = \
            ssh_user and validate.is_string( ssh_user )     or None
        self.ssh_pass    = \
            ssh_pass and validate.is_string( ssh_pass )     or None
        self.fast_ssh    = \
            fast_ssh and validate.is_boolean( fast_ssh )    or None
        if ssh_pass is not None:
            self.ssh_pass = validate.is_string( ssh_pass )  or None

        # timeout setting
        self.timeout = timeout and validate.is_integer( timeout) or None
        if not timeout is None:
            log.debug ("Timeout: %s seconds" % self.timeout  )

    def start(
        self,
        source = None,
        target = None,
        rdiff_options   = [],
        ):

        # analyse source and target
        if not source is None:
            self.source = self._analyseaddr( source ) 
        if not target is None:
            self.target = self._analyseaddr( target ) 

        # set up initial options array
        rdiff_options = validate.is_string_list( rdiff_options )
        options       = self.rdiff_options + rdiff_options 


        # set up ssh and bw limit options
        if self.source['is_remote'] is True:
            options.append( self._get_ssh_options( self.source) )
        else:
            # check local source
            if not os.path.exists( self.source['path']):
                raise RdiffSystemError(
                    "Error checking local source '%s': not found" % self.source['path']
                )
        if self.target['is_remote'] is True:
            options.append( self._get_ssh_options( self.target) )
        else:
            # check local target
            if not os.path.exists( self.target['path']):
                try:
                    log.debug( "Creating target path '%s'" % self.target['path'] )
                    dir.touch( self.target['path'])
                except IOError, emsg:
                    raise RdiffSystemError(
                        "Error checking local target: '%s' not found " 
                        "and could not create it\n%s" % (self.target['path'], emsg)
                    )

        # set up target temp dir option
        options.append( self._setup_tmp_dir() )

        # finalize options, FIXME check for spaces and sort arry
        options.sort()

        # analyse given source and target
        if not source is None:
            options.append( self.source['addr_path'] )
        if not target is None:
            options.append( self.target['addr_path'] )
        else:
            raise RdiffOptionsError(
                "Target must be defined here, found target: '%s'" % target
            )

        log.info( "STARTING %s %s" % ( self.RDIFF_EXE, " ".join( options ) ) )
        self._run_rdiff_exe( options, self.timeout, )

    def stop(self):
        """ Try to stop running rdiff-backup process """
        raise NotImplemented( "Stop is not implemented" )


#----------------------------------------------------------------------------
# helpers
#----------------------------------------------------------------------------
    def _get_ssh_options(self, target):

        #Assemble all options for --remote-schema
        ssh_string = "--remote-schema '"

        # bwu
        if self.bwu > 0:
            log.debug( "Limiting upload bandwidth to %d byte/s" % self.bwu)
            ssh_string += ' %s -v 1 -t %d | ' % ( self.CSTREAM_EXE, self.bwu )

        # ssh start
        ssh_string += " ssh"

        # port
        ssh_port = target['port'] or self.ssh_port or ""
        if ssh_port != "":
            ssh_string += " -p %d " % ssh_port
            log.debug( "Alternate ssh port: %d" %  ssh_port )


        # compression and encoding
        if self.fast_ssh is True:
            ssh_string += " -c %s " % ','.join(self.FAST_SSH_CIPHERS)

        # connection timeout, see man ssh_config(5), ConnectTimeout
        ssh_string += self.ssh_timeout \
        and " -o ConnectTimeout=%s" % self.SSH_TIMEOUT or ""
            
        # bwd
        if self.bwd > 0:
            log.debug( "Limiting download bandwidth to %d byte/s" % self.bwd)
            ssh_string += ' | %s -v 1 -t %d ' % ( self.CSTREAM_EXE, self.bwd )

        ssh_string += " %s rdiff-backup --server'"
            
        return( ssh_string )


    def _analyseaddr(self, target ):
        """
        Return user, ssh port, addr, is_remote from given source or
        target definition
        """

        if not validate.is_string( target ):
            raise RdiffOptionsError(
                "address '%s' does not look like a string"
                % target
            )

        try:
            (user_addr_port, path) = target.split('::')
        except (IndexError,ValueError):
            is_remote  = False
            path = target
            addr_path = target
            port   = None
            passwd = None
            addr   = None
            log.debug( "Found local path '%s'" % path )
        else:
            is_remote  = True
            path = validate.is_string(path)
            try:
                user_addr, port = user_addr_port.split(':')
                port = validate.is_integer( port, 0, self.SSH_MAX_PORT )
            except (IndexError,ValueError):
                # no port
                user_addr   = user_addr_port
                port   = None
            try:
                user_passwd, addr = user_addr.split('@')
                addr = validate.is_string( addr )
                addr_path = addr + '::' + path
            except (IndexError,ValueError):
                # no user
                addr        = validate.is_string( user_addr )
                addr_path   = addr + '::' + path
                passwd = None
            else:
                # user, maybe password
                try:
                    user, passwd = user_passwd.split('%')
                    addr_path    = validate.is_string( user ) + '@' + addr_path
                    addr         = validate.is_string( user ) + '@' + addr
                    passwd       = validate.is_string( passwd )
                    passwd       = passwd.strip("'").strip('"')
                except (IndexError,ValueError):
                    # no passwd
                    addr_path   = "%s@%s" % ( 
                                validate.is_string( user_passwd ),
                                addr_path,
                                )
                    addr= "%s@%s" % ( 
                                validate.is_string( user_passwd ),
                                addr,
                                )
                    passwd = None
            log.debug( 
                "Found remote address '%s', port %s, password %s" 
                % ( addr_path, port, passwd and "given" or "not given" )
            )

        return{ 
            'addr_path' : addr_path,
            'is_remote': is_remote, 
            'port'     : port, 
            'passwd'   : passwd,
            'addr'     : addr,
            'path'     : path, 
        }
        
    def _setup_tmp_dir(self):
        """
        Check if temp dir exists, create if necessary
        return temp dir option
        """
        path = self.target['path'] + os.sep + self.RDIFF_TMP_DIR

        if self.target['is_remote'] is True:
            # remote target
            log.debug( 
                "Setting up remote temp dir '%s'" 
                % (self.target['addr_path'] + os.sep + self.RDIFF_TMP_DIR )
            )
#            self._run_target_ssh( self.target, [
#                    "mkdir",
#                    "-p", 
#                    '"%s"' % path, 
#                ]
#            )
            return( ["--remote-tempdir=%s" % path ])
        else:
#            # local target
            log.debug( "Setting up local temp dir '%s'" % path ) 
#            if not os.path.exists( path ):
#                try:
#                    os.makedirs ( path )
#                except OSError, emsg:
#                    raise RdiffSystemError( 
#                        "OS Error creating temp dir '%s'(%s)" % (path,emsg) 
#                    )
#            else:
#                if not os.path.isdir(path):
#                    raise RdiffSystemError( 
#                        "Some file already exists at temp dir location '%s'!"
#                        % path
#                    )
            return ("--tempdir=%s" % path )

    def _run_target_ssh(self, target, cmd):
        """ 
        Run a shell command at given remote site

        Input: target dict, cmd array
        Exceptions: RdiffSystemError in case ssh command goes wrong
        """
        cmd_array = [ self.target['addr'] ]
        if not self.ssh_user is None:
            cmd_array.append( "-l" )
            cmd_array.append( self.ssh_user )
        if not self.ssh_port is None:
            cmd_array.append( "-p" )
            cmd_array.append( "%s" % self.ssh_port )
        cmd_array.extend( cmd )

        cmd = "%s %s" % (self.SSH_EXE, ' '.join(cmd_array))

        if target['passwd'] is not None:
            raise NotImplemented(
                "Handing over ssh password is not implemented, use ssh keys"
            )

        log.debug( "Starting command '%s'" % cmd )
        if os.system( cmd) > 0:
            raise RdiffSystemError( 
                "Error running os system command '%s'" % cmd
            )

    def _run_rdiff_exe( self, options, timeout=None ):
        """run any rdiff-backup command, analyse output"""
        exception = False   # any exception ?
        run_error = False   # any error during rdiff-backup run?
        self.number_of_errors = 0

        try:
            for out in self._run_pexcept(options, timeout=timeout):
                # handle exceptions
                try:
                    rdiff_cmd_keyword = out.split()[0]
                except IndexError:
                    # ignore empty lines
                    continue

                if   out.startswith( "Processing"):
                    continue
                # handle error messages, ignore statistics error keyword
                elif rdiff_cmd_keyword == "Errors":
                    self.number_of_errors = validate.is_integer( out.split()[1],0 )
                elif "Error" in rdiff_cmd_keyword:
                    run_error = True
                    log.error( out )
                    continue

                # handle exception messages
                elif out.startswith( "Exception " ):
                    # Permission denied

                    # handle ignoring of full exception text
                    exception = True
                    run_error     = True
                    log.debug( out )
                    continue
                elif out.startswith( " ") and exception:
                    # skip handling exception trace
                    log.debug( out )
                    continue
                else:
                    exception = False

                # everything fine
                log.info( out)
        except RdiffRunError, emsg:
            run_error = True
        except KeyboardInterrupt:
            log.error("User Break")

        # Errors ?
        # check target repository (rdiff-backup -l)
        try:
            self._quick_check_target(timeout=timeout)
        except RdiffRunError, emsg:
            quick_check_ok = False
        else:
            quick_check_ok = True
            emsg = ""

        log.debug( 
            "Quick check (rdiff-backup -l) status: %s, run errors: %s " 
            % ( quick_check_ok and "ok" or "error" , run_error )
        )

        if run_error or not quick_check_ok:
            raise RdiffRunError( 
                "There have been errors running rdiff-backup.%s"
                % emsg
            )

    def _quick_check_target(self, timeout=None):
        """
        Run rdiff-backup -l at target repository to check if it is
        in proper state
        """
        options = [ 
            "--list-increments"     , 
            self.target['addr_path'], 
        ]
        try:
            for out in self._run_pexcept( options, timeout=timeout):
                log.debug( out )
        except RdiffRunError:
            raise RdiffRunError( 
                "Rdiff target '%s' is in bad state, run --check-destination!"
                % self.target['addr_path']
             )
        else:
            log.info( 
                "Checked state of rdiff target '%s': looks fine"
                % self.target['addr_path']    
            )


    def _run_pexcept( self, options, timeout=None ):
        """Call rdiff executable via pexcept, store process pid chain"""

        cmd = "%s %s" % (self.RDIFF_EXE, ' '.join(options) )
        log.debug( "Running system command '%s'" % cmd )
        session = Run( timeout=timeout)
        for line in session.start( cmd ): 
            yield line

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
        level        = logging.INFO,  
        file_file    = None,      # None = no file logging
        file_level   = logging.DEBUG,         
    )

    rd=Rdiff( fast_ssh=1, bwu=200000,  timeout = None, )
    rdo= ["--backup-mode", "--print-statistics" ]
    rd.start( rdiff_options = rdo, source = "/etc/ssl", target = "/home/gunnar/delme2")
