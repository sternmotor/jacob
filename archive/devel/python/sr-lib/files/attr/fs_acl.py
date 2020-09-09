#!/usr/bin/python
import os
from sets import Set

# TODO
# acl.delete

# handle acl-perm and unix-perm  between all functions, only
# move module to acl_perm

# http://linux.die.net/man/3/acl_set_file  : error handler with 
# correct error codes

#=============================================================================
class FsAclError(Exception):
#=============================================================================
    pass

#=============================================================================
# non - standard modules
#=============================================================================
try:
    pass
    import posix1e      # python acl support
except ImportError, emsg:
    raise FsAclError(
        "Could not import posix acl module, try 'sudo aptitude install -y " \
        + "python-pylibacl' !\n%s" % emsg
    )

#=============================================================================
class _FsAclDefine:
#=============================================================================
    """
    Methods used by FsAcl class for converting an acl set as described in 
    FsAcl.__init__ docstring to an acl permissions string.

    TODO this methods need *some* facelifting
    """

    #-------------------------------------------------------------------------
    def define(self, acl_set = {} ):
    #-------------------------------------------------------------------------
        """
        Prepare acl permission set (check input, generate acl)
            x_usrs     * array of user  names or uids: walk
            r_usrs     * array of user  names or uids: walk+read
            w_usrs     * array of user  names or uids: walk+read+write
            x_grps     * array of group names or gids: walk
            r_grps     * array of group names or gids: walk+read 
            w_grps     * array of group names or gids: walk+read+write
            unix_owner * unix owner and group for file (0:0)
            unix_mode  * tupel of permissions for user, group, others like
                         ('rwx', 'rx', '').
        """

        # get unix owner and group from input string or set defaults
        self.onr, self.grp = (
            self._isInt( item, 'unix_onr/grp' ) for item in
            self._getUnixOwner( acl_set['unix_owner'] )
        )

        # get unix permissions from input string or set defaults
        acl_text_array = self._getUnixPermissions( acl_set['unix_mode'] )


        # concentate permission string from acl_set arrays
        for usersgroups in self._getUsersGroups( acl_set):
            acl_text_array.extend( usersgroups )


        # define and store posix1e.ACL handler and acl mask 
        #print ','.join( acl_text_array )
        self._createAcl( acl_text_array )


    #-------------------------------------------------------------------------
    def _getUnixPermissions( self, unix_mode, def_mode = ['rwx', 'rx', ''] ):
    #-------------------------------------------------------------------------
        """
        get unix permissions from input string or set defaults
        return array of acl strings
        """
        try:             
            if unix_mode == '' or unix_mode is None:
                new_mode = def_mode
        except KeyError: 
            new_mode = def_mode
        try:
            ( usr_perm, grp_perm, oth_perm ) = unix_mode
        except ValueError:
            raise FsAclError(
                "Error in unix permission definition "   \
                + "'%s', try something like" % xacl_set['unix_mode']   \
                + "'unix_mode=['rwx', 'rx', '']'!"
            )


        # convert permissions rx => r-X
        usr_perm = self._convertUnixPerm( usr_perm )
        grp_perm = self._convertUnixPerm( grp_perm )
        oth_perm = self._convertUnixPerm( oth_perm )


        # concentate permission strings, store for instance
        return   [  'user::%s' % usr_perm ] \
               + [ 'group::%s' % grp_perm ] \
               + [ 'other::%s' % oth_perm ] 


    #-------------------------------------------------------------------------
    def _getUnixOwner(self, owner_string, default_onr = 0, default_grp = 0 ):
    #-------------------------------------------------------------------------
        """
        get unix owner and group from input string or set defaults
        set default values for unix owner and group
        """
        try:
            if owner_string == '' or owner_string is None:
                return( default_onr, default_grp )
        except KeyError: 
            return( default_onr, default_grp )
        try:
            if len( owner_string.split(':') ) == 1:
                return( owner_string, default_grp )
            else:
                return owner_string.split(':')

        except ValueError:
            return( owner_string, default_grp )


    #-------------------------------------------------------------------------- 
    def _getUsersGroups( self, acl_set ):
    #-------------------------------------------------------------------------- 
        """
        concentate permission string from acl_set arrays
        check if given ids are integers
        """

        obj_strings = {
            'x_usrs' : 'user' , 'r_usrs' : 'user' , 'w_usrs' : 'user' ,
            'x_grps' : 'group', 'r_grps' : 'group', 'w_grps' : 'group',
        }
        perm_strings = {
            'x_usrs' : '--x'  , 'r_usrs' : 'r-x'  , 'w_usrs' : 'rwx'  ,
            'x_grps' : '--x'  , 'r_grps' : 'r-x'  , 'w_grps' : 'rwx'  ,
        }

        # concentate arrays
        acl_text_array = []

        for key in acl_set.keys():
            if key == 'unix_owner' or key == 'unix_mode':
                continue
            yield( 
                [ 
                    "%s:%s:%s" % ( 
                        obj_strings[key], 
                        self._isInt( id, key ), 
                        perm_strings[key] 
                    ) 
                    for id in acl_set[ key ] 
                ]
            )

    #-------------------------------------------------------------------------
    def _createAcl( self, acl_array ):
    #-------------------------------------------------------------------------
        """
        Define and store posix1e.ACL handler and acl mask 
        """
        self.acl_text = ','.join( acl_array )

        try:
            self.acl  = posix1e.ACL( text = self.acl_text )
            self.mask = self.acl.calc_mask()
        except IOError, emsg:
            self._handle_acl_definition_io_error( emsg )

        self._check_acl_definition()

        # create an empty acl for acl removal
        self.rem_acl      = posix1e.ACL( text = '' )
                            
    #-------------------------------------------------------------------------
    def _handle_acl_definition_io_error( self, emsg ):
    #-------------------------------------------------------------------------
        ec  = emsg[0]
        msg = emsg[1]
        print ec, msg
        if ec == 0 and msg == 'Error':
            raise FsAclError(
                "An error in acl definition request was found. Most likely is "
                "that some user or group was defined by name but does not "
                "exist in system.\nThe acl string was '%s'" % self.acl_text
            )

    #-------------------------------------------------------------------------
    def _check_acl_definition(self):
    #-------------------------------------------------------------------------
        try:
            (acl_ec, acl_index) = self.acl.check()
        except TypeError:
            # no error found
            return
        else:
            if acl_ec == posix1e.ACL_MULTI_ERROR:
                emsg = "The ACL contains multiple entries that have a "     \
                        + "tag type that may occur at most once"            \
                        + "at index (%s)\n'%s'" % (acl_index, self.acl_text)
            elif acl_ec == posix1e.ACL_DUPLICATE_ERROR:
                emsg = "The ACL contains multiple ACL_USER or "             \
                        + "ACL_GROUP entries with the same ID"              \
                        + "at index (%s)\n'%s'" % (acl_index, self.acl_text)
            elif acl_ec == posix1e.ACL_MISS_ERROR:
                emsg = "A required entry is missing, need to calc_mask? "   \
                        + "(index %s)" % acl_index
            elif acl_ec == posix1e.ACL_ENTRY_ERROR: 
                emsg = "The ACL contains an invalid entry tag "             \
                        + "type at index (%s)\n'%s'" % (acl_index, self.acl_text)
            else:
                emsg = "Unspecified ACL error, error code '%s', index "     \
                        + "'%s'" % ( acl_ec, acl_index )
        raise FsAclError(
            "Acl definition error: %s" % emsg
        )

    #-------------------------------------------------------------------------
    def _isInt( self, id, key ): 
    #------------------------------------------------------------------------- 
        try: 
            int_val = int( id ) 
            if int_val < 0: 
                raise FsAclError( 
                    "Error in input acl_set key '%s': id '%s' is not integer!"\
                    % ( key, id ) 
                ) 
        except ValueError: 
            raise FsAclError( 
                "Error in input acl_set key '%s': id '%s' is not integer!" \
                % ( key, id ) 
            ) 
        else: 
            return int_val 


    #-------------------------------------------------------------------------
    def _convertUnixPerm(self, perm ):
    #-------------------------------------------------------------------------
        """
        Convert permission definitions like r, w, x, rx  
        to complete rwX ... strings.

        Returns a tupel of converted strings
        """
        if   perm is None or perm == '':
            return ( '---' )
        elif perm.find('w') > -1: return "rwx"
        elif perm.find('r') > -1: return "r-x"
        elif perm.find('x') > -1: return "--x"




