#!/usr/bin/env python
# -*- coding: utf-8 -*-
#vim:fdm=marker 
# unlock vim folding via zR, zo and lock folding via zM, zc
#----------------------------------------------------------------------------
"""                                                                     
 DESCRIPTION  * simple wrapper for rdiff backup, making it available for {{{1
                 python scripts and setting some defaults
              *  see pydoc rdiff_backup.Main
 USAGE        
       
 CHANGELOG    
    2010-01-31 * creation, copied from /usr/bin/rdiff-backup

 TODO
 
 THANKS TO

"""

__version__ = "$Revision: 0.1.2010-01-31 $"
# $Source$

 
#----------------------------------------------------------------------------
# modules import, constants                                              {{{1
#----------------------------------------------------------------------------
# standard
import sys
import os

try:
    import msvcrt, os
    msvcrt.setmode(0, os.O_BINARY)
    msvcrt.setmode(1, os.O_BINARY)
except ImportError:
    pass


# extra modules
from fly.files.filetools import FileToolsError, touchDir


# constants, default values
CSTREAM_EXE        = '/usr/bin/cstream' 
CSTREAM_OPTIONS    = "-v 1 -t " # + bw limit in kb/sec
SSH_EXE            = "/usr/bin/ssh"
RDIFF_DIR          = 'rdiff-backup-data' 
TEMP_DIR           = 'tempdir'
LOG_FILE           = 'backup.log'
LOCK_FILE          = 'backup.lock'
FLAG_ERROR_FILE    = 'backup.error'
FLAG_RUNNING_FILE  = 'backup.running'
FLAG_FINISHED_FILE = 'backup.finished'
LOG_VERBOSITY      = 5
DIS_VERBOSITY      = 4
MIN_RDIFF_VERSION  = '1.2.0' 

 
exclude_regexps = (
    r'rdiff-backup-data'         ,
    r'RECYCLER'                  ,
    r'RECYCLE.BIN'               ,
    r'System Volume Information' ,
    r'.recycle'                  ,
    r'lost+found'                ,
    r'.tmp$'                     ,
    r'.TMP$'                     ,
    r'.Thumbs.db$'               ,
    r'Trashes'                   ,
)

standard_options = (
    '--print-statistics'        ,
    '--backup-mode'             ,
    '--preserve-numerical-ids'  ,
)

#----------------------------------------------------------------------------
# main classes                                                           {{{1
#----------------------------------------------------------------------------

class RdiffBackupError(Exception):
    pass

class RdiffBackup:
    def __init__(self,
                  source = None, target = None , 
                  bw_push   = None  , 
                  bw_pull   = None  , 
                  extra     = None  , 
                  ssh_port  = '22'  , 
                  log_verb  = LOG_VERBOSITY,
                  dis_verb  = DIS_VERBOSITY,
                  timeout   = None  , 
        ):
        """
        Rdiff wrapper, setting some standard options, allow bandwidth limits,
        background operation and log file rotatition. Verbosity levels are: 5 
        for internal log in rdiff-backup dir and 4 for displayed log.
        Furthermore it takes care of proper temp directory location for 
        regression run, if needed (rdiff_backup > 1.2.5).
        All methods below work local or remote, make sure to have ssh keys
        for source or target user in place.

        PUBLIC METHODS
            start()       * start backup in foreground, return an iterator
                            for displaying backup log lines
            startThread() * start backup in background thread, 
                            return immediately, no display logging
            stop()        * stop backup running in background
            status()      * return status of current backup
                            True: finished, None: running, False: Error
            removeOlderThan( date ) * specify date as yy-mm-dd
            checkDestination()      * check if target is clean, run regression
                                      if necessary. True = ok, raise on error
            listIncrements()        * guess what!
            listIncrementSizes()    * see above

        On errors, RdiffBackupError is raised.

        PARAMETERS
            source,target * remote or local source and target, specify
                            like [USER@]addr[:PORT]::DIRECTORY, 
            bw_push       * bw limit sending data to target, default: None
            bw_pull       * bw limit getting data from client, default: None
            extra         * extra options, see man rdiff_backup
            log_verb      * log verbosity, default 5
            dis_verb      * display verbosity, default 4
            timeout       * timeout for whole backup process (sec)
        """
        # initiate logging
        self.log = logging.getLogger(
            "%s.%s" % (__name__,self.__class__.__name__) 
        )

        # roughly check input
        if source is None or target is None:
            raise RdiffBackupError(
                "Missing source or target definition or both, try harder!"
            )

        # get user, ssh port, addr, is_remote
        self.source = self._analyseaddr( source ) 
        self.log.debug( "source: %s" % self.source )
        self.target = self._analyseaddr( target )
        self.log.debug( "target: %s" % self.target )

        # initiate rdiff
        try:
            import rdiff_backup.Main
        except ImportError:
            raise RdiffBackupError(
                "Could not import, try 'aptitude install rdiff_backup!"
            )
        # check rdiff_backup version
        version = rdiff_backup.Main.Globals.version
        if version < MIN_RDIFF_VERSION:
            raise RdiffBackupError(
                "Please update your rdiff-backup software, minimum "
                "required version is '%s' but '%s' was found!" 
                % ( MIN_RDIFF_VERSION, version )
            )

        # check if backup should run remote
        if self.source[ 'is_remote' ] or self.target[ 'is_remote' ]:
            self.has_remote = True
            # initiate ssh connections
            self._check_exe( SSH_EXE )
            self.log.debug( 'running remote' )
        else:
            self.log.debug( 'running local' )
            self.has_remote = False

        # initiate bandwidth limiter
        if (bw_push is not None) or ( bw_pull is not None ) and self.has_remote: 
            self._check_exe( CSTREAM_EXE )
            self.log.debug( 'running bandwidth limited' )
            self.bw_push = self._checkIntParameter( bw_push, 'push bandwidth' )
            self.bw_pull = self._checkIntParameter( bw_pull, 'pull bandwidth' )

        # initiate timeout
        if ( timeout is None ) or ( timeout == 0 ) or (timeout == False):
            self.timeout = None
        else:
            self.log.debug( 'running with timeout' )
            self.timeout = self._checkIntParameter( timeout, 'backup timeout' )
            try:
                from fly.run.thread_timeout import timelimited,TimeLimitExpired
            except ImportError:
                self._handle_error(
                    "Could not import thread_timeout library, try to install "
                    "secu-ring fly python package first or leave timeout None"
                )

        # initate file ad dir locations relative to rdiff-backup-dir
        self.temp_dir       = self.target['path'] + os.sep + RDIFF_DIR + os.sep + TEMP_DIR           
        self.log_file       = self.target['path'] + os.sep + RDIFF_DIR + os.sep + LOG_FILE           
        self.error_file     = self.target['path'] + os.sep + RDIFF_DIR + os.sep + FLAG_ERROR_FILE    
        self.running_file   = self.target['path'] + os.sep + RDIFF_DIR + os.sep + FLAG_RUNNING_FILE  
        self.finished_file  = self.target['path'] + os.sep + RDIFF_DIR + os.sep + FLAG_FINISHED_FILE 
            
            
