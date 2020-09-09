#!/usr/bin/python

#TODO:
    # make sure other is a set in default acl
    # clean xperm fs_acl fs_xattr (write down methods overview): 
        # double int conversion in methods
        # f <=> rwx conversion

# xperm: getf getw getr getx (usrs, grps, all_mode)

# smooss changes:
# * rem mode: take permissions of parent dir
# * red yel grn symbolic for : no r/rw full access 
 

from sets import Set
from pylin.fs.neu import fs_xattr
from pylin.fs.neu import fs_acl


#==============================================================================
class XpermError(Exception):
    """Errors in xperm script logic and usage errors"""
    pass
class XpermOsError(XpermError):
    """Errors applying/reading xperms to/from underlying file system"""
    pass
class XpermPermissionError(XpermError):
    """No permission to read or change here for current user"""
    pass
class Xperm:
#==============================================================================
    """
    Set walk, exec, read, write and full permissions in file system applying 
    acls and xattrs.

    DESCRIPTION
    Combination of acl, standard unix permissions and xattr entries in files
    and directories allows for storing xperm bits:
   
        x : walk  allow walking
        r : read  allow walking + reading
        w : write allow walking + reading + writing
        f : full  allow walking + reading + writing + changing permissions

    Walk means: entering directories is allowed but not listing the contents. 
    This makes symlinks work. "Execute" bits of files are left in the state 
    they are (unix 'X' mode, not 'x').

    Standard unix permissions are handled as follows: owner:group are set
    to 0:0 and permissions u=rwX,g=rX. Permissions for "others" (users not
    in group 0) are set via all_mode.

    Xattr entries are used to store xperm permission in directories. When 
    traveling the directory structure, each dir where "xperm" attribute is set
    is beeing examined for permissions of the user "uid" for which this script 
    is called. Unix owner and group is beeing set to "root", always.

    Setting permission has the following modes in handling existing xperm
    entries:
    * Mode "over" 
        * Recursively overwrite all xperm permissions, clearing all xperm 
          entries. Does not touch resp. descend into directories where 
          the user "uid" running Xperm has no "f" permissions. This is the 
          default operation mode.
    * Mode "keep"
        * Like "over" but in addition does not descent into directories where 
          any xperm is set already. 
    * Mode "join"
        * Like "over" but when descending into directories where any xperm is 
          set already, adds ("or") new xperm to existing ones. All xperm 
          entries in folder are kept (but modified). Recalculation of 
          resulting xperm is done basing on initial xperm at each xperm entry 
          found while traveling the directory structure.
    * Mode "single"
        * Non - recursive set permissions on single file or directory and it's
          contents: acl for each file entry, path's xperm for each directory
          where no existing xperm is found.
        
    Setting permissions does not start in case the "uid" or has no "f" 
    permission at entry point or parent directory ( resp. the parent's parent 
    etc.) *and* in xperm given as argument here. It does start in case there 
    are no parent xperms in filesystem and "f" is specified for uid. "f" is 
    specified for uid in case uid is in "f" group, member of a group with "f" 
    permissions or in case all_mode is "f".

    XpermError is raised in case a path does not exist except for uid_has...
    methods listed below.
          
    All user and group id's are handled as integers (uid/gid).

    PUBLIC METHODS
    __init__(xperm, uid) : uid: xperm and user to run as
    set(path, mode):     : store xperm at path, set acls as defined with mode
    get(path, depth)     : depth = 0: read single dir or file 
                           depth = 1: return all directory contents' xperms
                           depth > 1: descent directories "depth" levels deep,
                                      return nested arrays
                           default depth is 0
    rem(path, mode)      : * remove all xperm definitions in path
                           * set acl as of parent dir according to mode setting
    exists(path)         : True if there is an xperm set at path
    repair(path, mode)   : Fix xrw permissions in file system by applying the
                           acl stored in xperm entry(xattr) to the file system

    uidHasFperm(path)    : return True in case uid has "f" permissions at path
    uidHasWperm(path)    : return True in case uid has "w" permissions at path
    uidHasRperm(path)    : return True in case uid has "r" permissions at path
    uidHasXperm(path)    : return True in case uid has "x" or "X" permissions 
    False in case path does not exist ( hide pathes where uid has no r perm )

    see options in __init__() doc string.


    EXCEPTIONS
    XpermError, XpermOsError 
    """
    #-------------------------------------------------------------------------
    def __init__(self, xperm={}, uid=None ):
    #-------------------------------------------------------------------------
        """
        Check permission settings and initiate acl and xattr handlers.

            xperm array contains:  
                x_usrs, r_usrs, w_usrs, f_usrs
                x_grps, r_grps, w_grps, f_grps
               
                all_mode:  * permissions for "others" ( = all users except 
                             those in group 0 ) are set here, xrwf allowed

            uid * user which is issuing changes. "uid" is checked for
                  permissions at each xperm entry found in file system

        # read man mknod(2)
        """
        # check all xperm usr/grp arrays for uid/gid format (must be int)
        # TODO replace if clause below by keys().remve('all_mode')
        xperm = self._singularize( xperm )

        for key in xperm.keys():
            if key == 'all_mode': 
                continue
            for i, id in enumerate( xperm[ key ] ):
                xperm[key][i] =  self._isInt( id )
                if not xperm[key][i]:
                    raise XpermError(
                        "Id '%s' in xperm entry '%s' is no positive integer" \
                        + "uid/gid!" % ( id, key )
                    )

        # check uid for format
        if not self._isInt( uid ):
            raise XpermError( "Uid '%s' is no postive integer!"  % uid )

        # init set get rem exists methods for xattrs and acls
        self.xperm = xperm
        self.xattr = XpermXattr( xperm )
        self.acl   = XpermAcl()

    #-------------------------------------------------------------------------
    def _isInt( self, val ):
    #-------------------------------------------------------------------------
        """
        Check all xperm usr/grp arrays + uid for uid/gid format (must be int)
        """
        try:
            i = int( val )
            if not int( val ) < 0:
                return i 
            else:
                return False

        except ValueError:
            return False
            
    #-------------------------------------------------------------------------
    def uidHasFperm(self, path, uid=None):  
    #-------------------------------------------------------------------------
        """
        Return True if self.uid or given uid has "f" permission at path, is 
        member of a group with "f" permission or all_mode is "f". 
        False if not or dir does not exist.

        In case there are no xperm at path, parent dirs are examined.
        Method returns True in case there are no xperms at all up the tree in 
        order to make initial xperm setup does work.
        """
        if uid == None: uid = self.uid

        # read xperm from file, check xperm

    def _uidHasFInXperm(self, xperm):
        """
        Same as method above but analyses xperm struct only - reusable code.
        """
    #-------------------------------------------------------------------------
    def uidHasWperm(path):  
    #-------------------------------------------------------------------------
        """
        Return True if self.uid or given uid has "w" or "f" permission at 
        path, is member of a group with "w" or "f" permission or all_mode 
        is "w" or "f". 
        False if not or dir does not exist.

        "w" permissions are read from acl in file system, not from xperm
        entry in file (which is used for repair only)
        """
    def _uidHasWInXperm(self, xperm):
        """
        Same as method above but analyses xperm struct only - reusable code.
        """
    #-------------------------------------------------------------------------
    def uidHasRperm(path):  
    #-------------------------------------------------------------------------
        """
        Return True if self.uid or given uid has "r", "w" or "f" permission
        at path, is member of a group with "w" or "f" permission or all_mode 
        is "r", "w" or "f". 
        False if not or dir does not exist.

        "rw" permissions are read from acl in file system, not from xperm
        entry in file (which is used for repair only)
        """

    def _uidHasRInXperm(self, xperm):
        """
        Same as method above but analyses xperm struct only - reusable code.
        """
    #-------------------------------------------------------------------------
    def uidHasXperm(path):  
    #-------------------------------------------------------------------------
        """
        Return True if self.uid or given uid has xrwf permission
        at path, is member of a group with xrwf permission or all_mode 
        is one of xrwf. 
        False if not or dir does not exist.

        "xrw" permissions are read from acl in file system, not from xperm
        entry in file (which is used for repair only)
        """

    def _uidHasXInXperm(self, xperm):
        """
        Same as method above but analyses xperm struct only - reusable code.
        """
    #-------------------------------------------------------------------------
    def set( self, path, mode = 'over'): 
    #-------------------------------------------------------------------------
        """
        Set xperm permission for current path in case user has "f" permissions
        here and "f" perms are defined in new xperm. Stores acl, unix modes 
        and fperm in xattr at path. "f" permissions are translated to "w" for 
        all_mode and acls.

        Works recursive according to mode (see class description) in case path
        is a dir. In case path is a file, only this file is beeing processed.

        Standard unix permissions are handled as follows: owner:group are set
        to 0:0 and permissions u=rwX,g=rX. Permissions for "others" (users not
        in group 0) are set via all_mode.

        Setting permissions does not start in case the "uid" or has no "f" 
        permission at entry point or parent directory ( resp. the parent's 
        parent etc.) *and* in xperm given as argument here. It does start in 
        case there are no parent xperms in filesystem and "f" is specified for
        uid. "f" is specified for uid in case uid is in "f" group, member of a        group with "f" permissions or in case all_mode is "f".
            
        Raise if no "f" permission here.
        Raise if path does not exist.
        """
        self._checkPathExists( path )

        self.acl.define( self.xperm )
        self.acl.set( path )
        self.xattr.set( path )

    #-------------------------------------------------------------------------
    def get( self, path, depth = 0):  
    #-------------------------------------------------------------------------
        """
        Read and return xperm info for current path. In case there is no xperm
        entry at path, fperms are taken from parent dir(s), acls from path.
        In case there are no fperms specified in parent dirs, empty fperm 
        arrays are returned. Use uidHasFperm to examine if a user has full 
        permissions at path, then.
        The resulting xperm is a joined xperm of XpermXattr and XpermAcl get().
        Only the highest permission is returned ( f > w > r > x ).

        Reads fperm from xperm entry here but rwf is read from filesystem acl.
        In case fperm says "f" but acl is e.g. "rw" only, "rw" is returned. 
        "f" is returned only in case acl is "rwx".

        For depth > 1, an array of xperms is returned.    
        depth = 0: read single dir or file 
        depth = 1: return all directory contents' xperms
        depth > 1: descent directories "depth" levels deep return nested arrays

        Raise if path does not exists.
        Raise if uid has no "r"  permissions here.
        """
        self._checkPathExists( path )
        xperm = self._join( self._find( path ), self.acl.get( path ) )
        return self._singularize( xperm )

