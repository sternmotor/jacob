#!/usr/bin/env python

from pt.run import Run
from pt.data import validate
run=Run()
    
    
MOUNT_POINT='/mnt'
machine = 'bps1-devel'

ROOT_DRIVE   = 'root'
OTHER_DRIVES = [ 'srv', 'usr', 'var', 'tmp' ]
DRBD_DEV_PREFIX = '/dev/drbd' 
DRIVE_BUSY_MARKERS = [ 'xen-vbd:', 'Secondary/Primary' ]

class DrbdMountError(BaseException):
    pass
class DriveBusyError(DrbdMountError):
    pass

  
# analyse existing
for line in run.start( "drbd-overview" ):
    # is drive member of machine?
    if ':%s-' % machine in line:
        # identify drive
        res_id   = validate.is_integer( line.split(':')[0].strip() )
        res_name = validate.is_string ( line.split(':')[1].split()[0])
        # check if drive is busy
        for busy_marker in DRIVE_BUSY_MARKERS:
            if busy_marker in line:
                raise DriveBusyError( 
                    "Ressource %s:%s looks busy (found '%s' in drbd-overview "
                    "'s output)" % (res_id, res_name, busy_marker)
                )



