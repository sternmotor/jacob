#!/usr/bin/env python
# -*- coding: utf-8 -*-
#vim:fdm=marker
# unlock vim folding via zR, zo and lock folding via zM, zc
#----------------------------------------------------------------------------
"""                                                                     
DESCRIPTION   shell script command line parsing preparation            {{{1

USAGE          call this script with -h or --help option
                see pt.templates/shellscript  for usage example
      
CHANGELOG    

TODO

THANKS TO

"""

__version__ = "$Revision: 0.1.2010-08-03 $"
# $Source$

__all__ = [
    'OptParserError',
    'OptParserOptionsError',
    'OptParserStandardError',
    'OptParserDaemonError',
    'OptParser',
]

#----------------------------------------------------------------------------
# modules import, constants                                              {{{1
#----------------------------------------------------------------------------
# standard
import sys
import os

# extra modules
from optparse import OptionParser, OptionGroup
 
# constants, default values

# logging
import logging
log = logging.getLogger( __name__ )

#----------------------------------------------------------------------------
# error class
#----------------------------------------------------------------------------
class OptParserError(Exception):
    """ Errors setting up options handler"""

class OptParserOptionsError(OptParserError):
    """General ptions Syntax Error"""

class OptParserStandardError(OptParserOptionsError):
    """Error handling standard options"""

class OptParserDaemonError(OptParserOptionsError):
    """Error handling daemon options"""

#----------------------------------------------------------------------------
# main optparser class
#----------------------------------------------------------------------------
class OptParser(OptionParser):
    def __init__(self, 
        usage=None, 
        description=None,
        standard_opts=True, 
        daemon_opts=False, 
    ):

        # input check
        if usage is None:
            raise OptParserError(
                "OptParser: define short usage hint!"
            )

        if description is None:
            raise OptParserError(
                "OptParser: define short description !"
            )
        else:
            # renice description
            nice_desc = '\n'.join(
                [ line.strip() for line in description.split('\n')]
            ).strip()

        # make display and handler options available class wide
        self.standard_opts = standard_opts
        self.daemon_opts = daemon_opts

        # init original option parser
        OptionParser.__init__(self,
            usage=usage, 
            description = nice_desc, 
            add_help_option = False    ,
        )

        # replace original parse_args by wrapper
        self.orig_parse_args = self.parse_args
        self.parse_args  = self.new_parse_args
        
    def create_option_group(self, title):
        return OptionGroup(self, title)


    #-------------------------------------------------------------------------
    # OPTION PARSER REPLACEMENT
    #-------------------------------------------------------------------------
    def new_parse_args( self, args=None, caller_log=None ):
        """
        Wrapper for parse_args, expanding option settings by standard options
        and analysing options string for those options (e.g.verbosity)
        """
        if args is None:
            log.debug( 
                "WARNING: No arguments array defined for new_parse_args!" 
            )
        if caller_log is None:
            log.debug( 
                "WARNING: No log file defined for new_parse_args!" 
            )

        if self.daemon_opts:
            self._define_daemon_options()

        if self.standard_opts:
            self._define_standard_options()

        opts, args = self.orig_parse_args(args)


        if self.standard_opts:
            self._handle_standard_opts( opts, args, caller_log )

        if self.daemon_opts:
            self._handle_daemon_opts(   opts, args, caller_log )

        # OptionParser instances have several cyclic references. You may wish 
        # to break the cyclic references explicitly by calling destroy() on 
        # your OptionParser once you are done with it.
        self.destroy()

        log.debug( "Options: %s" % opts )
        log.debug( "Arguments: %s" % args ) 
        return opts, args


    #-------------------------------------------------------------------------
    # STANDARD OPTIONS
    #-------------------------------------------------------------------------
    def _define_standard_options(self):
        standard_group = OptionGroup(self, 'Standard Options')
        standard_group.add_option('-h', '--help',
                        action='help',
                        help="Show this help message and exit")
        standard_group.add_option('-q', '--quiet', dest='quiet',
                        action='count', default=0,
                        help="-q show warnings and errors, -qq show errors only")
        standard_group.add_option('-v', '--verbose', dest="verbosity",
                        action='count', default = 0,
                        help="-v show info messages, -vv show debug messages")
        standard_group.add_option( '-V', '--version', dest="version",
                        action='store_true', default = False,
                        help='Show program\'s version number and exit')
        self.add_option_group(standard_group)


    def _handle_standard_opts(self, opts, args, log):

        # helperfunctions surpressing text printing
        def disableStdout():
            import sys
            sys.stdout = open(os.devnull, 'w')

        # print version
        if opts.version:
            import sys
            print sys.argv[0], __version__.split('$')[1].strip()
            sys.exit( 0 )

        # verbosity    
        if opts.quiet and opts.verbosity:
            self.print_help()
            raise OptParserStandardOptionsError(
                "Found Options -q and -v: refusing this brainfuck, sorry."
            )

        if log is None:
            # do not handle log verbosity in this case, stdout only
            if   opts.quiet > 0:
                    disableStdout()
        else:
            # handle log verbosity, too
            if   opts.quiet > 2:
                    log.setLevel(   logging.CRITICAL   )
                    disableStdout()
            elif opts.quiet == 2:
                    log.setLevel(   logging.ERROR      )
                    disableStdout()
            elif opts.quiet == 1:
                    log.setLevel(   logging.WARNING    )
                    disableStdout()
            elif opts.verbosity == 1:
                    log.setLevel(   logging.INFO       )
            elif opts.verbosity > 1:
                    log.setLevel(   logging.DEBUG      )
            else:
                    log.setLevel(   logging.WARNING    )


    #-------------------------------------------------------------------------
    # DAEMON OPTIONS
    #-------------------------------------------------------------------------
    def _define_daemon_options(self):
        daemon_group = OptionGroup(self, 'Daemon Options')
        daemon_group.add_option(
            '-D', '--daemon', dest="daemon_cmd",
            action='store', default = None,
            help="""Enable daemon (background) operation, commands: 
            start, stop, restart, reload, status, debug, zap
            """)
        daemon_group.add_option(
            '-N', '--daemon-name', dest="daemon_name",
            action='store', default = None,
            help='pid file name or path (optional)')
        daemon_group.add_option(
            '-L', '--daemon-log', dest="daemon_logf",
            action='store', default = None,
            help='log file to redirect stdout and stderr to (optional)')
        daemon_group.add_option(
            '-U', '--daemon-user', dest="daemon_user",
            action='store', default = None,
            help='user[:group] to run daemon as (optional)')

        self.add_option_group(daemon_group)


    def _handle_daemon_opts(self, opts, args, caller_log):

        # no daemon command given
        if opts.daemon_cmd is None:
            if ( opts.daemon_name is not None ) \
            or ( opts.daemon_logf is not None ) \
            or ( opts.daemon_user is not None ):
                raise OptParserDaemonError(
                    "Daemon options error: pid or log file defined but no "
                    "--daemon-cmd is given!"
                )
