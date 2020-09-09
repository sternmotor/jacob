#!/usr/bin/env python
import os
import sys

DEFAULT_LIB_DIRS = [ "/lib" , "/usr/lib" ]

progs = sys.argv[1:]
progs = ["/bin/rm", "/bin/sh" ]

for prog in progs:
    for dep in os.popen( "ldd %s" % prog).readlines():
        path      = ""
        try:
            path = dep.split()[2]
        except IndexError:
            path = dep.split()[0]

        if path.startswith( "(" ):
            name = dep.split()[0]
            for lib_dir in DEFAULT_LIB_DIRS:
                path = lib_dir + os.sep + name
                if os.path.exists( path ):
                    break
            else:
                sys.stderr.write("Could not find '%s'!\n" % name)
                continue
        print path