#        try:
#            return timelimited(
#                timeout,
 #               _start,
#                full_cmd, getout, expand, stdin, stdout, stderr ,
#            )
#        except TimeLimitExpired:
    def start(self):
        """Start backup"""

    def startThread(self):
        """start backup in background"""

    def stop(self):
        """Stop the backup thread running in background"""

    def status(self):
        """Print status of latest or current backup run"""

    def checkDestination(self):
        """
        Run rdiff_backup_check destination on target, return True in case
        target is clean or raise RdiffBackupErrror in case not
        """

    def removeOlderThan(self, max_data ):
        """
        Remove all backups older than specified date yyyy-mm-dd
        """

    def listIncrements(self):
        """yes, exactly what you'll find in rdiff-backup manpage"""

    def listIncrementSizes(self): 
        """yes, exactly what you'll find in rdiff-backup manpage"""

#    def _runLocal(self, shell_cmd):
#        """run shell command locally, return (exit code, output)"""
#
    def _runRemote(self, shell_cmd):
        """run shell command remotely, return (exit code, output)"""

#    def _runAtTarget(self, shell_cmd):
#        """run shell command remotely or locally, return (exit code, output)"""
#        if self.target['is_remote']:
#            return self._runRemote( shell_cmd )
#        else:
#            return self._runLocal( shell_cmd )

    def _analyseaddr(self, target ):
        """
        return user, ssh port, addr, is_remote
        """
        try:
            (user_addr_port, path) = target.split('::')
        except (IndexError,ValueError):  
            is_remote = False
            user      = None
            user_addr = 'localhost'
            addr   = None
            port      = None
            path      = target
        else:
            is_remote = True
            log.debug( "found remote addr: '%s'" % target )
            try:
                user_addr, port = user_addr_port.split(':')
            except (IndexError,ValueError):  
                # no port
                user_addr = user_addr_port
                port = None
                
            try:
                user, addr = user_addr.split('@')
            except (IndexError,ValueError):  
                # no user
                addr = user_addr
                user    = None

        if target is None:
            self._handleError( "Source or target not defined!" )

        return {
            'user'      : user      ,
            'addr'      : addr   ,
            'user_addr' : user_addr, 
            'port'      : port      ,
            'path'      : path      ,
            'is_remote' : is_remote ,
        }



    def _check_exe(self, fpath ):
        if os.path.exists(fpath) and os.access(fpath, os.X_OK):
            return True
        else:
            self.handleError( "executable '%s' not found!" % fpath )

    def _checkIntParameter( self, number, name ):
        try:
            return int ( number )
        except ValueError:
            self._handleError( "Wrong value '%s' for %s" % ( number, name ) )
        except TypeError:
            return None

    def _handleError(self, msg):
        log.debug( msg )
        raise RdiffBackupError( msg )
    
#----------------------------------------------------------------------------
# test structure                                                         {{{1
#----------------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    import os
    import logging

    log = logging.getLogger()
    log.addHandler(logging.StreamHandler())    
    log.setLevel(logging.DEBUG)

#    log.debug( "HAHA")
    rdb = RdiffBackup( '/etc/', '/tmp/etc2', bw_push="22", timeout="23"  )
    #rdb = RdiffBackup( '/etc/', 'lal@localhost:34::/tmp/etc', bw_push="22", timeout="23"  )
    rdb.start()
#    rdiff_backup.Main.Main(['--backup-mode', '/etc/', '/tmp/etc'])
