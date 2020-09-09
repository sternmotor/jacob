#!/usr/bin/python

"""
 DESCRIPTION  wrapper for subprocess, adapted to linux shell needs
 
 USAGE        call this script with -h or --help option
       
 CHANGELOG    
    09-06-10    * removed run_quick
                * added timeout
    09-03-23    * release for python

 TODO
 
 THANKS TO

"""

#=============================================================================
# modules import, script initialisation
#=============================================================================
__ALL__ = [
    'ExeError',
    'which',
    'is_exe',
]

import os           # check path


class ExeError(BaseException):
    pass
    

#-----------------------------------------------------------------------------
# which - check if executable exists in path
#-----------------------------------------------------------------------------
def which(program):
    """emulates unix' "which" command (with one argument only)"""
    ppath, pname = os.path.split(program)
    if ppath:
        if is_exe(program):
            return program
    else:
        return _search_path(program)
    # not found
    raise ExeError(
        "No read/exec access to '%s', check permissions "
        "and installed packages!" % program
    )

#-----------------------------------------------------------------------------
# Helpers
#-----------------------------------------------------------------------------

def is_exe(exe):
    return os.path.isfile(exe) and os.access(exe, os.X_OK) and os.access(exe, os.R_OK)

def _search_path(program):
    found_executables = []
    for path in os.environ['PATH'].split(os.pathsep):
        exe = os.path.join(path, program)
        if is_exe(exe):
            found_executables.append( exe )
    if found_executables == []:
        raise ExeError(
            "No read/exec access to '%s' in system PATH, check permissions "
            "and installed packages!" % program
        )
    else:
        if len(found_executables) == 1:
            return found_executables[0]
        else:
            return found_executables

#=============================================================================
# test structure
#=============================================================================
if __name__ == "__main__": 
    import sys
    import os

    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
    sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', 0)


#    print which( "/bin/lsx" )
    print which( "ls" )


