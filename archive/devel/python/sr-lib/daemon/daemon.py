#!/usr/bin/env python
# -*- coding: utf-8 -*-
#vim:fdm=marker
# unlock vim folding via zR, zo and lock folding via zM, zc
#----------------------------------------------------------------------------
"""                                                                     
DESCRIPTION     daemon class for running python scripts as daemons        {{{1

USAGE           call this script with -h or --help option
      
CHANGELOG    
   10-05-05     * log file now is getting touched in "append" mode
                * changed usage text and some other wording stuff

TODO
  * incorporate pt.lock library for pid file generation
  * operate in chroot jail
  * disable core file generation to prevent leaking sensitive information 
    in daemons run by root
    see http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/

"""

__version__ = "$Revision: 2010-05.b1$"
# $Source$


__all__ = [
    'Error',
    'PermissionError',
    'LockError',
    'Daemon',
]

#----------------------------------------------------------------------------
# modules import, constants                                              {{{1
#----------------------------------------------------------------------------
# standard
import sys
import os
import pwd
import grp
from   signal import SIGTERM,SIGKILL,signal,SIGCHLD,SIG_IGN
import traceback

# extra modules
 
# constants, default values
DEFAULT_PID_DIR = '/var/run'
VALID_COMMANDS  = [ 
    'start', 'stop', 'restart', 'reload', 'status', 'debug', 'zap', 'usage',
]

# logging
import logging
log = logging.getLogger( __name__ )


#----------------------------------------------------------------------------
# error class
#----------------------------------------------------------------------------
class Error(Exception):
    """General daemon handling error"""
class PermissionError(Error):
    """Daemon filesystem or users permission error"""
class LockError(Error):
    """Trying to start resp. stop a daemon which is resp. is not running"""
class SubclassError(Error):
    """Error running (user-defined) subclass method"""


