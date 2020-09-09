#!/usr/bin/env python
# -*- coding: utf-8 -*-
#vim:fdm=marker
# unlock vim folding via zR, zo and lock folding via zM, zc
#----------------------------------------------------------------------------
"""                                                                     
DESCRIPTION    iptables netmap                        {{{1

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
    'Module',
]

# standard
import logging
log = logging.getLogger( __name__ )


# extra modules
from pt.net.iptables import *

#----------------------------------------------------------------------------
# error classes                                                          {{{1
#----------------------------------------------------------------------------
class Error(BaseException):
    """Base class for module errors"""
class NetmapError(Error):
    """Some Error"""

#----------------------------------------------------------------------------
# main class                                                             {{{1
#----------------------------------------------------------------------------

class Netmap():
    """
    source: network where traffic originates from
    fake_nw : 10.KD.xx.xx
    real_nw: 192.168.xx.xx
    """
    def __init__(self, fake_nw, real_nw, source_nw=None ):

        self.source = source_nw and source_nw or '0.0.0.0'
        self.real   = real_nw
        self.fake   = fake_nw
        self.description = (
            "incoming from '%s' to '%s' as '%s'"
            % ( self.source,self.real, self.fake )
        )

    def setup( self ):
        """Set up netmap"""

        if self.is_present():
            log.debug( "Netmap filter is present, already")
            return True

        log.info( "Mapping traffic %s" % self.description )
        args = ( 
            "-t nat -A PREROUTING "
            "--src %s "
            "--dst %s "
            "--jump NETMAP --to %s "
            % ( self.source, self.real, self.fake, )
        )
        for line in iptables( args ):
            pass

        # check for success
        if not self.is_present():
            raise NetmapError( "Tried to install netmap rule, no success")

    def remove(self):
        """Remove netmask setting"""
        if not self.is_present():
            log.debug( "Netmap filter is not present, doing nothing")
            return True

        # remove: work trough netmap entries in reverse order 
        chains = []
        for line in self.list_nat_table():
            netmap_data = self.is_my_netmap(line)
            if netmap_data:
                chains.append( netmap_data['chain'] )

        chains.reverse()
        for chain in chains:
            log.info( "Removing chain %s from NAT PREROUTING table" % chain )
            for out in iptables( " -t nat -D PREROUTING %s " % chain):
                pass

        # verify
        if self.is_present():
            raise NetmapError( "Netmap filter is still present, sorry")

    def is_present(self):
        """ Check if netmap entry exist, already """

        for line in self.list_nat_table():
            if self.is_my_netmap( line ):
                return True
        else:
            return False

    def is_my_netmap(self, line ):
        """ see if line from iptables table is netmap matching instance"""
        try:
            if line.split()[1] == 'NETMAP':
                log.debug( "Found netmap rule '%s'" % line )
                return{
                    'chain'  : line.split()[0], 
                    'source' : line.split()[4], 
                    'dest'   : line.split()[5], 
                    'fake'   : line.split()[6],
                }
            else:
                return False
        except IndexError:
            return False

    def list_nat_table(self):
        for line in iptables( "--line-numbers -L -n -t nat" ):
            yield line

#----------------------------------------------------------------------------
# tests and example invocation                                           {{{1
#----------------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    import os
    import pt.terminal # flush buffers, colors, terminal size
    import pt.logger   # set up logger

    # initialize logger
    log = pt.logger.Logger(
#        style = "plain",
        name         = None, # __name__ or self.__class__.__name__ 
        level        = logging.INFO,  
        file_file    = None,      # None = no file logging
        file_level   = logging.DEBUG,         
    )

    FAKE_NETWORKS = [
        '10.10.1.0/24',
        '10.10.2.0/24',
        '10.10.3.0/24',
    ]

    REAL_NETWORKS= [
        '192.168.1.0/24',
        '192.168.2.0/24',
        '192.168.3.0/24',
    ]

    BB_NW= "172.21.0.0/16"


    n=Netmap( FAKE_NETWORKS[1], REAL_NETWORKS[0], source_nw=BB_NW )
    n.setup()
    n.remove()
