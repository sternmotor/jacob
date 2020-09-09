#!/usr/bin/env python
# -*- coding: utf-8 -*-
#vim:fdm=marker
# unlock vim folding via zR, zo and lock folding via zM, zc
#----------------------------------------------------------------------------
"""                                                                     
 DESCRIPTION  simple bandwith limiter for single tcp connection           {{{1
 
 USAGE        call this script with -h or --help option
       
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
import socket
import asyncore
import time

# extra modules
from fly.validate.validate import is_integer, is_float, is_ip_addr, VdtTypeError 



# constants, default values
DEFAULT_BLOCK_SIZE = 4096

#----------------------------------------------------------------------------
# main classes                                                           {{{1
#----------------------------------------------------------------------------
class TcpForwardError(Exception):
    pass

class BwLimitError(Exception):
    pass

class TcpForward(asyncore.dispatcher):
    """
    ip, port                * listen here, must be local address
    remoteip, remoteport    * address to forward data to
    push_bw, pull_bw        * max. bandwidth (kByte / sec) for send/recv
    block_size               * block_size for send/recv, default is 4096 (bytes)
    """
    def __init__( self,
        ip, port, 
        remoteip,remoteport,
        push_bw = 10,pull_bw = None,
        block_size = DEFAULT_BLOCK_SIZE,
        backlog=5,
    ):

        asyncore.dispatcher.__init__(self)
        self.remoteip   = is_ip_addr( remoteip )
        self.remoteport = is_integer( remoteport )
        self.create_socket(socket.AF_INET,socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind( ( is_ip_addr( ip ) , is_integer( port ) ) )
        self.listen( is_integer( backlog ) )
        self.block_size = is_integer( block_size )
        log.debug(
            "Forwarding %s:%s => %s:%s"
            % (ip, port, remoteip, remoteport )
        )


        # calculate bandwidth limits in block sizes
        self.push_max_blocks, self.push_delay  \
            = self._calc_block_count_delay( push_bw ) 
        self.pull_max_blocks, self.pull_delay  \
            = self._calc_block_count_delay( pull_bw ) 
        log.debug(
            "Limiting bandwidth for push: %ikB/%0.2fs and pull: %ikB/%0.2fs "
            % ( 
                self.push_max_blocks * self.block_size / 1024, 
                self.push_delay,
                self.pull_max_blocks * self.block_size / 1024,
                self.pull_delay,
            )
        )
        log.debug(
            "This is pushing %s chunks of block size %s kB "
            "and pulling %s chunks of block size %s kB" 
            % ( 
                self.push_max_blocks, self.block_size / 1024,
                self.pull_max_blocks,self.block_size / 1024,
            )
        )

    def handle_accept(self):
        conn, addr = self.accept()
        log.debug( "Connect" )
        sender(
            receiver(
                conn, 
                self.block_size, 
                self.push_max_blocks, 
                self.push_delay,  
            ),
            self.remoteip,
            self.remoteport,
        )

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
class receiver(asyncore.dispatcher):
#----------------------------------------------------------------------------
    def __init__(self, conn, block_size, max_blocks, delay):
        asyncore.dispatcher.__init__(self,conn)
        self.from_remote_buffer = ''
        self.to_remote_buffer   = ''
        self.sender     = None
        self.block_count_recv  = 0
        self.block_size = block_size
        self.max_blocks = max_blocks
        self.delay      = delay
        self.last_time  = time.time()

    def handle_connect(self):
        pass

    def handle_read(self):
        read = self.recv(self.block_size)
        self.block_count_recv += 1
        now = time.time()
        # now - self.last_time is transport and other delay
        delay = self.delay - ( now - self.last_time  ) 
            

        if self.block_count_recv == self.max_blocks or delay < 0:
            log.debug( 
                'sleep %0.8fs after %s blocks' 
                % ( delay, self.block_count_recv ) 
            )
            try: 
                time.sleep( delay )
            except IOError, emsg:
                # negative number for delay, out of time
                pass
            # reset counters
            self.last_time = time.time()
            self.block_count_recv = 0

        self.from_remote_buffer += read

    def writable(self):
        return (len(self.to_remote_buffer) > 0)

    def handle_write(self):
        sent = self.send(self.to_remote_buffer)
        #log.debug( 'RECEIVER WRITE %04i <--' % sent )
        self.to_remote_buffer = self.to_remote_buffer[sent:]

    def handle_close(self):
        self.close()
        if self.sender:
            self.sender.close()

#----------------------------------------------------------------------------
class sender(asyncore.dispatcher):
#----------------------------------------------------------------------------
    def __init__(self, receiver, remoteaddr,remoteport):
        asyncore.dispatcher.__init__(self)
        self.receiver=receiver
        receiver.sender=self
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((remoteaddr, remoteport))

        self.block_count_sent = 0

    def handle_connect(self):
        pass

    def handle_read(self):
        read = self.recv(1024)
        self.block_count_sent += 1
#        log.debug( 
#            "SENDER read handler <-- %04i, total : %i" % (len(read), self.block_count_sent ) 
#        )
        self.receiver.to_remote_buffer += read

    def writable(self):
        return (len(self.receiver.from_remote_buffer) > 0)

    def handle_write(self):
        sent = self.send(self.receiver.from_remote_buffer)
        #log.debug( 'SENDER sent handler --> %04i' % sent )
        self.receiver.from_remote_buffer = self.receiver.from_remote_buffer[sent:]

    def handle_close(self):
        self.close()
        self.receiver.close()


    #------------------------------------------------------------------------
    #                                                                    {{{2   
    #------------------------------------------------------------------------
 
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
        '-l','--local-ip',
        dest='local_ip',default='127.0.0.1',
        help='Local IP address to bind to')
    parser.add_option(
        '-p','--local-port',
        type='int',dest='local_port',default=8082,
        help='Local port to bind to')
    parser.add_option(
        '-r','--remote-ip',dest='remote_ip',default='10.98.117.6',
        help='Remote IP address to connect to')
    parser.add_option(
        '-P','--remote-port',
        type='int',dest='remote_port',default=22,
        help='Remote port to bind to')
    options, args = parser.parse_args()

    TcpForward(options.local_ip,options.local_port,options.remote_ip,options.remote_port, 100000, 1000)
    asyncore.loop()


    sys.exit(0)

