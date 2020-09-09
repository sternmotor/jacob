#/usr/bin/env python

    
__ALL__ = [ 'get_cpu_cores' ]

def get_cpu_cores():
    """Return number of cpu cores on local maschine"""

    cpuinfo_fh = open( '/proc/cpuinfo', 'r')

    cpus_counter = 0
    for line in cpuinfo_fh.readlines():
        if line.startswith( 'processor' ):
            cpus_counter += 1
    cpuinfo_fh.close()

    return cpus_counter


if __name__ == '__main__':

    import pt.terminal
    print get_cpu_cores()
