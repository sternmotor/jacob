#!/usr/bin/python

import sys
import os

class DrbdConfigError(Exception):
    pass

DRBD_DEVICE = '/dev/drbd'       # common prefix before device number


def findDeviceLines( config_file, host_name ):
    """
    Iterator yielding lines containing device entries. Options split
    into multiple lines are joined. Finally each line containing 'device'
    string is yielded, {} removed
    """

    # try to open config file
    try:
        fh_config = open( config_file )
    except Exception, emsg:
        raise DrbdConfigError( 
            "could not open config file '%s'!\n%s" 
            % ( config_file , emsg)
        )

    # read config file, strip out resource and device lines
    for line in fh_config:

        # list all lines for this host
        line_segments = line.split()

        # concentate line segments from multiple lines
        try:
            # memorize latest resource entry
            if   line_segments[0] == 'resource':
                resource = line_segments[1]
                continue
            # split device line
            elif line_segments[0] == 'on' and line_segments[1] == host_name:
                sub_line = line
                # add other options until '}' is reached
                while sub_line.find('}') < 1:
                    line_segments.extend( sub_line.split() )
                    sub_line = fh_config.next()
            else:
                continue

        except IndexError:
            continue

        # strip out line content between {}
        new_line = ' '.join( line_segments ).split('{')[-1]
        yield  "resource %s; %s" % (resource, new_line.split('}')[0].strip() )

def getResources( config_file = '/etc/drbd.conf' , host_name = None ):
    """
    Return iterator over all ressources in drbd.conf or other 
    specified drbd config file

    Requires hostname for which the ressources should be listed
    """

    if host_name == None:
        raise DRBD_ERRROR(
            "Specify one of the hostnames in your drbd config file!")

    dev_length = len( DRBD_DEVICE )

    for line in findDeviceLines( config_file, host_name ):

        # return value
        device = {}
        
        for key_val in line.split(';'):
            try:
                key = key_val.split()[0].strip('"').strip()
                val = key_val.split()[1].strip('"').strip()
            except IndexError:
                continue

            if   key == 'resource':
                 device['resource'] = val

            elif key == 'device':
                 device['dev'     ] = val
                 device['dev_id'  ] = int(val[dev_length:])

            elif key == 'disk':
                 device['disk'    ] = val

            elif key == 'address':
                 device['address' ] = val.split(':')[0]
                 device['port'    ] = int(val.split(':')[1])

        if len(device) < 6:
            raise DrbdConfigError(
                "Could not find all parameters for device in '%s'"
                % line
            )
        else:        
            yield device

if __name__ == "__main__":
    import sys
    sys.path.pop(0)
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
    sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', 0)

    try:
        for data in getResources('/etc/drbd.conf', 'host1'):
            print data
    except DrbdConfigError, emsg:
        print emsg
        sys.exit(1)


