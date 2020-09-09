#!/usr/bin/python
# -*- coding: utf-8 -*-
#vim:fdm=marker
# unlock vim folding via zR, zo and lock folding via zM, zc
#----------------------------------------------------------------------------
"""                                                                     
DESCRIPTION    simple directory handler functions                        {{{1

USAGE          see __doc__ strings or test section for example use
      
CHANGELOG    
   10-02-12    * creation, copied from fstools.py

TODO

THANKS TO

"""

__version__ = "$Revision: 0.1.2010-02-12 $"
# $Source$


#----------------------------------------------------------------------------
# modules import, constants                                              {{{1
#----------------------------------------------------------------------------

# module export
__all__ = [
    'SplitterError',
    'Splitter'
]

# standard
import logging
log = logging.getLogger( __name__ )
import subprocess
import os
from datetime import datetime
import sys


# extra modules
import pexpect
from pt.files.rdiff import date_time
from pt.data import uniq

#----------------------------------------------------------------------------
# error classes                                                          {{{1
#----------------------------------------------------------------------------
class Error(BaseException):
    """Base class for module errors"""
class SplitterError(Error):
    """Some Error"""


class Splitter:
    """
    rdiff-backup repository splitter
    METHODS
    yield_sessions: return iterator for all backup sessions in repository

    VARIABLES
    mirror_dir
    rdiff_dir
    sessions

    """
    RDIFF_DIR = "rdiff-backup-data"

    def __init__(self, mirror_path):

        # check mirror
        if os.path.exists( mirror_path ):
            self.mirror_dir = mirror_path
        else:
            raise SplitterError(
                "Could not access local rdiff-backup mirror '%s', try harder"
                % mirror_path
            )

        self.rdiff_dir = mirror_path + os.sep + self.RDIFF_DIR

        # fetch information about rdiff sessions
        self.sessions = []
        for entry in os.listdir( rdiff_path):
            if entry.startswith("session_statistics"):
                dt = datetime.strptime(
                        entry[0:38], 'session_statistics.%Y-%m-%dT%H:%M:%S'
                )
                self.sessions.append( dt)

        self.sessions.sort()


    def yield_sessions(self):
        for session in sessions:
            yield session


    def calculate_schedule(self, S, M, H, d, m, w, Y ):
        """
        Calculate time stamps for the dates at which 
        a backup should be present
        """


# prepare schedule time objects: obtain 
if __name__ == "__main__":
    import sys
    import os
    import pt.terminal # flush buffers, colors, terminal size
    import pt.logger   # set up logger

    # logger
    log        = pt.logger.Logger( level = logging.DEBUG, style = "plain" )

    # read increments currently available
    REPO_PATH = "/srv/backup/data/alt/hwa5-schweinfurt"
    rdiff_path = REPO_PATH + os.sep + "rdiff-backup-data"

    splitter = Splitter( REPO_PATH )

    # calculate which increments shall be kept
    schedule = date_time.get_dates( {
        'secondly'  : 1,
        'minutely'  : 1,
        'hourly'    : 2,
        'daily'     : 3,
        'weekly'    : 1,
        'monthly'   : 2,
        'yearly'    : 1,
    } )

    
    # increments which must be kept are those near to the dates calculated above
    # loop through schedule dates and check if there is some increment 
    # present which fits to this date more than another
    def _store_keep_list( session_date, schedule_date):
        """Store session date stamps to keep_ arrays"""

        # store schedules which need this backup set
        intervalls=[]
        if schedule_date in schedule['secondly' ]:
            intervalls.append(       "secondly" )
        if schedule_date in schedule['minutely' ]:
            intervalls.append(       "minutely" )
        if schedule_date in schedule['hourly' ]:
            intervalls.append(       "hourly"   )
        if schedule_date in schedule['daily'    ]:
            intervalls.append(       "daily"    )
        if schedule_date in schedule['weekly'   ]:
            intervalls.append(       "weekly"   )
        if schedule_date in schedule['monthly'  ]:
            intervalls.append(       "monthly"  )
        if schedule_date in schedule['yearly'   ]:
            intervalls.append(       "yearly"   )
        keep_list.append( {
           'intervalls': intervalls,
           'session_date' : session_date        ,
           'schedule_date': schedule_date       ,
        } )


    keep_list  = []
    schedule_dates = sorted( 
        uniq (
            schedule['secondly'] + \
            schedule['minutely'] + \
            schedule['hourly'  ] + \
            schedule['daily'   ] + \
            schedule['weekly'  ] + \
            schedule['monthly' ] + \
            schedule['yearly'  ]  
        ) 
    )
    for schedule_date in schedule_dates:
        for counter, session_date in enumerate( splitter.sessions):
            # skip look what sessions need to be kept
            try:
                if schedule_date > session_date \
                and schedule_date < splitter.sessions[counter + 1 ]:
                    _store_keep_list( session_date, schedule_date )
            except IndexError:
                if schedule_date > session_date:
                    _store_keep_list( session_date, schedule_date )

    for i in sorted(keep_list):
        print i

#            keep_dates.append{
#                'session_date' : session_date,
#                'schedule_date': schedule_date,
#
#            }
#            print "keep:", session_date, schedule_date

#            if schedule_date in days:
#                print "daily"

#        log.info( 
#            "%s day %2d (%s): " 
#            % ( action, idays, day.strftime("%Y-%m-%d")  ) 
#        )




    #def run_cmd( cmd):
    #
    #    child = pexpect.spawn(cmd, timeout=None)
    #    while True:
    #        try:
    #            out = child.readline()
    #            if out =='':
    #                continue
    #            yield out.rstrip()
    #        except pexpect.EOF:
    #            break
    #
    #for line in run_cmd( "rdiff-backup -l ." ):
    #    print  line

