#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
 DESCRIPTION  some shell tools for python scripts
 checkNet     - Check if a host is reachable via "ping" or at specific ports.


 
 CHANGELOG    
    09-07-22    * split up tools into users fs net tools
    09-06-23    * combined mount, symlink, print stuff from pylin

 TODO
 
 THANKS TO

"""

from pylin.syscmd.syscmd import SysCmd, SysCmdError
import time


class NetToolsError(Exception):
    pass

#------------------------------------------------------------------------------
# network reachable ?
#------------------------------------------------------------------------------
def isReachable(host, timeouts = [0] , ports=[]):
    """
    Check if a host is reachable via "ping" or at specific ports.

    Parameters
        * host       = valid ip or dns name
        * ports      = array to test for reachability (instead of 
                       simple ping)
        * timout_seq = retry sequence in sec between retries, None for
                       just one check
    """
    ping_cmd = SysCmd(
           [ 'ping', '-c', '1', '-w', '1', host ],
           shell = False,
    )
    ping_cmd.print_stdout = False    # print stdout messages while running cmd
    ping_cmd.store_stdout = False   # store standard output as array self.stdout
    ping_cmd.print_stderr = False    # print stderr messages while running cmd
    ping_cmd.store_stderr = True    # store error messages as array self.stderr


    retry = len( timeouts ) + 1
    print "Checking connection to host '%s' ..." % host,

    for timeout in timeouts:
        retry = retry - 1 
        try:
            ping_cmd.start()
        except SysCmdError, emsg:
            print "%d:%dsec " % (retry, timeout),
            time.sleep( timeout )
            continue
        print "ok"
        return True
    print "... ERROR"
    return False




#------------------------------------------------------------------------------
# test structure
#------------------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    import os
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
    sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', 0)

    print isReachable( host = 'www.gosgle.de', timeouts=[1,2] )