#------------------------------------------------------------------------------
# main class
#------------------------------------------------------------------------------
class Daemon:
    """
    Usage: Daemon.handle_cmd( start|stop|restart|debug|status|zap )

    Options:
        pidfile  * false = define pid file name automatically
        stdin    * stdin  handler (default: /dev/null)
        stdout   * stdout handler (default: /dev/null or logfile)
        stderr   * stderr handler (default: /dev/null or logfile)
        user     * user[:group] to switch daemon to
        logfile  * default is to have no logfile but do
                    the logging from within (Run())
    """
    def __init__(   
        self, 
        callname = None,
        pidfile  = False,     
        stdin    = os.devnull,
        stdout   = os.devnull,
        stderr   = os.devnull,
        user     = None,      
        logfile  = None,      
    ):

        # check input parameters
        if callname is None:
            raise Error(
                "Need a callname for daemon process identification, "
                "please specify!"
            )

        # turn parameters to instance variables
        self.stdin      = stdin
        self.stdout     = stdout
        self.stderr     = stderr
        self.pidfile    = pidfile or os.path.join( DEFAULT_PID_DIR, callname )
        self.callname   = callname
        self.logfile    = logfile

        # prepare user setup
        if not user is None or user == '':
            if user.find(':') > 0:
                # group info contained here
                self.user   = user.split(':')[0]
                self.group  = user.split(':')[1]
            else:
                self.user   = user
                # primary group
                try:
                    self.group  = grp.getgrgid( pwd.getpwnam(user)[3] )[0]   
                except KeyError:
                    raise Error(
                        "Could not find user '%s', aborting" % user
                    )

        # method alias
        self.debug = self.foreground


    def _setup_logfile(self):
        """
        check log file setup, create file structure it if necessary, set permissions
        """

        log.debug( __doc__ )
        if not os.path.exists(self.logfile):
            # try touching file
            try:
                open(self.logfile, 'a').close() 
            except IOError:
                # houston we have a problem here: check if directory exists
                logdir = os.path.dirname(self.logfile)
                if not os.path.isdir( logdir ):
                    try:
                        os.makedirs( logdir )
                    except OSError, emsg:
                        raise Error( 
                            "Error creating directory '%s' for log file" % logdir 
                        )
                    # fine, retry creating log file now
                    try:
                        open(self.logfile, 'a').close() 
                    except Exception, emsg:
                        raise Error( 
                            "Could not create log file '%s'!" % self.logfile 
                        )
                else:
                    raise Error( 
                        "Strange: directory exists but can't create log file '%s'"
                        % self.logfile
                    )

        # log file exists now, set permissions
        if not self.user is None:

            # get user uid
            if self.group is None:
                self.group = self.user
            try:
                uid = pwd.getpwnam(self.user )[2]
                gid = grp.getgrnam(self.group)[2]
            except KeyError, emsg:
                raise Error( 
                    "user '%s' not found!" % (self.user, self.group) 
                )
            # set file owner and permission, leave group untouched
            try:
                os.chown( self.logfile, uid, gid)
                os.chmod( self.logfile, 0640)
            except OSError, emsg:
                raise PermissionError( 
                    "Not allowed to change permissions and owner for "
                    "log file '%s', try running with higher privilegues!\n%s" 
                    % ( self.logfile, emsg) 
                )


    def _daemonize(self):
        """
        do the UNIX double-fork magic, see Stevens' "Advanced 
        Programming in the UNIX Environment" for details (ISBN 0201563177)
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
        """

        # one common problem that people run into is os.fork() producing zombie
        # processes when children quit. This can easily be overcome by setting 
        # the SIGCHLD signal to SIG_IGN
        signal(SIGCHLD, SIG_IGN)

        try: 
            pid = os.fork() 
            if pid > 0:
                # exit first parent
                sys.exit(0) 
        except OSError, e: 
            raise Error(
                "fork #1 failed: %d (%s)" % (e.errno, e.strerror) 
            )
    
        # decouple from parent environment
        os.chdir("/") 
        os.setsid() 
        os.umask(0) 
    
        # do second fork
        try: 
            pid = os.fork() 
            if pid > 0:
                # exit from second parent
                sys.exit(0) 
        except OSError, e: 
            raise Error(
                "fork #2 failed: %d (%s)" % (e.errno, e.strerror)
            )
   
        # redirect stderr and stdout to handlers or logfile 
        # (logfile has highest prio)
        if not self.logfile is None:
            self._setup_logfile()
            self.stdout = self.logfile
            self.stderr = self.logfile

        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = file(self.stdin, 'r')
        so = file(self.stdout, 'a+')
        se = file(self.stderr, 'a+', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())
    
        # write pidfile
        pid = str(os.getpid())
        try:
            file(self.pidfile,'w+').write("%s" % pid)
        except IOError, emsg:
            raise PermissionError( 
                "Not allowed to change permissions and owner for "
                "log file '%s', try running with higher privilegues!\n%s" 
                % ( self.logfile, emsg) 
            )

    def status(self):
        try:
            pf = file(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        try:
            procfile = file("/proc/%d/status" % pid, 'r')
            procfile.close()
        except (IOError, TypeError):
            sys.stdout.write("%s is not running\n" % self.callname )
        else:
            sys.stdout.write("%s is running (PID %d)\n" % (self.callname, pid) )
        self.Status()


    def _drop_privilegues(self):
        """
        drop all privileges of the current process and set the privileges
        of the given user instead.
        """

        # return immediately in case there is nothing to do
        try:
            if self.user is None:
                return
        except AttributeError:
            return

        # get user uid, gid
        # take user name as group name in case group is not speecified
        if self.group is None:
            self.group = self.user
        try:
            uid = pwd.getpwnam(self.user )[2]
            gid = grp.getgrnam(self.group)[2]
            # find all other groups this user is member of, see os.setgroups
            other_groups = [ 
                entry[2] for entry in grp.getgrall() if self.user in entry [3] 
            ]

        except KeyError, emsg:
            raise Error( 
                "User '%s' or group '%s' not found!" % (self.user, self.group) 
            )

        try:
            os.setgroups(other_groups)
            os.setregid( gid, gid)
            os.setreuid( uid, uid)
        except OSError, emsg:
            raise PermissionError(
                "Failed to drop privileges, try running with higher "
                "privilegues\n%s" % emsg
            )
 

    def _check_start(self):
        """
        check if daemon is running already
        """
        # Check for a pidfile to see if the daemon already runs
        try:
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if pid:
            raise LockError( 
                "%s is already running ( locked by pidfile '%s' )" 
                % (self.callname, self.pidfile) 
            )
        
    def start(self):
        """
        Start the daemon in background
        """
        self._check_start()
        print "Starting %s ... " % self.callname
        self._daemonize()
        self._drop_privilegues()
        self.Run()


    def foreground(self):
        """
        Start the daemon in foreground
        """
        self._check_start()
        self._drop_privilegues()
        # prepare terminal buffering etc.
        import pt.terminal  
        try:
            self.Run()
        except KeyboardInterrupt:
            print "Debug user break ... stopping"
            sys.exit(0)
        


    def stop(self):
        """
        Stop the daemon
        """
        # Get the pid from the pidfile
        try:
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None
        

        if not pid :
            raise LockError( 
                "Cannot stop %s (pidfile '%s' not found)" 
                % (self.callname, self.pidfile) 
            )
            # not an error in a restart
            return 

        print "Stopping %s ..." % self.callname,
        # call user defined cleanup function
        self.Cleanup()

        # Try killing the daemon process    
        from time import sleep
        try:
            while 1:
                os.kill(pid, SIGTERM)
                sleep(0.1)
        except OSError, err:
            if "No such process" in str(err):
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                raise Error(
                    "Error soft - killing process %s, pidfile '%s'!\n%s"
                    % (pid, self.pidfile, err)
                )
        print "ok" 

    def restart(self):
        """
        Restart daemon
        """
        self.stop()
        self.start()

    def zap(self):
        """
        Kill daemon
        """
        # call user defined cleanup and zap function first
        # ignore errors
        try:
            self.Cleanup()
        except Exception, emsg:
            log.error( "Error running user defined Cleanup()\n%s" % emsg )
        try:
            self.Zap()
        except Exception, emsg:
            log.error( "Error running user defined Zap()\n%s" % emsg )
            pass


        # Get pid from pidfile
        try:
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None
        

        # handle not existing pid file
        if not pid :
            raise LockError( 
                "%s can not get stopped (pidfile '%s' not found)" \
                % (self.callname, self.pidfile) 
            )

        # kill daemon unfriendly
        print "zapping %s ..." % self.callname,
        from time import sleep
        try:
            while 1:
                os.kill(pid, SIGTERM)
                sleep(0.1)
        except OSError, err:
            if "No such process" in str(err):
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
                print "ok"
                print "Z's dead, Baby, Z's dead"
            else:
                raise Error(
                    "Error hard - killing process %s, pidfile '%s'!\n%s"
                    % (pid, self.pidfile, err)
                )

    def reload(self):
        self._callSubClassMethod( self.Reload() )


    def handle_cmd(self, cmd=None):
        """
        Start daemon given command if possible. Start user defined Run()
        method in case cmd is None.
        """
       
        if cmd is None:
            log.debug( "No daemon command specified, starting with no daemon" )
#            self._callSubClassMethod( "Run") 
            self.Run()
                
        if not cmd in VALID_COMMANDS:
            raise Error(
                "Command '%s' does not look like a daemon command, "
                "you may want to use one of %s" 
                % ( cmd, ', '.join(VALID_COMMANDS) )
            )

        method_ref=getattr(self,cmd)
        method_ref()


    def usage(self):
        """
        General usage text for a daemon, you may want to override this.
        """
        progname = os.path.split(sys.argv[0])[1]

        print "Usage: %s COMMAND [-L LOGFILE] [ -P PIDFILE] [-U USER[:GROUP]]" % progname
        print "CMD is one of start|stop|restart|reload|status|debug|zap"
        print
        print "COMMAND   :"
        print "  start, stop * start or stop service daemon"
        print "  restart     * restart if running, start otherwise"
        print "  reload      * reload config, leave daemon running"
        print "  debug       * print all output to terminal, run in foreground"
        print "  zap         * forced reset (kill daemon, remove pidfile)"
        print
        print "LOGFILE    : file where output should be written to (optional)"
        print "PIDFILE    : file where daemon process id is stored (optional)"
        print "USER:GROUP : user [and group ]to run daemon as ( optional )"

    #-------------------------------------------------------------------------
    # subclass announcers
    #-------------------------------------------------------------------------

    def Status(self):
        """This method is called at begin of Daemons status() method."""

        raise NotImplemented(
            self.Status.__doc__ + "\nYou should override this "
            "method when you subclass Daemon !"
        )

    def Zap(self):
        """
        This method is called at begin of dameonizers's zap 
        method, after Cleanup().
        """

        raise NotImplemented(
            self.Zap.__doc__ + "\nYou should override this "
            "method when you subclass Daemon !"
        )
    def Cleanup(self):
        """
        Cleanup() will be called at the time the daemon's process 
        is stopped.
        """
        raise NotImplemented(
            self.Cleanup.__doc__ + "\nYou should override this "
            "method when you subclass Daemon !"
        )

    def Run(self):
        """
        Run() will be called after the process has been daemonized by 
        start() or restart().
        """
        raise NotImplemented(
            self.Run.__doc__ + "\nYou should override this "
            "method when you subclass Daemon !"
        )

    def Reload(self):
        """
        Restarting service now (calling self.restart()) .
        """

        raise NotImplemented(
            self.Reload.__doc__ + "\nYou should override this "
            "method when you subclass Daemon !"
        )




#------------------------------------------------------------------------------
# example usage 
#------------------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    print "This module is not meant to be called directly, see init-script"
    print "how to call this module from python scripts" 
    sys.exit(1)


