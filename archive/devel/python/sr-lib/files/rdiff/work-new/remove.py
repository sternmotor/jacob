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
    'RdiffError',
    'RdiffBackupTimeoutError',
    'RdiffOptionsError',
    'RdiffFatalError',
    'RdiffFinishedError',
    'RdiffBusyError',
    'RdiffSystemError',
    'RdiffNetworkError',
]

# standard
import logging
log = logging.getLogger( __name__ )
import os


# extra modules
#import pt.syscmd  # shell command handler ( subprocess )
from pt.files import validate_file
from pt import fs
from pt.data  import validate   # data validator
#from pt.syscmd import syscmd
import pexpect


#----------------------------------------------------------------------------
# error classes                                                          {{{1
#----------------------------------------------------------------------------
class RdiffError(Exception):
    """All Errors during rdiff-backup call"""

# network errors
class RdiffNetworkError(RdiffError):
    """Timeout during ssh connection setup or other network error"""

class RdiffBackupTimeoutError(RdiffError):
    """Timeout during network connection setup"""

class RdiffOptionsError(RdiffError):
    """Wrong options to Rdiff class methods"""

class RdiffFatalError(RdiffError):
    """Fatal condition found during rdiff run"""

class RdiffFinishedError(RdiffError):
    """Rdiff finished but there have been errors"""

class RdiffBusyError(RdiffError):
    """Rdiff backup session running on target"""

class RdiffRemoteServerError(RdiffError):
    """Errors checking remote rdiff server"""

# errors running shell commands
class RdiffSystemError(RdiffError):
    """Pre - or Post backup command failed at remote site"""


