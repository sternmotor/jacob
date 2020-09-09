#!/usr/bin/env python
# -*- coding: utf-8 -*-
#vim:fdm=marker
# unlock vim folding via zR, zo and lock folding via zM, zc
#----------------------------------------------------------------------------
"""                                                                     
 DESCRIPTION    simple shell script template                             {{{1
 
 USAGE          call this script with -h or --help option
       
 CHANGELOG    
    10-02-12    * creation, copied from

 TODO
 
 THANKS TO

"""

__version__ = "$Revision: 0.1.2010-02-12 $"
# $Source$

 
#------------------------------------------------------------------------------
# mounting cifs, bind, unMount
#------------------------------------------------------------------------------
class FsError(BaseException):
    """General files tools error"""

class MountError(FsError):
    """Errors occurring while trying to mount files to mount point"""
    pass


#------------------------------------------------------------------------------
def is_mounted( mount_point ):
#------------------------------------------------------------------------------
    """
    Test if a file/directory holds a mount. Return False if not. If a mount 
    point is found, the tupel (src, target, fs, options, dump, pass_) 
    is returned.
    """
    if os.path.ismount(mount_point):
        try:
            proc_mounts_fh = open( MOUNT_LIST, 'r')
        except IOError, emsg:
            raise MountError("Could not open list of mount points '%s' (%s)" \
                              % ( MOUNT_LIST, emsg[1]) )
        for line in proc_mounts_fh.xreadlines():
            (src, target, fs, options, dump, pass_ ) = line.split()
            if target == mount_point:
                break
        proc_mounts_fh.close()
        return (src, target, fs, options, dump, pass_ )
    else:
        return False


def un_mount( 
    mount_point, 
    force       = False, 
    term_timeout_seq = [ 2, 6, 14 ],     # default term sequence (sec)
    kill_timeout_seq = [ 2, 6, 14 ],     # default kill sequence (sec)
    ):
    """
    Remove a mount from mount_point.

    After trying normal unMount, the mount point gets checked if it is
    really clear. In case not, a lazy unMount is forced (force=False).
    This is repeated until all mounts are vanished which pop up under 
    /proc/mounts.

    In case force=True (non-default), all processes occupying the mount 
    point get killed - see below.


    Return values
    * True : mount point is not mounted (anymore)

    Exception
    * raised when unMount is not possible, (mount point still busy or 
      does not exist)

    Parameters
    * mount point = directory to un-mount from
    * term/kill_timeout_seq: delays between un-mount retries(sec)
    * force=True kills all processes which keep current mount point busy
      in case this is necessary. Default: False

      First, a friendly SIGTERM is issued to the processes which
      block the mount point (sequence defined in term_timeout_seq). In 
      case the process is still alive, a sequence of SIGKILL signals is initiated
      (defined in kill_timeout_seq). If the mount point stays occupied,
      an exception is raised.

      Unmounting is run in sudo mode, killing every process in the way. 
      Take care.
    """
    # check if target exists and is mount point

    # try standard umount as often as returning "ok"

    # mount point still mounted: umount lazy or kill occupying process


    # check if target exists
    print " * un-mounting '%s' ..." % mount_point,

    counter = 0
    # normal umount
    while True :
        try:
            cmd = SysCmd( ['/bin/umount', '-l', mount_point, ], shell = False)
            cmd.start()
            counter += 1
            print "pass %d" % counter,
        except SysCmdError, emsg:
            # last unmount always throws error - ignore in case
            # unmounting did succeed, actually
            if not isMounted( mount_point ):
                print "... ok"
                break
            else:
                # re - raise otherwise
                raise

        else:
            continue



#------------------------------------------------------------------------------
def Mount(
    source      ,
    target      ,
    mount_fs    ,
    mount_options = """relatime""",
    ):
    """
    General, simple mount function (applying sudo mode).
    The mount point gets created in case it does not exist.
    """

    # check mount point
    try:
        createDir( target )
    except FsToolsError, emsg:
        raise MountError(
            "Could not create or access mount target '%s'!" % target
        )

    # mount source to target
    cmd = SysCmd( 
            [ 
                '/bin/mount'            , 
                '-t'                    ,       
                mount_fs                ,
                '%s'   % source         ,
                '%s'   % target         , 
                '-o'                    , 
                '%s'   % mount_options  ,
            
        ]
        , shell = False
    )
    cmd.print_stdout = False    # print stdout messages while running cmd
    cmd.store_stdout = True     # store standard output as array self.stdout
    cmd.print_stderr = False    # print stderr messages while running cmd
    cmd.store_stderr = True     # store error messages as array self.stderr
    try:
        cmd.start()
    except SysCmdError, emsg:
        raise MountError(
            "Error executing mount command\n%s" \
            % '\n'.join(cmd.stdout + cmd.stderr)
        )

#------------------------------------------------------------------------------
def cifsMount( 
    host    ,
    share   ,
    target  ,
    user     = None     ,
    cred_file = None    ,
    mount_fs = 'cifs'   ,
    passwd   = None     ,
    mount_options = "iocharset=utf8,nosetuids,noperm,acl,user_xattr" ,
    extra_options = ""  ,
    timeouts  = [ 0 ],    # retry sequence (sec):
    ):
    """
    Mount a network cifs share to loal mount point.

    Network availability is tested prior to mount tries (like defined
    in timeout_seq).
    """

    # check network connectivity to host
    if not nettools.isReachable( host, timeouts=timeouts ):
        raise MountError("host '%s' is not reachable" % host )


    # check user and password
    if cred_file is None:
        # check user and password
        if user is None or passwd is None:
            raise MountError("cifs mount: specify user+passwd or cred_file!" )
        else:
            cred_option = 'username=%s,password=%s' % (user, passwd)
    else:        
        # credfile given
        if not os.path.isfile( cred_file ):
            raise MountError("Could not read credentials file '%s'" % cred_file)
        else:
            cred_option = 'credentials=%s' % cred_file

    if cred_file is None:
        log.debug(
            "mounting '//%s/%s' to '%s' as user '%s'"
            % (host, share, target, user)
        )
    else:
        log.debug(
            "mounting '//%s/%s' to '%s' using credentials in '%s'" 
            % (host, share, target, cred_file)
        )


    # go mount 
    try: 
        Mount(  
            source   = '//%s/%s' % (host,share) ,
            target   = target                   ,
            mount_fs = mount_fs                 ,
            mount_options  = '%s,%s,%s' % (cred_option, mount_options, extra_options),
        )
    except MountError, emsg:
        if str(emsg).find("mount error 6 = No such device or address") > 0:
            raise MountError(
                "Could not mount share [%s] from '//%s', " % (share,host) \
                + "share not found.\n%s" % emsg
            )
        else:
            raise


#------------------------------------------------------------------------------
def bindmount(source, target):
    """
    Create a bind - mount between two files/dirs.

    In case source is a directory, a target directory is created
    resp. made sure to exist. If the source is a file, the target file
    gets checked. An exception is raised in case of trying to bind mount
    a directory to a file and vice versa.
    """

    log.debug "bind - mounting '%s' to '%s' ... " % (host, target)

    if not os.path.exists(source):
        raise MountError(
            "Bind-mounting '%s' to '%s': source not found!" % (host, target)
        )

    # go mount 
    Mount(  
        source   = source      ,
        target   = target      ,
        mount_fs = none        ,
        mount_options  = 'bind',
    )

 
 
#----------------------------------------------------------------------------
# test structure                                                         {{{1
#----------------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    import os
    import logging
