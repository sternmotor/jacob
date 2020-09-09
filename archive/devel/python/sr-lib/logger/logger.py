#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
 DESCRIPTION  simple logging initiator, 
 
 USAGE        
              see class docstring
 CHANGELOG    



 TODO
 
 THANKS TO


    # see http://sgillies.net/blog/832/python-logging/


"""

__version__ = "$Revision: 0.1.2010-08-02 $"
# $Source$

__all__ = [
    'LoggerError',
    'Logger',
]

import logging
from sys import stdout as sys_stdout
from sys import stderr as sys_stderr

# mail data
#RELAY_USER = "servermail@secu-ring.de"
#RELAY_PASS = "20000meilenuntermeer"
#RELAY_HOST = "mail.secu-ring.de"

DEFAULT_INFO_STYLE     = 'time' 
DEFAULT_DEBUG_STYLE    = 'long' 
DEFAULT_WARN_STYLE     = 'short'
DEFAULT_ERROR_STYLE    = 'short'
DEFAULT_CRITICAL_STYLE = 'long' 


#------------------------------------------------------------------------------
class LoggerError(Exception):
#------------------------------------------------------------------------------
    pass


def Logger( 
    name          = None           ,   # module name, None for root logger
    level         = logging.INFO   ,   # console verbosity
    style         = "short"         ,  # plain short long
    file_level    = None           ,   # log file verbosity
    file_file     = None           ,   # log file 
    file_style    = "short"         ,  # plain short long
#    mail_level    = None           ,   # mail verbosity
#    mail_sender   = "LogSender"    ,
#    mail_addrs    = []             ,
#    mail_subject  = "LogSubject"   ,
#    mail_user     = RELAY_USER     ,
#    mail_pass     = RELAY_PASS     ,
#    mail_host     = RELAY_HOST     ,
    
    ):
    """
    style plain: just write message
    style short: log file style message
    style long:  debug style message

    This function is a setup of the root logger where various logger may be child
    from. For setting up a non-root logger, define "name" parameter

    Initialise childs like
    log = logging.getLogger("fly.logging.loggi")
    or
    self.log = logging.getLogger("%s:%s" % (__name__,self.__class__.__name__) )
    """

    # create log handler depending on log level
    class LevelFilter(logging.Filter):
        def __init__(self, level):
            self.level = level
        def filter(self, record):
            return self.level == record.levelno

    def make_handler(outstream, format, filter_level, display_level):
        handler = logging.StreamHandler(outstream)
        formatter = logging.Formatter(format, '%Y-%m-%d %H:%M:%S')
        handler.setFormatter(formatter)
        handler.setLevel( display_level)
        handler.addFilter(LevelFilter(filter_level))
        return handler

    if (not style == "plain") and (not style == "short" ) and (not style == "long"):
        raise LoggerError(
            "Style parameter needs to be one of 'plain', 'short' or 'long'!"
        )

    format_string = {
        'plain' : "%(message)s",
        'time'  : "%(asctime)s  %(message)s",
        'short' : "%(asctime)s  %(name)s\t%(levelname)-8s: %(message)s",
        'long'  : "%(asctime)-20s %(levelname)-8s%(name)s:%(funcName) s[%(lineno)d]:\t%(message)s",
    }

    # initiate "name" logging instance
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)


    # create file handler and set level + format
    if ( file_level is not None) and (file_file is not None):
        try:
            file_h = logging.FileHandler(file_file)
        except AttributeError:
            raise LoggerError(
                "Could not set up log file, file_file '%s' is garbage" % file_file 
            )
        except IOError:
            raise LoggerError(
                "Could not create log file '%s'" % file_file 
            )
        file_h.setLevel(file_level)
        file_formatter = logging.Formatter( format_string[file_style] )
        file_h.setFormatter( file_formatter )
        logger.addHandler( file_h )

    # create console handler and set level + format
    if level is not None:
    # print info messages to stdout, all other to stderr
        logger.addHandler( make_handler(sys_stdout, format_string[DEFAULT_INFO_STYLE    ], logging.INFO    , level))
        logger.addHandler( make_handler(sys_stderr, format_string[DEFAULT_DEBUG_STYLE   ], logging.DEBUG   , level))
        logger.addHandler( make_handler(sys_stderr, format_string[DEFAULT_WARN_STYLE    ], logging.WARN    , level))
        logger.addHandler( make_handler(sys_stderr, format_string[DEFAULT_ERROR_STYLE   ], logging.ERROR   , level))
        logger.addHandler( make_handler(sys_stderr, format_string[DEFAULT_CRITICAL_STYLE], logging.CRITICAL, level))

#    # create mail handler and set level + format
#    if mail_level is not None:
#
#        from logging.handlers import SMTPHandler
#        
#        mail_h = SMTPHandler(
#            mail_host   ,
#            mail_sender ,
#            mail_addrs  ,
#            mail_subject,
#            ( mail_user   , mail_pass   ),
#        )
#        mail_h.setLevel(mail_level)
#        mail_formatter = logging.Formatter(
#            "%(asctime)s\t%(name)s\t%(levelname)-8s %(message)s",
#            '%Y-%m-%d %H:%M:%S',
#        )
#        mail_h.setFormatter( mail_formatter )
#        logger.addHandler( mail_h )

    # return non - root logger ( e.g. name = "module.class" )
    return logging.getLogger(name) 


