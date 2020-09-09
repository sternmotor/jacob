#!/usr/bin/python
import os
    

class FsTravelError(Exception):
    """
    Errors occurring descending into filesystem tree
    """
class FsTravel:
    """
    Methods for traveling up or down a filesystem tree. Instanciation returns
    an iterator yielding (parent, dirs, files, links, others) tupel for each "valid" 
    directory.
    
    "Valid" means that the "self.isValidDir()" method returns true for this
    path. This method can be freely overwritten and may contain e.g. permission
    checks or name filters.

    In case path is not a directory, an exception is raised.

    METHODS
    __init__( depth, follow_links ) : 
        depth : maximum depth which should be descented or ascendet 
          start dir is 0
        * depth = -1: travel until file system root '/' or
          end of tree is reached, depending on direction setting
        * depth = 0 : return dir itself, check validity
        * depth > 0 : travel down to specified depth
        
        follow_links:
        * True: follow links in case they point to directories, False: not

    start( path, direction="down" )      
                       * start either descending or ascending, specify direction
    travelUp( path )   * ascend the file system tree
    travelDown( path ) * descend the file system tree

    EXCEPTIONS
    FsTravelError
    """
    def __init__(
        self, 
        depth=-1, 
        follow_links = True, 
    ):
        """
        See class docstring, default values are:
        depth      = -1   : travel until file system root '/' or end 
        follow_links = True: follow links in case they point to directories
        """

        self.DEPTH        = depth
        self.FOLLOW_LINKS = follow_links

    #--------------------------------------------------------------------------
    def travel( self, path, depth=None ):
    #--------------------------------------------------------------------------
        """Standard: travel down"""
        return self.start( path, depth=depth, direction='down' )
    #--------------------------------------------------------------------------
    def travel_down( self, path, depth=None ):
    #--------------------------------------------------------------------------
        return self.start( path, depth=depth, direction='down' )
    #--------------------------------------------------------------------------
    def travel_up( self, path, depth=None ):
    #--------------------------------------------------------------------------
        return self.start( path, depth=depth, direction='up' )

    #--------------------------------------------------------------------------
    def start( self, path, depth=None, direction="down" ):
    #--------------------------------------------------------------------------
        """ 
        Iterate over "valid" directory entries, yield each directory

        When depth = 0, return directory itself (after checking for validity)

        direction = down: travel down the directory dir, the default
                    up: travel up the tree and list each dir in path
                    until file system root or depth levels is reached
        """
        # set (default) depth from __init__ if not specified
        if depth == None:
            depth = self.DEPTH

        # check if start path exists
        if not os.path.exists( path ):
            raise FsTravelError( "Could not find start directory '%s'" % path )
        else:
            if not os.path.isdir( path ):
                raise FsTravelError( "Start path '%s' is no directory" % path )

        # start recursive travel
        if direction == 'down':
            # descend into directory
            return self._travel_down( path, maxdepth=depth )
            #return self._listDirEntries( path, self._list_start(path) )
        else:
            # ascent up
            #return self._listDirEntries( path, self._list_start(path) )
            return self._travel_up( path, maxdepth=depth )

    #--------------------------------------------------------------------------
    def _list_start( self, path ):
    #--------------------------------------------------------------------------
        """ dummy function for showing entry point later in _listAllEntries"""
        return path
        
    #--------------------------------------------------------------------------
    def _travel_down( self, path=None, depth=0, maxdepth=None ):
    #--------------------------------------------------------------------------
        newdepth = depth  + 1
        if depth == 0:
            if self.isValidDir(path):
                yield([path])
        if ( not newdepth > maxdepth ) or ( maxdepth == -1 ):
            dirs = self._listDirEntries( path, os.listdir )
            for dir in dirs:
                for newdirs in self._travel_down( dir, newdepth, maxdepth ):
                    yield( newdirs )
            yield( dirs )

    #--------------------------------------------------------------------------
    def _travel_up( self, path = None, maxdepth=None ):
    #--------------------------------------------------------------------------
        # split path into number of parts corresponding to maxdepth
        path_segments = os.path.realpath( path ).split( os.sep )
        path_segments[0] = os.sep
        path_length = len( path_segments )
        for ( count, segment) in enumerate ( path_segments ):
            # consider maximum depth definition
            if ( count > maxdepth - 1 ) and (maxdepth > 0 ):
                break

            # concentate current path
            current_path = os.sep.join( path_segments[:path_length - count])
            current_path = current_path.replace( 
                '%s%s' % (os.sep, os.sep), os.sep 
            )

            # list and return path  (contents)
            if self.isValidDir( current_path):
                yield current_path
            else:
                continue
            #yield self._listDirEntries( current_path )
        


    #--------------------------------------------------------------------------
    def _listDirEntries(self, path, list_function ):
    #--------------------------------------------------------------------------
        """ Returns an array with all directories here """

        dirs = []

        # speed up loop below by avoiding to resolve namespaces
        isLink = os.path.islink
        isDir  = os.path.isdir

        for entry in self._listAllEntries( path, list_function ):
            try:
                entry = entry.encode( 'utf-8' )
            except UnicodeDecodeError:
                pass
            # order is important here: links first for sorting functionality
            # the if... cascade for each file dir other part here is 
            # optimized for speed (not calling methods isValid... not needed),
            # test carefully (e.g. against find /usr > /dev/null) when changing
            if   isLink( entry ) and self.FOLLOW_LINKS is False:
                continue

            elif isDir(  entry ):
                if self.isValidDir( entry ):
                    dirs.append( entry )
            else:
                continue

        return( sorted( dirs )  )

    #--------------------------------------------------------------------------
    def _listAllEntries(self, path, list_function ):
    #--------------------------------------------------------------------------
        """
        List all contents of given path as generator.
        """

        # speed up loop below by avoiding to resolve namespaces
        sep = os.sep

        # list directory entries
        try:
            for entry in list_function(path):
                # os.path.join is much slower here
                yield( "%s%s%s" % (path, sep, entry ) )
        except OSError, emsg:
            if emsg[0] == 2:
                raise FsTravelError(
                    "Path '%s' not found!\n%s" % ( path, emsg [1] )
                )
            else:
                raise

    #--------------------------------------------------------------------------
    def isValidDir(self, path):
    #--------------------------------------------------------------------------
        """
        Return True if path is a valid directory. Overload this method for
        implementing filters and path manipulators. Return False or 
        path name.
        """
        return True

#==============================================================================
# test structure
#==============================================================================

if __name__ == "__main__":
    import sys
    # remove actual dir from search path
    sys.path.pop(0)
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
    sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', 0)
#    from pylin.output import terminal

    t = FsTravel()
    for dirs in t.travel_up( '/etc/ssl', depth = 1 ):
        print dirs
#        for dir in dirs:
#            print dir