#=============================================================================
class FsAcl(_FsAclDefine):
#=============================================================================
    """
    Set/read acl permissions on/from a single file or directory. Standard unix
    owner, group and permissions are included in acl definition handed over
    art instance creation.

    The acl set is defined at instance creation. 

    set()
        Each call to "set" quickly writes the acl to file system without 
        further checks which are done at instance creation. Any existing acl 
        is beeing overwritten.
    
    get()
        Returns an array with permissions like at instance creation, see
        __init__ doc string.

    rem()
        Completely wipe out acl definition, only standard unix owner, group
        and permissions are kept

    # read man mknod(2) for a good overview about permissions
    """

    #-------------------------------------------------------------------------
    def set(self, path = None, acl = None ):
    #-------------------------------------------------------------------------
        """
        Check if path exist resp. can be created and apply acl to path 
        (standard and default acl), non - recursive. 
        
        Unix owner and group are replaced by given id's reps. names.
        """

        try:
            self.acl
        except AttributeError:
            raise FsAclError(
                "Call .define( acl_set= ... ) first!"
            )

        # raise exception in case path does not exist or is not defined
        self._checkPathExists( path)

        # get into business: write out acl
        try:
            self.acl.applyto(path, posix1e.ACL_TYPE_ACCESS)
        except IOError, emsg:
            # handle xacl error
            self._handle_acl_error( path, emsg )

        try:
            self.acl.applyto(path, posix1e.ACL_TYPE_DEFAULT)
        except IOError, emsg:
            # ignore default acl error messages on non-directories
            # default acls can be set on directories only
            if not os.path.isdir(path) and emsg[0] == 13:
                pass
            else:
                # handle xacl error
                self._handle_acl_io_error( path, emsg )

        # set unix owner an group
        os.chown( path, self.onr, self.grp )

    #-------------------------------------------------------------------------
    def rem(self, path):
    #-------------------------------------------------------------------------
        """
        Completely wipe out acl definition, only standard unix owner, group
        and permissions are kept
        """

        # raise exception in case path does not exist or is not defined
        self._checkPathExists( path)

        # get into business: write out acl
        try:
            self.rem_acl.applyto(path, posix1e.ACL_TYPE_ACCESS)
        except IOError, emsg:
            # handle xacl error
            self._handle_acl_io_error( path, emsg)

        try:
            self.rem_acl.applyto(path, posix1e.ACL_TYPE_DEFAULT)
        except IOError, emsg:
            # ignore default acl error messages on non-directories
            # default acls can be set on directories only
            if not os.path.isdir(path) and emsg[0] == 13:
                pass
            else:
                # handle xacl error
                self._handle_acl_io_error( path, emsg )



    #-------------------------------------------------------------------------
    def get(self, path=None):
    #-------------------------------------------------------------------------
        """
        Read acl_set for a single file or directory, non - recursive. The file
        or directory must exist, otherwise FsAclError is raised. 

        Returns an array with permissions like at instance creation, see
        __init__ doc string.
        """

        # raise exception in case path does not exist or is not defined
        self._checkPathExists( path)

        x_usrs = [] 
        r_usrs = [] 
        w_usrs = [] 
        x_grps = [] 
        r_grps = [] 
        w_grps = [] 
        unix_mode = ['', '', '',]


        # iterate over all acl entries and add those entries to acl_set
        # raise if path does not exist
        for type_, name, perm in self._getAcl( path ):

            if   type_ == 'user':
                if name is '':
                    # default user's permission
                    unix_mode[0] = perm
                else:
                    # some user
                    name_int = int(name)
                    if   perm.find('w') > -1: w_usrs.append(name_int)
                    elif perm.find('r') > -1: r_usrs.append(name_int)
                    elif perm.find('x') > -1: x_usrs.append(name_int)

            elif type_ == 'group':
                if name is '':
                    # default group's permission
                    unix_mode[1] = perm
                else:
                    # some group
                    name_int = int(name)
                    if   perm.find('w') > -1: w_grps.append(name_int)
                    elif perm.find('r') > -1: r_grps.append(name_int)
                    elif perm.find('x') > -1: x_grps.append(name_int)
            elif type_ == 'other':
                # default other's permission
                unix_mode[2] = perm


        # find out user an owner for file
        try:
            uid = os.stat(path)[4]
            gid = os.stat(path)[5]
        except OSError, emsg:
            if emsg[0] == 2:
                raise FsAclError("File not found: '%s'" % path )

        # return acl_set
        acl_set = {}
        acl_set[ 'unix_mode'  ] = unix_mode
        acl_set[ 'unix_owner' ] = '%d:%d' % (uid, gid)
        if len( x_usrs ) > 0: acl_set[ 'x_usrs' ] = x_usrs 
        if len( r_usrs ) > 0: acl_set[ 'r_usrs' ] = r_usrs 
        if len( w_usrs ) > 0: acl_set[ 'w_usrs' ] = w_usrs 
        if len( x_grps ) > 0: acl_set[ 'x_grps' ] = x_grps 
        if len( r_grps ) > 0: acl_set[ 'r_grps' ] = r_grps 
        if len( w_grps ) > 0: acl_set[ 'w_grps' ] = w_grps 
       
        return acl_set

    #-------------------------------------------------------------------------
    def _getAcl(self, path=None):
    #-------------------------------------------------------------------------
        """
        Read acl for a single file or directory, non - recursive. The file
        or directory must exist, otherwise FsAclError is raised. 

        Returns a simple array with all entries. See get() for a different
        format.
        """
        try:
            # read standard acls
            for acl in posix1e.ACL(file = path):
                if acl.tag_type == posix1e.ACL_USER_OBJ:
                    yield( 'user',  '', str(acl.permset) )
                elif acl.tag_type == posix1e.ACL_GROUP_OBJ:
                    yield( 'group', '', str(acl.permset) )
                elif acl.tag_type == posix1e.ACL_OTHER:
                    yield( 'other', '', str(acl.permset) )
                elif acl.tag_type == posix1e.ACL_USER:
                    yield( 'user',  str( acl.qualifier ), str( acl.permset) )
                elif acl.tag_type == posix1e.ACL_GROUP:
                    yield( 'group', str( acl.qualifier ), str( acl.permset) )
                elif acl.tag_type == posix1e.ACL_UNDEFINED_TAG:
                    emsg = "Unknown acl tag, permset '%s' at file '%s'" \
                        % ( acl.permset, path)
                    raise FsAclError(emsg)
        except IOError, io_msg:
            # handle xacl error
            self._handle_acl_error(io_msg)


    #-------------------------------------------------------------------------
    def _checkPathExists(self, path=None):
    #-------------------------------------------------------------------------
        """
        Raise exception in case path does not exist or is not defined
        """

        if path is None:
            raise FsAclError(
                "_checkPathExists: path is not defined!"
            )
            
        if not os.path.exists( path ):
            raise FsAclError(
                "Could not read acl from path '%s': file not found!" % path
            )


    #-------------------------------------------------------------------------
    def _handle_acl_io_error( self, path, emsg ):
    #-------------------------------------------------------------------------
        """
        Handle posix acl error message grind
        """
        # handle io error code
        ( ec,  msg   ) = emsg
        if   ec == 2:
            emsg = "Target '%s' not found!" % path

        elif msg == "Permission denied" and ec == 13:
            emsg = "Permission denied on '%s', this is most likely " % path \
                   + "an error setting DEFAULT ACLS when no standard ACLS " \
                   + "are defined or when truely there is an IO problem "   \
                   + "on this file."

        elif ec == 95:
            emsg = "Acls not supported at '%s'\n%s( code %s )"  \
                   % (os.path.realpath( path ), msg, ec ) 

        else:
            emsg = "Unspecifed IO error setting acl at '%s'"    \
                   + "\n%s ( code %s )" % (path, msg, ec )

        raise FsAclError( emsg )

#=============================================================================
if __name__ == "__main__":
#=============================================================================
    import sys
    import os

    try:
        from pylin.fs import fstools
    except ImportError, emsg:
        raise FsAclError(
            "Could not import secu-ring pylin fs tools module, try 'aptitude " \
            + "install srx-pylin from http://deb.secu-ring.de\n%s" % emsg
        )


    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
    sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', 0)
    acl_set = {
    'w_grps'    : [1004], 
    'r_usrs'    : [ 400, "78"], 
    'unix_mode' : ['rw', 'rwx', ''],
    'unix_owner' : '7',
    
    }

    file = '/srv/test/xaclssd'
    #fstools.createFile( file )
    try:
        acl = FsAcl()
        print acl.get(file)
        acl = FsAcl( )
        acl.define( acl_set=acl_set )
        acl.set(path=file)
        print acl.get(file)
#        acl.rem(path=file)
        print acl.get(file)
    except FsAclError, emsg:
        raise
        print emsg
        sys.exit(1)

    sys.exit(0)

