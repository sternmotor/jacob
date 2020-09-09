#!/usr/bin/python
from datetime import datetime, timedelta, MINYEAR, MAXYEAR
import calendar
from pt.data import validate
import logging
log = logging.getLogger( __name__ )


__version__ = "$Revision: 0.1.2011-01-10 $"
__all__=['get_dates']

class GetDatesError(BaseException):
    """Error analysing schedule"""

def get_rdiff_time( file_name ):
    """
    Return datetime.datetimeobject for a time given 
    in rdiff-backup format (like current - mirror marker)
            
    Expects filename like current_mirror.2011-05-26T09:47:14+02:00.data
    """ 
    full_string = file_name.split('.')[1]
    date_string = full_string[:19]
    date_time   = datetime.strptime(
        date_string, '%Y-%m-%dT%H:%M:%S')
    return date_time


def _get_date_time( year, month, day, hour=0, minutes=0, seconds=0):
    return datetime.strptime( 
        "%04d%02d%02d%02d%02d%02d" % (
            validate.is_integer( year    , MINYEAR, MAXYEAR ),
            validate.is_integer( month   , 0, 12 ), 
            validate.is_integer( day     , 0, 53 ),
            validate.is_integer( hour    , 0, 23 ),
            validate.is_integer( minutes , 0, 59 ),
            validate.is_integer( seconds , 0, 59 ),
        ),
        '%Y%m%d%H%M%S'
    )

def get_dates( schedule ):
    """
    Expects associative array as input for schedule, returns an array.

    Return hash of arrays (day_dates, sunday_dates, month_end_days, 
    year_end_days) for a given number of maximum dates sundays months 
    and years.
    All dates are returned in datetime.datetime format.
    """

    if type(schedule ) is not type({}):
        raise GetDatesError(
            "get_dates_hash() expects an hash/associative array as input!"
        )

    # check input
    max_S = validate.is_integer( schedule['secondly'], 0 )
    max_M = validate.is_integer( schedule['minutely'], 0 )
    max_H = validate.is_integer( schedule['hourly'  ], 0 )
    max_d = validate.is_integer( schedule['daily'   ], 0 )
    max_w = validate.is_integer( schedule['weekly'  ], 0 )
    max_m = validate.is_integer( schedule['monthly' ], 0 )
    max_Y = validate.is_integer( schedule['yearly'  ], 0 )

    # prepare output array
    res = {
        'secondly' : [],
        'minutely' : [],
        'hourly'   : [],
        'daily'    : [],
        'weekly'   : [],
        'monthly'  : [],
        'yearly'   : [],
    }

    # define loops start 
    now = datetime.now()

    # loop years
    start_year = int(now.strftime("%Y") ) 
    for year in range( start_year , start_year -1 - max(
            max_Y,
            int( max_m/12                   ),
            int( max_w/51                   ),
            int( max_d/365                  ),
            int( max_H/( 365 * 24 )         ),
            int( max_M/( 365 * 24 * 60 )    ),
            int( max_S/( 365 * 24 * 3600 )  ),
        ) , -1):

        # handle year
        year_end = _get_date_time( year, 12, 31  ) 
        if len(res['yearly']) < max_Y and year_end < now:
            res['yearly'].append( year_end )

        # loop months
        for month in range( 12, 0, -1 ):
            # obtain last day in month
            days_in_month= calendar.monthrange( year, month )[1]
            month_end = _get_date_time( 
                year, 
                month,
                days_in_month,
            )
            # handle month
            if len(res['monthly']) < max_m and month_end < now:
                res['monthly'].append( month_end )

            # loop all days in current month
            for loop_day in range( days_in_month, 0, -1 ):
                day = _get_date_time(
                    year,
                    month,
                    loop_day
                )
                if day < now:
                    # handle weekends (sunday)
                    week_day = day.isoweekday()
                    if len(res['weekly']) < max_w and week_day == 7: 
                        res['weekly'].append( day)
                    # handle days
                    if len(res['daily']) < max_d:
                        res['daily'].append( day )

    # loop hrs 
    for hour in range( 1, max_H + 1 ):
        if len( res['hourly'] ) < max_H:
            then = now - timedelta(hours=hour )
            yearmonthday = datetime.strftime(then, '%Y-%m-%d')
            hour= int( datetime.strftime(then, '%H')) +1
            res['hourly'].append( 
                datetime.strptime(
                    "%s %02d:00:00" % (yearmonthday, hour),
                    '%Y-%m-%d %H:%M:%S'
                ) 
            )
        else: 
            break

    # loop minutes
    for minute in range( 1, max_M + 1 ):
        if len( res['minutely'] ) < max_M:
            then = now - timedelta(minutes=minute )
            yearmonthdayhour= datetime.strftime(then, '%Y-%m-%d %H')
            minute= int( datetime.strftime(then, '%M')) +1
            res['minutely'].append( 
                datetime.strptime(
                    "%s:%02d:00" % (yearmonthdayhour, minute),
                    '%Y-%m-%d %H:%M:%S'
                ) 
            )
        else: 
            break

    # loop seconds
    for second in range( 1, max_S + 1 ):
        if len( res['secondly'] ) < max_S:
            then = now - timedelta(seconds=second )
            res['secondly'].append( then )
        else: 
            break

    return res

if __name__ == "__main__":
    import sys
    import os
    import pt.terminal # flush buffers, colors, terminal size
    import pt.logger   # set up logger

    dates = get_dates( {
        'secondly' : 4 ,
        'minutely' : 2 ,
        'hourly'   : 1 ,
        'daily'    : 6 ,
        'weekly'   : 3 ,
        'monthly'  : 2 ,
        'yearly'   : 10 ,
        }
    )
    for key in dates.keys():
        print key
        for date in dates[key]:
            print date
