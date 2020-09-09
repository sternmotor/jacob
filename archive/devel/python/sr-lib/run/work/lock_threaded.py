#!/usr/bin/env python
# -*- coding: utf-8 -*-
#vim:fdm=marker
# unlock vim folding via zR, zo and lock folding via zM, zc
#----------------------------------------------------------------------------
"""                                                                     
The lockfile module exports a FileLock class which provides a simple API for locking files. Unlike the Windows msvcrt.locking function, the Unix fcntl.flock, fcntl.lockf and the deprecated posixfile module, the API is identical across both Unix (including Linux and Mac) and Windows platforms. The lock mechanism relies on the atomic nature of the link (on Unix) and mkdir (on Windows) system calls.

Furthermore content of lockfile is accessible as cjson object

USAGE          see __doc__ strings or test section for example use
      
CHANGELOG    
    2010-08
        * added storage capability to lock handler: write info like
          process and childs or other stuff directly into lock file
TODO

THANKS TO

"""

__version__ = "$Revision: 0.1.2010-08-17 $"
# $Source$


#----------------------------------------------------------------------------
# modules import, constants                                              {{{1
#----------------------------------------------------------------------------

# module export
__all__ = ['Error', 'LockError', 'LockTimeout', 'AlreadyLocked',
           'LockFailed', 'UnlockError', 'NotLocked', 'NotMyLock',
           'LinkFileLock', 'MkdirFileLock', 'SQLiteFileLock', 'UpdateError',]

# standard
import sys
import socket
import os
import thread
import threading
import time
import errno
import urllib

import logging
log = logging.getLogger( __name__ )

# extra modules
# Work with PEP8 and non-PEP8 versions of threading module.
if not hasattr(threading, "current_thread"):
    threading.current_thread = threading.currentThread
if not hasattr(threading.Thread, "get_name"):
    threading.Thread.get_name = threading.Thread.getName
#from pt.syscmd    import *   # shell command handler ( subprocess )
#from pt.config    import *   # configfile handler

# constants
 
#----------------------------------------------------------------------------
# error classes                                                          {{{1
#----------------------------------------------------------------------------
"""
Exceptions:

* Error - base class for other exceptions
* LockError - base class for all locking exceptions
    AlreadyLocked - Another thread or process already holds the lock
    LockFailed - Lock failed for some other reason
* UnlockError - base class for all unlocking exceptions
    AlreadyUnlocked - File was not locked.
    NotMyLock - File was locked but not by the current thread/process
"""
class Error(Exception):
    pass
class LockError(Error):
    pass
class UpdateError(LockError):
    pass
class ReadError(LockError):
    pass
class LockTimeout(LockError):
    pass
class AlreadyLocked(LockError):
    pass
class LockFailed(LockError):
    pass
class UnlockError(Error):
    pass
class NotLocked(UnlockError):
    pass
class NotMyLock(UnlockError):
    pass

