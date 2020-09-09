#!/usr/bin/python
# create a logical volume of same size on remote host


import sys
import os


class LvmError(BaseException):
    """Errors handling logical volumes, pvs or vgs"""

def usage():
    print "Usage: %s [LV PATH] [PEER HOST]" % sys.argv[0]
    print "Creates an lvm with same size and name at PEER HOST,"
    print "this requires ssh login to peer host."
    print
    print "Example: %s /dev/vg0/data-tmp host2.sr1.srservers.net" % sys.argv[0]



def get_lv_size( lv_path ):

    lv = os.path.basename( lv_path )

    # size is read in KBytes
    for line in os.popen( "lvs --units K --separator ':' --noheadings --nosuffix --unbuffered %s " % lv_path ).readlines():
        ( line_lv, line_vg, mode, size ) = line.split(':')[:4]

        if lv == line_lv.strip():
            return size
        else:
            continue
    raise LvmError( "Could not read size information for device '%s'" % lv_path )


def create_peer_lv(lv_path, lv_size, rem_host):

    print(
        "creating lvm '%s' at remote host '%s'"
        % (lv_path, rem_host)
    )

    ec = os.system(
        'ssh %s lvcreate -L %sk -n %s'
        % ( rem_host, lv_size, lv_path)
    )
    if not ec == 0:
        raise LvmError(
            "Error creating lv '%s' at host '%s'"
            % ( lv_path, rem_host,  )
        )


if __name__ == '__main__':

    try:
        lv_path, rem_host = sys.argv[1:3]
    except IndexError:
        usage()
        sys.exit(1)


    lv_size = get_lv_size( lv_path )
    create_peer_lv( lv_path, lv_size, rem_host)

