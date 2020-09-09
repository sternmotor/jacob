#!/usr/bin/python
"""
Module for handling ldap directory interaction

Ldap  * general ldap handler
LdapUser * user and group handler
"""

#import os
#import ldap

"""
class LdapUser

    # general
    uid, nam, gid: single entry or array

__init__
check and store connection parameters
    open and close connection at each request


_open()
_close()
_isArray()

getpwall()
# list of tupels for all users under this ldap tree
getpwnam(nam) # single or a
getpwuid(uid)

(name,passwd,uid,gid,gecos,dir,shell)

setpwnam(nam, [attrs])
# in case any parameter is none, leave it like it is, put "" to clear
setpwuid(uid, [attrs])
rempwnam(nam) # single or array
rempwuid(uid) # single or array 
existspwnam(nam)
existspwuid(uid)

disablepwnam(nam) # single or array
disablepwuid(uid) # single or array
enablepwnam(nam)  # single or array
enablepwuid(uid)  # single or array

pwaddgrnam        # add single entry or array
pwremgrnam  # single or array
pwsetgrnam
pwgetgrnam  # single or array
pwaddgrgid
pwremgrgid
pwsetgrgid
pwgetgrgid

(name,gid,mem)

getgrall()
# list of tupels for all groups under this ldap tree
getgrnam(name)
# tupel
getgrgid(gid)
# tupel
remgrnam(nam)
remgrgid(gid)
existsgrnam(nam)
existsgrgid(gid)
#handle user membership in group
graddpwuid  # add single entry or array
grsetpwuid
grrempwuid
grgetpwuid
graddpwnam
grsetpwnam
grrempwnam
grgetpwnam



if __name__ == "__main__":
    import sys
    #try:
    #useradd( sUserName = 'hbeimer', sHome = '/dev/null' , sShell = '/bin/nologin',  )
    #useradd( sUserName = 'rbeimer', sHome = '/dev/null' , sShell = '/bin/nologin',  )
#    #usermod( sUserName = 'hbeimer', sShell = '/bin/bash' )
#    userpasswd( 'hbeimer',  'hallo1' )
    groupadd( 'hjlh' )
    #except Exception, emsg:
    #    print emsg
    #    sys.exit(1)
    #addgroupstouser( 'hbeimer', [ 'rbeimer', 'hbeimer'] )

"""