#----------------------------------------------------------------------------
# main class                                                             {{{1
#----------------------------------------------------------------------------
class Lock:
    """Lock file by creating a directory."""

    def __init__(self, path, threaded=True, pid=None ):
        """
        usage: 
        lock = Lock('somefile')
        lock = Lock('somefile', threaded=False)
        """
        self.path = path
        self.lock_file = os.path.abspath(path)
        self.hostname = socket.gethostname()
        # get pid if not defined at caller
        if pid is None:
            self.pid = os.getpid()
        else:
            self.pid = pid

        if threaded:
            name = threading.current_thread().get_name()
            tname = "%s-" % urllib.quote(name, safe="")
        else:
            tname = ""
        dirname = os.path.dirname(self.lock_file)

        if threaded:
            tname = "%x-" % thread.get_ident()
        else:
            tname = ""

        # Lock file itself is a directory.  Place the unique file name into
        # it.
        self.unique_name  = os.path.join(
                                self.lock_file, 
                                "%s.%s%s" % (self.hostname, tname, self.pid),
                            )


    def update(self,  content=''):
        """store new content in lock file (e.g. json)"""
        if not self.is_locked():
            raise UpdateError(
                "Could not write content to lock file: no "
                "proper lock file found, call acquire first."
            )

        log.debug( 
            "Writing content to lock file '%s'" % self.unique_name
        )

        try:
            fh = open( self.unique_name, 'wb')
            #for line in content:
            fh.write( content )
            fh.close
        except IOError, emsg:
            raise UpdateError(
                "Could not write content to lock file "
                "'%s':\n%s" % (self.unique_name, emsg)
            )

    def read(self ):
        """read content from lock file, return content"""
        if not self.is_locked():
            raise ReadError(
                "Could not read content from lock file: no proper lock "
                "file found, call acquire() resp. update() first."
            )

        try:
            fh = open( self.unique_name, 'r')
            #for line in content:
            return fh.readlines()
            fh.close
        except IOError, emsg:
            raise ReadError(
                "Could not read content from lock file "
                "'%s':\n%s" % (self.unique_name, emsg)
            )


    def acquire(self, timeout=-1, content=''):
        """
        Acquire the lock.

        * If timeout is omitted (or None), wait forever trying to lock the
          file.

        * If timeout > 0, try to acquire the lock for that many seconds.  If
          the lock period expires and the file is still locked, raise
          LockTimeout.

        * If timeout <= 0, raise AlreadyLocked immediately if the file is
          already locked.
        """
        
        log.debug( "Trying to aquire lock '%s'" % self.lock_file)

        end_time = time.time()
        if timeout is not None and timeout > 0:
            end_time += timeout

        if timeout is None:
            wait = 0.1
        else:
            wait = max(0, timeout / 10)

        while True:
            try:
                os.mkdir(self.lock_file)
            except OSError:
                err = sys.exc_info()[1]
                if err.errno == errno.EEXIST:
                    # Already locked.
                    if os.path.exists(self.unique_name):
                        # Already locked by me.
                        return
                    if timeout is not None and time.time() > end_time:
                        if timeout > 0:
                            raise LockTimeout
                        else:
                            # Someone else has the lock.
                            raise AlreadyLocked
                    time.sleep(wait)
                else:
                    # Couldn't create the lock for some other reason
                    raise LockFailed("failed to create %s" % self.lock_file)
            else:
                log.debug( "Creating lock file" )
                self.update( content )
                return

    def release(self):
        """
        Release the lock.

        If the file is not locked, raise NotLocked.
        """
        log.debug( "Trying to release lock '%s'" % self.lock_file)

        if not self.is_locked():
            raise NotLocked
        elif not os.path.exists(self.unique_name):
            raise NotMyLock
        os.unlink(self.unique_name)
        os.rmdir(self.lock_file)

    def is_locked(self):
        """
        Tell whether or not the file is locked.
        """
        return os.path.exists(self.lock_file)

    def i_am_locking(self):
        """
        Return True if this object is locking the file.
        """
        return (self.is_locked() and
                os.path.exists(self.unique_name))

    def break_lock(self):
        """
        Remove a lock.  Useful if a locking thread failed to unlock.
        """
        if os.path.exists(self.lock_file):
            for name in os.listdir(self.lock_file):
                os.unlink(os.path.join(self.lock_file, name))
            os.rmdir(self.lock_file)

    def __enter__(self):
        """
        Context manager support.
        """
        self.acquire()
        return self

    def __exit__(self, *_exc):
        """
        Context manager support.
        """
        self.release()

#----------------------------------------------------------------------------
# tests and example invocation                                           {{{1
#----------------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    import os
    import pt.terminal  # flush buffers, colors, terminal size
    import pt.logger    # set up logger

    log = pt.logger.Logger(
#        style = "plain",
        name         = __name__ , # __name__ or self.__class__.__name__ 
        level        = logging.DEBUG,  
        file_file    = None,      # None = no file logging
        file_level   = logging.DEBUG,         
    )

    lfile= "/tmp/zick"
    lock = Lock( lfile, threaded=False )
    lock.break_lock()
    lock.acquire()
    print lock.read()
    lock.update( "jjj")  # write cjson or pickle or config stuff
    print lock.read()
#    try:
#        lock.acquire()
#    except AlreadyLocked, emsg:
#        print "already locked ... releasing"
#        lock.break_lock()
#

