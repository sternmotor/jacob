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


# standard
import logging
log = logging.getLogger( __name__ )

#----------------------------------------------------------------------------
# modules import, constants                                              {{{1
#----------------------------------------------------------------------------

from pt.files.rdiff.statistics import *

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

    try:
        statistics = RdiffStatistics( sys.argv[1] )
    except:
        statistics = RdiffStatistics( '/srv/backup/data/sr1-devel/' )


    try:
        #print statistics.getLastSession()

        unit_factor = units.FACTORS1024[ 'Mi' ]

        for data in statistics.getFullHistory():
            print (
                "%s: needed=%s, data=%s, increments=%s, all=%s, changes=%s"
                % (
                    data['EndDate'            ],
                    numbers.renice( "%12.2f", data['NeededRepoSize'     ] / unit_factor ),
                    numbers.renice( "%12.2f", data['DataMirrorSize'     ] / unit_factor ),
                    numbers.renice( "%12.2f", data['IncrementsSize'     ] / unit_factor ),
                    numbers.renice( "%12.2f", data['CumulativeSize'     ] / unit_factor ),
                    numbers.renice( "%12.2f", (
                        data['DeletedFileSize']   
                        + data['NewFileSize']     
                        + data['ChangedMirrorSize']
                        )  / unit_factor
                    )
                )
            )

#        for key in data.keys():
#            try:
#                print key, numbers.renice( "%12.2f", data[key] / unit_factor)
#            except:
#                pass
#        history = statistics.getRepoSize()
#        print "Date                ", "|%-14s" % "Cumulative Size", "|%-14s" % "Needed Space"
#        for line in history:
#            print "%s     |%12.2f|%12.2f" % line
    except Error, emsg:
        print emsg
        sys.exit(1)