#----------------------------------------------------------------------------
# main class                                                             {{{1
#----------------------------------------------------------------------------
class Rdiff:
    """
    DESCRIPTION
      rdiff-backup wrapper for starting one backup action (no profile handling),
      maintaining logging, bandwidth control


    FEATURES
        * bandwidth control for local and remote operation
        * ssh port, encryption, compression control
        * retry regime for connection setup
        * log analysis, proper error handling, smart job control
        * logging control (log rotation)
        * repository checking, log file handling, status log creation
        * useful default excludes
        * verbosity settings via python log handler
        * separate error, short and full log
        * temp dir handling: 
            * if target is local, temp dir is rdiff-backup-data/tmp
            * if target is remote, temp dir is rdiff-backup-data/tmp
        * timeout for backup run


        NOT included ( too big for this one)
        * backup repository rotation
        * backup repository splitter
        * job control (start stop background operation)
        * debug (foreground operation)
        * target and source pre/post scripts

    OPTIONS
        excludes = array of rdiff-backup --exclude-regexp expressions
        includes = --include-regexp expressions

        rdiff_options=[], array of rdiff-backup extra options
        error_log_entries = ERROR_LOG_ENTRIES,
        ssh_port = SSH_PORT,
        ssh_user = SSH_USER,
        ssh_fast = SSH_ENC,     # true, on, yes, 1 false, off, no, 0
            * true: turn compression, encrpytion off
        bwu = BWU,      initial bandwidh limit        # kbyte / sec
        bwd = BWD,     initial bandwidh limit         # kbyte / sec
        max_log_size = MAX_LOG_SIZE,    # Megabytes
            maximum size for backup.log, backup_short.log (Mbyte)
        log_verb = LOG_VERBOSITY,
        dis_verb = DIS_VERBOSITY,
    
    METHODS
        update(source, target, as_date) 
            * Copy next increment resp. create backup repository
            * run check
            
        
            path, source, target 
            * directories or remote location where to run action
                [[user[%passwd]@]host::]PATH
        stop(target) try to kill running rdiff-backup session

        purge(max age, date )
            * remove old snapshots
        restore (age, date, mirror path, target)
            * restore snapshot to target dir
        check(target)     
            * Check and repair backup repository
            * update statistics, log-rotation            
            * Empty out temp dir
           
        status(target)     
            * finished increments, increment sizes, total size from last check
            * running: show short log, finished stats when finished

        bwd()       
            * Tune read   bandwidth (download) live (kBit/s)
        bwu()       
            * Tune write  bandwidth (upload)   live (kBit/s)

        list()       show all increments and sizes, less accurate but very fast
        list_accurate()   show all increments and sizes - very accurate but takes ages


    EXCEPTIONS
    LOGGING
        Logging is done with verbosity 6 to "rdiff-backup-data/backup.log" and 
        verbosity 4 to "rdiff-backup-data/backup_short.log". At "check" run, 
        "rdiff-backup-data/status.log" is written. All logs get rotated in "check" run.

    EXAMPLE
    """

    # class constants:
    CSTREAM_EXE = "/usr/bin/cstream"
    SSH_EXE     = "/usr/bin/ssh"
    RDIFF_EXE   = "/usr/bin/rdiff-backup"
    LOGR_EXE    = "/usr/sbin/logrotate"

    EXCLUDES = [
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
    RDIFF_START_OPTIONS= [
        r'--preserve-numerical-ids'  ,
        r'--print-statistics'        ,
        r'--backup-mode'             ,
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
    SSH_TIMEOUT   = "60"  # ConnectTimeout
    BWU = 0
    BWD = 0
    MAX_LOG_SIZE = 100
    RDIFF_VERBOSITY = 5     # verbosity for log analysis 
    RDIFF_TMP_DIR = "rdiff-backup-data/tmp"


    def __init__(self,
        excludes        = [],
        regexp_excludes = [],
        includes        = [],
        regexp_includes = [],
        rdiff_options   = [],
        ssh_port = None,
        ssh_user = None,
        ssh_pass = None,
        fast_ssh = SSH_FAST,         # true, on, yes, 1 false, off, no, 0
        bwu      = BWU,              # kbyte / sec
        bwd      = BWD,              # kbyte / sec
        max_log_size = MAX_LOG_SIZE, # Megabytes
        rdiff_verb = RDIFF_VERBOSITY,
    ):
        """
        Check some options an prerequisites. See class __doc__ for OPTIONS
        description.
        """
           
        # standard executables
        for exe in [self.LOGR_EXE, self.RDIFF_EXE]:
            if not validate_file.is_exe( exe ):
                raise RdiffSystemError(
                    "No read/exec access to '%s', check permissions and "
                    "installed packages. Need \n%s."
                    % ( exe, '\n'.join(self.EXECUTABLES)  )
                )

        # bw limit: check cstream exe
        if bwu > 0 or bwd > 0:
            self.do_bwlimit = False
            if not validate_file.is_exe( self.CSTREAM_EXE ):
                raise RdiffSystemError(
                    "No read/exec access to '%s', check permissions and "
                    "installed packages!" % self.CSTREAM_EXE
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
        self.rdiff_options      = validate.is_string_list( rdiff_options )
        self.error_log_entries  = validate.is_string_list( 
                                    self.ERROR_LOG_ENTRIES 
                                )
        if not ssh_pass is None:
            self.ssh_pass       = validate.is_string( ssh_pass )
        self.fast_ssh           = validate.is_boolean( fast_ssh )
        self.bwu                = validate.is_integer( bwu, 0 ) 
        self.bwd                = validate.is_integer( bwd, 0 ) 
        self.max_log_size       = validate.is_integer( max_log_size )

        # verbosity tests
        self.rdiff_options.append( 
            "--verbosity=%s" % validate.is_integer( rdiff_verb, 0, 9 ) 
        )


        # check pylibacl and pyxattr
        # remote backup: check ssh exe


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

        
#----------------------------------------------------------------------------
# update helpers
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
        ssh_string += target['port'] and " -p %d " % target['port'] or ""


        # compression and encoding
        if self.fast_ssh is True:
            ssh_string += " -c %s " % ','.join(self.FAST_SSH_CIPHERS)

        # connection timeout, see man ssh_config(5), ConnectTimeout
        if self.SSH_TIMEOUT > 0:
            ssh_string += " -o ConnectTimeout=%s" % self.SSH_TIMEOUT
            
        # bwd
        if self.bwd > 0:
            log.debug( "Limiting download bandwidth to %d byte/s" % self.bwd)
            ssh_string += ' | %s -v 1 -t %d ' % ( self.CSTREAM_EXE, self.bwd )

        ssh_string += " %s rdiff-backup --server'"
            
        return( ssh_string )

    def _check_clude(self, cludes, option_string):
        return_array = []
        for clude in cludes:
            return_array.append( "%s=%s" % (option_string, clude) )
        return return_array

#----------------------------------------------------------------------------
# common helpers
#----------------------------------------------------------------------------
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
                addr_path = host + '::' + path
            except (IndexError,ValueError):
                # no user
                addr        = validate.is_string( user_addr )
                addr_path   = addr + '::' + path
                passwd = None
            else:
                try:
                    user, passwd = user_passwd.split('%')
                    addr_path    = validate.is_string( user ) + '@' + addr_path
                    passwd       = validate.is_string( passwd )
                    passwd       = passwd.strip("'").strip('"')
                except (IndexError,ValueError):
                    # no passwd
                    addr_path   = "%s@%s" % ( 
                                validate.is_string( user_passwd ),
                                '@',
                                addr_path,
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
        
    def _get_tmp_dir(self):
        """
        Check if temp dir exists, create if necessary
        set temp dir option
        """
        path = self.target['path'] + os.sep + self.RDIFF_TMP_DIR

        if self.target['is_remote'] is True:
            # remote target
            log.debug( 
                "Setting up remote temp dir '%s'" 
                % (self.target['addr_path'] + os.sep + self.RDIFF_TMP_DIR )
            )
            self._run_target_ssh( """mkdir -p "%s" """ % path )
            return( ["--remote-tempdir=%s" % path ])
        else:
            # local target
            log.debug( "Setting up local temp dir '%s'" % path ) 
            if not os.path.exists( path ):
                try:
                    os.makedirs ( path )
                except OSError, emsg:
                    raise RdiffSystemError( 
                        "OS Error creating temp dir '%s'(%s)" % (path,emsg) 
                    )
            else:
                if not os.path.isdir(path):
                    raise RdiffSystemError( 
                        "Some file already exists at temp dir location '%s'!"
                        % path
                    )
            return (["--tempdir=%s" % path ])

                        
    def _run_target_ssh(self, cmd):
        syscmd( [ self.SSH_EXE, self.target['addr'], cmd ] )
#        # passwd
#        if target['passwd'] is not None:
#            raise NotImplemented(
#                "Handing over ssh password is not implemented, use ssh keys"
#            )

    def _run_rdiff_exe( self, options, source=None, target = None, timeout=None ):
        """run any rdiff-backup command"""

        # check input, announce rdiff-backup command and options
        log.debug ("Starting '%s'" % self.RDIFF_EXE )
        tmp_opts = options
        if not source is None:
            log.debug ("Source: '%s'" % source)
            tmp_opts += [ source ]
        if not target is None:
            log.debug ("Target: '%s'" % target)
            tmp_opts += [ target ]
        if not timeout is None:
            timeout = validate.is_integer( timeout)
            log.debug ("Timeout: %s seconds" % timeout  )

        log.debug ("Options: %s"  % " ".join( sorted( options )  ) )

        cmd_h = pexpect.spawn( self.RDIFF_EXE, tmp_opts, timeout=timeout)
        while True:
            try:
                out = cmd_h.readline()
                if out =='':
                    continue
                print out.rstrip()
            except pexpect.EOF:
                break


#        # passwd
#        if target['passwd'] is not None:
#            raise NotImplemented(
#                "Handing over ssh password is not implemented, use ssh keys"
#            )


#        for out,err in syscmd( 
#            [ self.RDIFF_EXE ] + options + [ source, target ], pipe=True ):
#            [ "./delme" ], pipe=True ):
#            print  "OUT: %s " % out
#            print  "ERR: %s " % err

        

#        child = pexpect.spawn(cmd, timeout=None)
#        while True:
#            try:
#                out = child.readline()
#                if out =='':
#                    continue
#                print out.rstrip()
#            except pexpect.EOF:
#                break


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

    rd=Rdiff( fast_ssh=1, bwu=200000)
    rd.update(source = "/etc", target = "/tmp/delme", timeout = None )
