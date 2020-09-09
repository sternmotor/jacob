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
  * operate in chroot jail
  * disable core file generation to prevent leaking sensitive information 
    in daemons run by root
    see http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/

"""

__version__ = "$Revision: 2010-05.b1$"
# $Source$


__all__ = [
    'DaemonError',
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

# extra modules
 
# constants, default values

# logging
import logging
log = logging.getLogger( __name__ )


#----------------------------------------------------------------------------
# error class
#----------------------------------------------------------------------------
class DaemonError(Exception):
    pass


#------------------------------------------------------------------------------
# main class
#------------------------------------------------------------------------------
class Daemon:
    """
    Usage: subclass the Daemon class and override the following methods:
    Run() Status() Zap() Cleanup() Reload() Usage()

    Then, the following commands are available like "instance.start()" :
      start|stop|restart|reload|status|debug|zap

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
        callname = os.path.split(sys.argv[0])[1], 
        pidfile  = False,     
        stdin    = os.devnull,
        stdout   = os.devnull,
        stderr   = os.devnull,
        user     = None,      
        logfile  = None,      
    ):


        # turn parameters to instance variables
        self.stdin      = stdin
        self.stdout     = stdout
        self.stderr     = stderr
        self.pidfile    = pidfile or os.path.join( '/var/lock/', callname )
        self.callname   = callname
        self.logfile    = logfile

        # prepare user setup
        if not user is None:
            if user.find(':') > 0:
                # group info contained here
                self.user   = user.split(':')[0]
                self.group  = user.split(':')[1]
            else:
                self.user   = user
                # primary group
                self.group  = grp.getgrgid( pwd.getpwnam(user)[3] )[0]   
        
    def setup_logfile(self):
        """
        check log file setup, create file structure it if necessary, set permissions
        """

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
                        raise DaemonError( 
                            "Error creating directory '%s' for log file" % logdir 
                        )
                    # fine, retry creating log file now
                    try:
                        open(self.logfile, 'a').close() 
                    except Exception, emsg:
                        raise DaemonError( 
                            "Could not create log file '%s'!" % self.logfile 
                        )
                else:
                    raise DaemonError( 
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
                raise DaemonError( 
                    "user '%s' not found!" % (self.user, self.group) 
                )
            # set file owner and permission, leave group untouched
            try:
                os.chown( self.logfile, uid, gid)
                os.chmod( self.logfile, 0640)
            except Exception, emsg:
                raise DaemonError( 
                    "Could not set permissions for log file (%s)!" % emsg 
                )


    def daemonize(self):
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
            raise DaemonError(
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
            raise DaemonError(
                "fork #2 failed: %d (%s)" % (e.errno, e.strerror)
            )
   
        # redirect stderr and stdout to handlers or logfile 
        # (logfile has highest prio)
        if not self.logfile is None:
            self.setup_logfile()
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
        file(self.pidfile,'w+').write("%s" % pid)

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
        except IOError:
            raise DaemonError(
                "'%s' with PID in '%s' is not running" 
                % (self.callname, self.pidfile) 
            )
        except TypeError:
            raise DaemonError("%s is stopped" % self.callname )

        sys.stdout.write("%s is running (PID %d)" % (self.callname, pid) )
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
            raise DaemonError( 
                "user '%s' or group '%s' not found!" % (self.user, self.group) 
            )
            sys.exit(1)

        try:
            os.setgroups(other_groups)
            os.setregid( gid, gid)
            os.setreuid( uid, uid)
        except OSError, emsg:
            raise DaemonError("Failed to drop privileges (%s)" % emsg)
            sys.exit(1)

 

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
            raise DaemonError( 
                "%s is already running ( locked by pidfile '%s' )" 
                % (self.callname, self.pidfile) 
            )
            sys.exit(1)
        
    def start(self):
        """
        Start the daemon in background
        """
        self._check_start()
        print "Starting %s" % self.callname
        self.daemonize()
        self._drop_privilegues()
        self.Run()

    def foreground(self):
        """
        Start the daemon in foreground
        """
        self._check_start()
        self._drop_privilegues()
        self._prepare_terminal()
        self.Run()


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
            raise DaemonError( 
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
                print str(err)
                sys.exit(1)
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
            print "Error running user defined Cleanup()\n%s" % emsg
            print "-----"
        try:
            self.Zap()
        except Exception:
            print "Error running user defined Zap()\n%s" % emsg
            pass

        # Get the pid from the pidfile
        try:
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None
        

        # handle not existing pid file
        if not pid :
            raise DaemonError( 
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
                print str(err)
                sys.exit(1)

    def reload(self):
        self.Reload()

    def _prepare_terminal(self):
        import pt.terminal  



    def Status(self):
        """
        You should override the Status() method when you subclass 
        Daemon. This method is called at begin of dameonizers's status()
        method.
        """
        print self.Status.__doc__

    def Zap(self):
        """
        You should override the Zap() method when you subclass 
        Daemon. This method is called at begin of dameonizers's zap 
        method, after Cleanup().
        """
        print self.Zap.__doc__

    def Cleanup(self):
        """
        You should override the Cleanup() method when you subclass Daemon.  
        Cleanup() will be called at the time the daemon's process 
        is stopped.
        """
        print self.Cleanup.__doc__

    def Run(self):
        """
        You should override the Run() method when you subclass Daemon.
        run() will be called after the process has been daemonized by 
        start() or restart().
        """
        print self.Run.__doc__

    def Reload(self):
        """
        You should override the Reload() method when you subclass Daemon.
        Restarting service now (calling self.restart()) .
        """
        print self.Reload.__doc__
        self.restart()

    def Usage(self):
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

#------------------------------------------------------------------------------
# example usage 
#------------------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    print "This module is not meant to be called directly, see init-script"
    print "how to call this module from python scripts" 
    sys.exit(1)