#    #-------------------------------------------------------------------------
#    def rem( self, path, mode= 'over' ): 
#    #-------------------------------------------------------------------------
#        """
#        Remove all xperm definitions in path, set acl as of parent dir 
#        applying mode setting. In case parent path has no acls, remove them 
#        here, too.
#
#        Works recursive according to mode (see class description).
#
#        Return False if there are no xperms stored at path. 
#        Raise in case path does not exist.
#        Raise if not "f" at path.
#        """
#        self._checkPathExists( path )
#        self.acl.rem( path )
#        self.xattr.rem( path )
    
        # set parent permissions
#    #-------------------------------------------------------------------------
#    def repair(self, path, mode ):
#    #-------------------------------------------------------------------------
#        """
#        Fix xrw permissions in file system by applying the acl stored in xperm
#        entry(xattr) to the file system.
#        Works recursive according to mode (see class description).
#
#        Raise if no "f" at path
#        Raise if path does not exists. 
#        """
#        self._checkPathExists( path )
    #-------------------------------------------------------------------------
    def exists(self, path ):
    #-------------------------------------------------------------------------
        """
        True if an xperm is stored at path (xattr entry xperm_all_mode exists)
        False if path does not exist.
        """
        # return False in case path does not exist
        try:
            self._checkPathExists( path )
        except XpermError:
            return False

        # check if xperm exists
        return self.xattr.exists( path )

    #-------------------------------------------------------------------------
    def _find(self, path):
    #-------------------------------------------------------------------------
        """
        Travel up path, find xperm (if exists) an return it. Used for 
        determining fperm state for current path.
        Return False if there are no xperms up the Tree.

        Raise in case path does not exist.
        Raise in case uid has no "r" permissions here or up the tree
        """
        self._checkPathExists( path )
        # no xperm entry found in file system
        return { 'all_mode' : ''}
    #    return self.xattr.get_short( path )
        
    #-------------------------------------------------------------------------
    def _join(self, xperm1, xperm2): 
    #-------------------------------------------------------------------------
        """
        Return merge of two xperm sets. Merging is an atomic addition of all
        xrwf permissions (here: simple user/group addition in member arrays)

        Logically, addition is an "or" junction of both permission sets.

        Recalculate new xperm so full mode replaces rwx where approbiate.
        """
            
        # create a list of all keys in xperm1 and xperm2 (which are set at all) 
        all_keys = list(Set( xperm1.keys() ).union( xperm2.keys() ) )

        # join w usrs, w_grps
        xperm = {}
        for key in all_keys:
            try:
                xperm[ key ] = list(Set( xperm1[ key ] ).union( xperm2[ key ]))
            except KeyError:
                try: 
                    xperm[ key ] = xperm1[ key ]
                except KeyError:
                    xperm[ key ] = xperm2[ key ]
    
        # join all mode
        xperm[ 'all_mode' ] = ''.join(
            list( 
                Set( 
                    list( xperm1[ 'all_mode' ] ) 
                ).union(
                    list( xperm2[ 'all_mode' ] )
                )
            )
        )

        return xperm

    #-------------------------------------------------------------------------
    def _singularize( self, xperm ):
    #-------------------------------------------------------------------------
        """
        Clean up xperm permission set by removing all double entries, e.g.
        f permissions replace x, r and w.
        """
        # handle users and groups
        for key in ( 'usrs', 'grps'):
            try:
                for item in xperm[ 'f_' + key ]:
                    try: xperm[ 'w_' + key ].remove( item )
                    except ValueError: pass
                    try: xperm[ 'r_' + key ].remove( item )
                    except ValueError: pass
                    try: xperm[ 'x_' + key ].remove( item )
                    except ValueError: pass
            except KeyError: 
                pass

            try:
                for item in xperm[ 'w_' + key ]:
                    try: xperm[ 'r_' + key ].remove( item )
                    except ValueError: pass
                    try: xperm[ 'x_' + key ].remove( item )
                    except ValueError: pass
            except KeyError: 
                pass

            try:
                for item in xperm[ 'r_' + key ]:
                    try: xperm[ 'x_' + key ].remove( item )
                    except ValueError: pass
            except KeyError: 
                pass
            
        # handle all_mode
        if   'f' in xperm[ 'all_mode']:
            xperm[ 'all_mode' ] = 'f'
        elif 'w' in xperm[ 'all_mode']:
            xperm[ 'all_mode' ] = 'w'
        elif 'r' in xperm[ 'all_mode']:
            xperm[ 'all_mode' ] = 'r'

        # fine
        return xperm

    #-------------------------------------------------------------------------
    def _checkPathExists(self, path ):
    #-------------------------------------------------------------------------
        """
        Simply check if there is a file or directory at path, raise
        otherwise
        """
        if not os.path.isfile( path ) and not os.path.isdir( path ):
            raise XpermError(
                "Path '%s' is no directory or file!" % path
            )


