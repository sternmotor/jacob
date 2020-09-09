#!/usr/bin/python

from pylin.fs.neu import xperm

#=============================================================================
if __name__ == "__main__":
#=============================================================================
    import sys
    import os

    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
    sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', 0)


    xp = xperm.Xperm()
    print xp.get("/tmp/lala")
