#!/usr/bin/env python
# -*- coding: utf-8 -*-
#vim:fdm=marker
# unlock vim folding via zR, zo and lock folding via zM, zc
#----------------------------------------------------------------------------
"""                                                                     
 DESCRaddrTION  simple bandwith limiter for single tcp connection           {{{1
 
 USAGE        call this scraddrt with -h or --help option
       
 CHANGELOG    
    09-06-23    * creation, copied from

 TODO
 
 THANKS TO

"""

__version__ = "$Revision: 0.1.2010-05-04 $"
# $Source$




 
#----------------------------------------------------------------------------
# modules import, constants                                              {{{1
#----------------------------------------------------------------------------
# standard
import time

# extra modules
from fly.validate.validate import is_integer, is_float, VdtTypeError 

# optimal delay between chunks ( 0.2 secs  is a good compromise allowing nice
# flow and minimum management effort)
OPTIMAL_DELAY = 0.2
BLOCK_SIZE    = 4


class TcpForward:
    """
    addr, port                * listen here, must be loc address
    remaddr, remport    * address to forward data to
    push_bw, pull_bw        * max. bandwidth (kByte / sec) for send/recv
    block_size               * block_size for send/recv, default is 4096 (bytes)
    """
    def __init__( self,
        loc_addr, loc_port, 
        rem_addr,rem_port,
        bw_up = 12,bw_down = 20,
        block_size = BLOCK_SIZE,
        opti_delay = OPTIMAL_DELAY,
        backlog=5,
    ):

        log.debug(
            "Forwarding %s:%s => %s:%s"
            % (loc_addr, loc_port, rem_addr, rem_port )
        )

        # block size in byte
        self.block_size = is_integer( block_size )
        # bw in byte / sec
        bw_up   = is_float( bw_up   ) 
        bw_down = is_float( bw_down ) 

        bw = bw_up
        bs = block_size
        od = opti_delay
        
        """
        Traffic consists of single blocks of block size. Bandwidth limiting
        means putting some delay between this blocks. By grouping a number of
        blocks to chunks and putting delay in between this chunks, traffic
        gets into nice flow (multiple delays) but is limited in bandwidth.

        The number of blocks per chunk and the delay between chunks is 
        calculated here.

        Input
         bw = max bandwidth (kbyte/sec)
         bs = blocksize (kbyte)
         od = optimal delay between chunks

        Output
         tuple: (
            bpc # blocks per chunk,
            dbc # delay between chunks,
         )
        """


        if bw is not None:
            if bw < bs:
                raise BwLimitError(
                    "Bandwidth limit '%s kbyte/s' is smaller than block_size '%s kbyte' "
                    % ( bw, bs )
                )
            else:
#                # calc delay between blocks so accuracy is high even when 
#                # all block_size do not fit into one second
#                max_blocks  = int( max_bw_bytes / self.block_size )
#                delay = ( 1 / max_bw_bytes ) * max_blocks * self.block_size
#                # now after max_blocks are transfered wait delay seconds
#                return ( is_integer( max_blocks ), is_float( delay)  )

                # how much blocks can be transferred per second    
                bps = int( bw / bs )
                log.debug( "bandwidth: %s kbyte/s, block size %s kbyte" % ( bw, bs ) )
                # full delay per second
                dps = 1 - ( 1 / bw ) * bps * bs  
                log.debug( "blocks per second: %s, delay per second %0.6f s" % (bps, dps) )
                # chunks per second so optimum delay is reached, round up
                try:
                    cps = int( dps / od + 0.5 ) 
                except ZeroDivisionError:
                    cps = bps
                # blocks/ delay per chunk
                bpc = bps / cps
                dpc = dps / cps
                log.debug( 
                    "chunks per second: %d, blocks per chunk: %d, delay per chunk: %0.6f"
                    % ( cps, bpc, dpc )
                )
                
        else:
            # no limit
            pass


#        # calculate bandwidth limits in block sizes
#        self.push_max_blocks, self.push_delay  \
#            = self._calc_block_count_delay( push_bw ) 
#        self.pull_max_blocks, self.pull_delay  \
#            = self._calc_block_count_delay( pull_bw ) 
#        log.debug(
#            "Limiting bandwidth for push: %ikB/%0.2fs and pull: %ikB/%0.2fs "
#            % ( 
#                self.push_max_blocks * self.block_size / 1024, 
#                self.push_delay,
#                self.pull_max_blocks * self.block_size / 1024,
#                self.pull_delay,
#            )
#        )
#        log.debug(
#            "This is pushing %s chunks of block size %s kB "
#            "and pulling %s chunks of block size %s kB" 
#            % ( 
#                self.push_max_blocks, self.block_size / 1024,
#                self.pull_max_blocks,self.block_size / 1024,
#            )
#        )

    def _calc_block_count_delay( self, max_bw ):
        """
        Return block count for given max bandwidth and block size
        """
        if max_bw is not None:
            max_bw_bytes = is_float( max_bw ) * 1024
            if max_bw_bytes < self.block_size:
                raise BwLimitError(
                    "Bandwidth limit '%s kB/s' is smaller than block_size '%s B' "
                    % ( max_bw, self.block_size )
                )
            else:
                # calc delay between blocks so accuracy is high even when 
                # all block_size do not fit into one second
                max_blocks  = int( max_bw_bytes / self.block_size )
                delay = ( 1 / max_bw_bytes ) * max_blocks * self.block_size
                # now after max_blocks are transfered wait delay seconds
                return ( is_integer( max_blocks ), is_float( delay)  )
        else:
            # no limit
            return(0, 0)


#----------------------------------------------------------------------------
# test structure                                                         {{{1
#----------------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    import os
    import logging
    import optparse

    log = logging.getLogger('fly.net.bwlimit')
    log.addHandler(logging.StreamHandler())
    log.setLevel(logging.DEBUG)

    parser = optparse.OptionParser()

    parser.add_option(
        '-l','--loc-addr',
        dest='loc_addr',default='127.0.0.1',
        help='loc addr address to bind to')
    parser.add_option(
        '-p','--loc-port',
        type='int',dest='loc_port',default=8082,
        help='loc port to bind to')
    parser.add_option(
        '-r','--rem-addr',dest='rem_addr',default='10.98.117.6',
        help='rem addr address to connect to')
    parser.add_option(
        '-P','--rem-port',
        type='int',dest='rem_port',default=22,
        help='rem port to bind to')
    options, args = parser.parse_args()

    TcpForward(options.loc_addr,options.loc_port,options.rem_addr,options.rem_port, 19.9, 60)


    sys.exit(0)