#==============================================================================
class XpermXattrError(Exception):
    """Errors in script logic and usage errors"""
class XpermXattrOsError(XpermXattrError):
    """Errors applying/reading fperms to/from xattrs in file system"""
class XpermXattr:
#==============================================================================
    """
    Methods for handling xperm permissions on dirs or files. This permissions
    are stored as xattr entries to files.
    Basically this is a wrapper to fs.xattr methods.

    set( path )        # store xperm users and groups
    get( path )        # return xperm from path
    rem( path )        # clear out xperm definitions
    exists( path )     # return True False if xperm entry exists at all

    Works non-recursive, permissions to change files are not changed here.
    """

    #-------------------------------------------------------------------------
    def __init__( self, xperm ):
    #-------------------------------------------------------------------------
        """
        Load and initialize fs.xattr class.
        """
        # convert xperm to xattr compatible format:
        #   w_usrs = 23::45666:222222::2
        self.sep       = '::'
        self.xattr_set = {}
        try:
            for key in xperm.keys():
                if len( xperm[ key ] ) == 0: # do not store empty arrays
                    continue

                # store w_usrs as xperm_w_usrs
                self.xattr_set[ 'xperm_' + key ] \
                    = self.sep.join( [ str(i) for i in xperm[ key ] ] )
        except Exception, emsg:
            raise XpermXattrError(
              "Could not concentate xattr from xperm '%s'\n%s" % (xperm, emsg)
            )

        # store all_mode as xperm_all_mode
        self.xattr_set[ 'xperm_all_mode' ] = xperm[ 'all_mode' ]

    #-------------------------------------------------------------------------
    def set( self, path ):
    #-------------------------------------------------------------------------
        """
        Store xperm to file. Raise if path does not exist.
        """
        try:
            for key in self.xattr_set.keys():
                fs_xattr.set( path, key, self.xattr_set[ key ] )

        except fs_xattr.XattrError, emsg:
            raise XpermXattrOsError(
                "Error setting xacl part of xperm to '%s\n%s'" % ( path, emsg )
            )

    #-------------------------------------------------------------------------
    def get( self, path ):
    #-------------------------------------------------------------------------
        """
        Read xperm from file. Raise if path does not exist.
        """
        if not self.exists( path ):
            raise XpermXattrError(
                "Get: no xperm defined at path '%s'!" % path
            )

        xperm = {}
        # read stored keys
        try:
            for key, val in fs_xattr.getAll( path ):
                if key.startswith('xperm_'):
                    xperm[ key[6:] ] = val.split( self.sep )

        except fs_xattr.XattrError, emsg:
            raise XpermXattrOsError(
               "Error reading xacl part of xperm from '%s\n%s'" % ( path,emsg)
            )

        # convert to uid strings to int, remove empty entries
        for key in xperm.keys():
            if len( xperm[ key ] ) == 0 :
                xperm[ key ].remove # remove not tested
                continue
            elif key == 'all_mode':
                continue
            else:
                xperm[ key ] = [ int(i) for i in xperm[ key ] ]

        return xperm

    #-------------------------------------------------------------------------
    def get_short( self, path ):
    #-------------------------------------------------------------------------
        """
        Read xperm xattr entry from path but return full permissions, only
        """
        full_xperm = self.get( path )
        short_xperm = {}

        for key in ( 'all_mode', 'f_usrs', 'f_grps' ):
            try:
                short_xperm[ key ] = full_xperm[ key ]
            except KeyError:
                pass
        # remove all_mode setting which is not "f"        
        if 'f' in short_xperm[ 'all_mode' ] :  
            short_xperm[ 'all_mode' ] = 'f'  
        else:
            short_xperm[ 'all_mode' ] = ''  

        return short_xperm 
        

    #-------------------------------------------------------------------------
    def rem( self, path ):
    #-------------------------------------------------------------------------
        """
        Remove xperm entry from file. Raise if path does not exist.
        """
        try:
            for key, val in fs_xattr.getAll( path ):
                if key.startswith('xperm_'):
                     fs_xattr.rem( path, key )

        except fs_xattr.XattrError, emsg:
            raise XpermXattrOsError(
                "Error removing xacl part of xperm from '%s\n%s'" % ( path,emsg)
            )



    #-------------------------------------------------------------------------
    def exists( self, path ):
    #-------------------------------------------------------------------------
        """
        True if xperm entry exists in file, False if not. Raise if path does 
        not exist.
        """
        try:
            fs_xattr.get( path, 'xperm_all_mode' )
        except fs_xattr.XattrError:
            return False
        else:
            return True



