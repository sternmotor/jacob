#!/usr/bin/env python
# -*- coding: utf-8 -*-
#vim:fdm=marker
# unlock vim folding via zR, zo and lock folding via zM, zc
#----------------------------------------------------------------------------
"""                                                                     
DESCRIPTION    rdiff-backup statistics methods                          {{{1

USAGE          see __doc__ strings or test section for example use
      
CHANGELOG    
   10-02-12    * creation, copied from fstools.py

TODO

THANKS TO

"""

__version__ = "$Revision: 0.1.2010-10-05 $"
# $Source$


#----------------------------------------------------------------------------
# modules import, constants                                              {{{1
#----------------------------------------------------------------------------

# module export
__all__ = [
    "Error",
    "RdiffStatistics"        ,
    "RdiffStatisticsError"   ,
    "OptionsError"      ,
]

# standard
import logging
log = logging.getLogger( __name__ )
import os
import sys
import glob
import datetime
from pt.data.validate import is_float, is_integer, VdtTypeError



 
#----------------------------------------------------------------------------
# error classes                                                          {{{1
#----------------------------------------------------------------------------
class Error(BaseException):
    """General rdiff-backup errors"""
class RdiffStatisticsError(Error):
    """Errors analyising repository statistics"""
class OptionsError(Error):
    """Error in unit options handed over"""


class RdiffStatistics:
    """
    Class handling repository statistics (times, sizes). All sizes are returned
    in bytes.
    This is not super - accurate but fast.

    DESCRIPTION
    FEATURES
    OPTIONS
        path           * directory where the rdiff-backup resides in
                         ( path/rdiff-backup-data must exists!)
    METHODS
        __init__       * initialize repository (store path, do some checks)
        getLastSession * return last sessions statistics with no full size
        getFullHistory * yield  session statistics with repository full size  
                        calculation
    EXCEPTIONS
    LOGGING
    EXAMPLE
    """

    # class variables    
    RDIFF_DIR_NAME      = "rdiff-backup-data"
    DEFAULT_SESSION_FILE_LINES = 18            # if session file length

    def __init__(self, path ):
       
        # check path
        self.rdiff_dir = path + os.sep + self.RDIFF_DIR_NAME

        if not os.path.isdir( path ):
            raise OptionsError(
                "Path '%s' does not exist or is no directory" % path
            )
        if not os.path.isdir( self.rdiff_dir ):
            raise OptionsError(
                "Rdiff-Backup directory '%s' not found in '%s' !" 
                % (self.RDIFF_DIR_NAME, path)
            )


    def getLastSession(self):
        """ find latest session file, return contents as array """
        for data in self.getFullHistory():
            pass
        return data

    def getFullHistory(self):
        """ Return list containing full backup history """

        # history container
        sessions = []

        # get sorted file list of all session files
        session_files = self._getSessionFileList()

        # determine base size from oldest backup increment
        base_file        = self.rdiff_dir + os.sep + session_files[0] 
        base_mirror_size = self._readSessionStats( base_file )['MirrorFileSize']

        # iterate over all session files, return statistics data
        cum_size = base_mirror_size   # cumulative size inc + mir
        mir_size = 0                  # size of user data (mirror)
        inc_size = 0                  # size of increment data

        for file in session_files:
            session_data = self._readSessionStats(  self.rdiff_dir + os.sep + file )
            cum_size    += session_data['TotalDestinationSizeChange']
            inc_size    += session_data['IncrementFileSize'         ]
            mir_size     = session_data['MirrorFileSize'            ]   # = cum - inc

            log.debug( 
                "%s: cum=%s, inc=%s, mir=%s "
                % ( session_data['EndDate'], cum_size, inc_size, mir_size )
            )
            session_data['CumulativeSize'] = cum_size
            session_data['IncrementsSize'] = inc_size
            session_data['DataMirrorSize'] = mir_size

            sessions.append(session_data)

        # The needed full repository size( Cumulative Size) at a given time
        # is the latest cumulative size minus the sum of all older increments
        for session_data in sessions:
            session_data['NeededRepoSize'] = cum_size - session_data['IncrementsSize']

            yield session_data            


    def _readSessionStats(self, file):
        """read single session file"""
        # container for stat data
        stats = {}

        # open session file,reasd all stats
        log.debug( "Reading session file '%s'" % file )
        for line in open( file, 'r' ).readlines():
            par = line.split()[0]
            val = line.split()[1]
            try: 
                stats[ par ] = is_integer( val ) 
            except VdtTypeError:
                try:
                    stats[ par ] = is_float( val )
                except VdtTypeError:
                    raise StatisticsError(
                        "Error reading session file '%s': cannot convert"
                        " second value in '%s' to integer or float!"
                        % (file, line )
                    )
            # convert stats['EndTime'] to stats['EndDate'  ] 
            if par == 'StartTime' or par == 'EndTime':
                stats[ par.replace( 'Time', 'Date' ) ] \
                = str( datetime.datetime.fromtimestamp( stats[ par ] )
                ).split('.')[0]

        return stats

    def _getSessionFileList(self):
        """ Return sorted list of session file entries in backup dir """
        session_files = []
        glob_expr = 'session_statistics.*.data'
        for entry in glob.glob( self.rdiff_dir + os.sep + glob_expr):
            session_files.append( os.path.basename( entry ) )
        return sorted( session_files)


#----------------------------------------------------------------------------
# tests and example invocation                                           {{{1
#----------------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    import os
    import pt.terminal # flush buffers, colors, terminal size
    import pt.logger   # set up logger
    from pt.data import numbers, units

    # initialize logger
    log = pt.logger.Logger(
#        style = "plain",
        name         = __name__ , # __name__ or self.__class__.__name__ 
        level        = logging.INFO
    )

