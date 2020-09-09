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
    "Statistics"   ,
    "getLastSession"    ,
    "getHistory"        ,
    "getFullSize"       ,
    "getIncSize"        ,
]

# standard
import logging
log = logging.getLogger( __name__ )
import os
import sys
import datetime
import glob
from pt.data.validate import is_float, is_integer, VdtTypeError
import sqlite3 as sqlite # python 2.5



RDIFF_DIR_NAME      = "rdiff-backup-data"
DB_NAME             = "session_statistics.db"
 
#----------------------------------------------------------------------------
# error classes                                                          {{{1
#----------------------------------------------------------------------------
class Error(BaseException):
    """General rdiff-backup errors"""
class StatisticsError(Error):
    """Errors analyising repository statistics"""
class OptionsError(Error):
    """Error in unit options handed over"""


class Statistics:
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
    RDIFF_DIR_NAME  = RDIFF_DIR_NAME
    DB_NAME         = DB_NAME


    def __init__(self, path ):
       
        # set path variables
        self.repos_dir  = path      
        self.rdiff_dir = path + os.sep + self.RDIFF_DIR_NAME

        if not os.path.isdir( path ):
            OptionsError(
                "Path '%s' does not exist or is no directory" % path
            )
        if not os.path.isdir( self.rdiff_dir ):
            OptionsError(
                "Rdiff-Backup directory '%s' not found in '%s' !" 
                % (self.RDIFF_DIR_NAME, path)
            )


        # initiate database, create empty tables
        self.db = sqlite.connect(self.rdiff_dir + os.sep + self.DB_NAME)
        self.db.execute(
            '''CREATE TABLE IF NOT EXISTS %s ( 
                id INTEGER NOT NULL PRIMARY KEY,
                file_name   TEXT
            )''' % 'read_stats'
        )
        self.db.execute(
            '''CREATE TABLE IF NOT EXISTS %s (
                id INTEGER NOT NULL PRIMARY KEY
            )''' % 'calc_stats'
        )


    def updateDb(self):
        """Load or create sqlite db file, make sure all session files
        are mirrored 1:1 in data base (delete outdated data sets, read
        new session files into db
        """

        # get current 'session_statistics.*.data' file's list
        self._updateFileList( table='file_list' )
        
        # compare file list and exisiting data: import all data
        # which are not present in current tables

        try:
            for session in self.db.execute('''
                SELECT file_name FROM 'file_list' EXCEPT SELECT file_name FROM 'read_stats'
            '''):
                print session, "CCC"
        except sqlite.OperationalError, emsg:
            # no table data found in 'read_stats', load all values
            for id, session in self.db.execute('''
                SELECT * FROM 'file_list'
            '''):
                self._loadSession( self.rdiff_dir + os.sep + session )

        # drop all read_stats and calc_stats entries which are
        # not presented as session files in rdiff-backup dir
        


    def _loadSession( self, file, table='read_stats'):
        """Load a session file's contents to database"""

        stats = {}

        # open session file,read all stats
        log.debug( "Reading session file '%s'" % file )
        for line in open( file, 'r' ).readlines():
            par = line.split()[0]
            val = line.split()[1]
            # value must be in or float
            try: 
                val = is_integer( val ) 
            except VdtTypeError:
                try:
                    val = is_float( val )
                except VdtTypeError:
                    raise StatisticsError(
                        "Error reading session file '%s': cannot convert"
                        " second value in '%s' to integer or float!"
                        % (file, line )
                    )

            # store par, val in database
            self.db.execute(
                '''ALTER TABLE 'read_stats' ADD %s TEXT''' % par
            )
            self.db.execute(
                '''INSERT INTO 'read_stats' (%s) VALUES (%s)'''
                % (par, val )
            )

            # convert stats['EndTime'] to stats['EndDate'  ] 
            if par == 'StartTime' or par == 'EndTime':
                stats[ par.replace( 'Time', 'Date' ) ] \
                = str( datetime.datetime.fromtimestamp( stats[ par ] )
                ).split('.')[0]
#            raise StatisticsError(
#                "Found unknown data type in statistics file '%s', second "
#                "value is '%s' but should be integer or float"
#                % ( file, val )
#            )

        else:        
            return stats


    def _updateFileList(self, table='file_list'):
        """ read current list of session statistics files into table"""

        # drop old list table if exists
        self.db.execute(
            '''DROP TABLE IF EXISTS %s''' % table )
        self.db.execute(
            '''CREATE TABLE IF NOT EXISTS %s (
                id          INTEGER PRIMARY KEY,
                file_name   TEXT
            )''' % table
        )

        # load all files into db
        glob_expr = 'session_statistics.*.data'
        for file_path in glob.glob( self.rdiff_dir + os.sep + glob_expr):
            self.db.execute( 
                ''' INSERT INTO %s (file_name) VALUES ('%s') '''  
                % ( table, os.path.basename( file_path ) )
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
        for entry in os.listdir( self.rdiff_dir ):
            if 'session_statistics.' in entry:
                session_files.append( entry )
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
        level        = logging.DEBUG
    )

    try:
        statistics = Statistics( sys.argv[1] )
    except:
        statistics = Statistics( '/srv/backup/data/sr1-devel/' )

    statistics.updateDb()


#    try:
#        #print statistics.getLastSession()
#
#        unit_factor = units.FACTORS1024[ 'Mi' ]
#
#        for data in statistics.getFullHistory():
#            print (
#                "%s: needed=%s, data=%s, increments=%s, all=%s, changes=%s"
#                % (
#                    data['EndDate'            ],
#                    numbers.renice( "%12.2f", data['NeededRepoSize'     ] / unit_factor ),
#                    numbers.renice( "%12.2f", data['DataMirrorSize'     ] / unit_factor ),
#                    numbers.renice( "%12.2f", data['IncrementsSize'     ] / unit_factor ),
#                    numbers.renice( "%12.2f", data['CumulativeSize'     ] / unit_factor ),
#                    numbers.renice( "%12.2f", (
#                        data['DeletedFileSize']   
#                        + data['NewFileSize']     
#                        + data['ChangedMirrorSize']
#                        )  / unit_factor
#                    )
#                )
#            )
#
#        for key in data.keys():
#            try:
#                print key, numbers.renice( "%12.2f", data[key] / unit_factor)
#            except:
#                pass
#        history = statistics.getRepoSize()
#        print "Date                ", "|%-14s" % "Cumulative Size", "|%-14s" % "Needed Space"
#        for line in history:
#            print "%s     |%12.2f|%12.2f" % line
#    except Error, emsg:
#        print emsg
#        sys.exit(1)