#==============================================================================
class XpermAclError(Exception):
    """Errors in acl script logic and usage errors"""
class XpermAclOsError(XpermAclError):
    """Errors applying/reading acls to/from underlying file system"""
    pass
class XpermAcl:
#==============================================================================
    """ 
    Methods for handling acl and standard unix permissions on dirs and files.
    Basically this is a wrapper to fs.fs_acl methods.
    define( xperm )     # define acl set (convert from xperm)
    set( path )         # write out acls and unix permissions to path
    get( path )         # return xperm containing acl and unix permissions
    rem( path )         # clear out acl definitions, set 0:0 0750

    Works non-recursive, permissions to change files are not checked here.
    """
    #-------------------------------------------------------------------------
    def __init__(self):
    #-------------------------------------------------------------------------
        """
        Define acl class for read an rem method access, set() needs define()
        beeing executed before set() call.
        """
        self.id_keys = ( 
            'x_usrs', 'r_usrs', 'w_usrs',  
            'x_grps', 'r_grps', 'w_grps',  
        )

        self.acl = fs_acl.FsAcl()
    
    #-------------------------------------------------------------------------
    def define( self, xperm, onr='0:0', onr_mode='rwx', grp_mode='rx' ):
    #-------------------------------------------------------------------------
        """
        Convert xperm to acl_set, applying defaults.
        onr = unix owner:group (default: root:root)
        onr_mode, grp_mode: r,w,x 
        grp_mode is determined from xperm all_mode
        """

        # shorten xperm list by full entries

        self.acl_set = {}
        for key in self.id_keys:
            try:
                self.acl_set[ key ] = xperm[ key ]
            except KeyError:
                pass # ignore unset keys


        # recalculate xperm so fperms are translated to "w" permissions in 
        # all_mode and "w" groups and users
        self.acl_set['w_usrs'] \
            = list(Set( xperm['w_usrs'] ).union( xperm['f_usrs'] ))
        self.acl_set['w_grps'] \
            = list(Set( xperm['w_grps'] ).union( xperm['f_grps'] ))

        # adjust all mode
        if   xperm['all_mode'].find('f') > -1 \
        or   xperm['all_mode'].find('w') > -1:
            all_mode = 'rwx'
        elif xperm['all_mode'].find('r') > -1:
            all_mode = 'rx'
        elif xperm['all_mode'].find('x') > -1:
            all_mode = 'x'
        else:
            all_mode = ''

        # set acl_set unix permissions,  must be like ['rwx', 'rx', '']
        self.acl_set['unix_mode'] = [ onr_mode, grp_mode, all_mode, ]

        # set ac_set unix owner and group
        self.acl_set['unix_owner'] = onr

        try:
            self.acl.define( self.acl_set )
        except fs_acl.FsAclError, emsg:
            raise XpermAclOsError(
                "Could not initialize fs_acl instance with xperm data!\n%s" \
                % emsg
            )

    #-------------------------------------------------------------------------
    def set( self, path ):
    #-------------------------------------------------------------------------
        """
        Prepare + write acls and unix owner:group = 0:0 to path, non-recursive.
        Any existing acl is beeing overwritten.

        Raise in case path does not exist.
        """
        try: 
            self.acl.set( path )
        except fs_acl.FsAclError, emsg:
            raise XpermAclOsError(
                "Could not set fs_acl acl permissions for '%s' !\n%s" \
                % ( path, emsg )
            )

        

    #-------------------------------------------------------------------------
    def get( self, path ): 
    #-------------------------------------------------------------------------
        """
        Read acl from path, return xperm. Raise in case path does not exist.
        """
        # read acl from file
        try: 
            acl_set = self.acl.get( path )
        except fs_acl.FsAclError:
            raise XpermAclOsError(
                "Could not read fs_acl acl permissions from '%s'\n%s" \
                % ( path, emsg )
            )

        # convert acl to xperm: 
        xperm = {}
        for key in self.id_keys:
            try:
                xperm[ key ] = acl_set[ key ]
            except KeyError:
                pass

        xperm['all_mode'] = acl_set['unix_mode'][2]

        # convert unix onr/grp to xperm, in case it is not root
        onr, grp = acl_set['unix_owner'].split(':')

        onr_perm = acl_set['unix_mode'][0]
        if ( not onr == 0 ) or ( onr_perm == '' ):
                for perm in 'w' 'r' 'x':
                    if onr_perm.find( perm ) > -1:
                        try:
                            xperm[ '%s_usrs' % perm ]
                        except KeyError:
                            xperm[ '%s_usrs' % perm ] = [ onr ]
                        else:
                            xperm[ '%s_usrs' % perm ].append( onr )

        grp_perm = acl_set['unix_mode'][1]
        if not grp == 0 or grp_perm == '':
                for perm in 'w' 'r' 'x':
                    if grp_perm.find( perm ) > -1:
                        try:
                            xperm[ '%s_grps' % perm ]
                        except KeyError:
                            xperm[ '%s_grps' % perm ] = [ grp ]
                        else:
                            xperm[ '%s_grps' % perm ].append( grp )
        # fine
        return xperm


    #-------------------------------------------------------------------------
    def rem( self, path ):
    #-------------------------------------------------------------------------
        """
        Remove posix acl entries from path, leave unix permissions only.
        Raise in case path does not exist.
        """
        self.acl.rem( path )


#=============================================================================
if __name__ == '__main__':
#=============================================================================
    import sys
    import os
    from pylin.fs import fstools

    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
    sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', 0)
    file = "/srv/test/ldap/"
    fstools.createDir( file )

    xperm = {
        'w_grps'     : [1003]        ,
        'w_usrs'     : ['1001', 2003]       ,
        'f_grps'     : [2]           ,
        'f_usrs'     : ['2', '5', 7]  ,
        'all_mode'  : 'f'  ,
    }


    file = '/etc'

# test acl
    x = Xperm(xperm, uid=2)
#    x.set( '/srv/test' )
    print x.get( file )
    print x.exists( file )

# test xattr

#    x = Xperm(xperm, uid=2)
#    x.xattr.set('/srv/test')
#    print x.xattr.get('/srv/test')
#    print x.xattr.exists( '/srv/test' )


# test join

#    xperm1 = {
#        'w_grps'     : [1003]        ,
#        'w_usrs'     : ['1000', 2003]       ,
#        'f_grps'     : [2]           ,
#        'f_usrs'     : ['2', '5', 7]  ,
#        'all_mode'  : 'r'  ,
#    }
#    xperm2 = {
#        'w_grps'     : [1003, 4]        ,
#        'w_usrs'     : ['1000', 2003]       ,
#        'f_grps'     : [2,1]           ,
#        'f_usrs'     : ['2', '5', 7]  ,
#        'all_mode'  : 'rf'  ,
#    }
#
#    id_keys = ( 
#        'x_usrs', 'r_usrs', 'w_usrs', 'f_usrs', 
#        'x_grps', 'r_grps', 'w_grps', 'f_grps', 
#    )
#
#    # set dummy values for undefined arrays
#    for key in id_keys:
#        try: 
#            xperm1[ key ]
#        except KeyError:
#            xperm1[ key ] = []
#    # set dummy values for undefined arrays
#    for key in id_keys:
#        try: 
#            xperm2[ key ]
#        except KeyError:
#            xperm2[ key ] = []
#
#
#    print xperm1
#    print xperm2
#    x = Xperm(xperm, uid=2)
#    print x._joinXperms( xperm1, xperm2 )
