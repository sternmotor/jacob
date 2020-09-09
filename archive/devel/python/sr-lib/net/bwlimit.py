#!/usr/bin/env python

import sys
import os
import time
import pt.proc.mem
from datetime import datetime, timedelta
from pt.data import validate



class BwLimitError(BaseException):
    """Error calculating delay between sending data loops"""
class BwLimitEOF(BaseException):
    """End of data reached"""

class BwLimit:
    """
    General bandwith limit handler menat to be subclassed
    for usage in pipes and socket handlers.
    Time units: microseconds, size units: bytes

    METHODS
    init
    start()         # start bandwith limit, calculate optimum parameters
    tune(max_bw)    # 


    PARAMETERS
    check_intervall * seconds between re-adjustments of pipe parameters
                      default: 600 = 10 min
    bs_start * start block size 
    bw_max: target bandwith byte/s, 0 = unlimited
    """

    BS_START = 1 * 1024    # start optimisation with 1k blocks
    BS_MAX   = 4 * 1024    # 4k block limit
    CHECK_INTERVAL = 2   # readjust bwlimit parameters every e.g. 600s = 10 minutes
    NICE_DELAY = 0.2 * 1000 * 1000 # nice delay between blocks
   
    def __init__(self, 
        check_interval=CHECK_INTERVAL, 
        bs_start= BS_START, 
        bs_max  = BS_MAX, 
        bw_max  = None , 
        *args, **kwargs):

        # store check_intervall in us
        self.check_interval = validate.is_integer( check_interval, 1 )

        # check block size to start with ( in bytes)
        bs_start = validate.is_integer( int( bs_start + 0.5) , 1024 ) 

    
        # maximum block size
        #if bs_max:
        self.bs_max = validate.is_integer( int( bs_max + 0.5) , 1024  )
        #else:
        #    free_mem = pt.proc.mem.get_info()['MemTotalFree']
        #    bs_max = int( free_mem / 10 + 0.5)

        # max bandwidth
        try:
            self.bw_max = validate.is_integer( int( bw_max + 0.5) , 1024  )
        except TypeError:
            raise BwLimitError("bw_max is not defined, try harder!")

        # configure transfer start
        self.bs = bs_start  # block size
        self.cs = 10         # chunk size ( number of blocks)
        self.delay = None   # delay between loops (usec)

        # array for storing block transfer times (for weighted median calc
        self.block_times = []


    def start(self):
        """
        1. transfer max_loops
        2. sleep delay
        repeat 1,2 until check_interval is reached
        recalculate transfer parameters
        repeat 1,2 ... until BwLimitEOF is reached
        """
       
        start_time = datetime.now()
        self.loops = 0     # number of transmitted loops
        while True:
            # transfer chunk and sleep 
            self.loops += 1
            try:
                self.transfer_chunk()
            except BwLimitEOF:
                # finished
                return True
            try:
                time.sleep(self.delay)
            except TypeError:
                # first run, calculate all parameters
                self.elapsed = datetime.now() - start_time
                self.readjust()
                start_time = datetime.now()
                self.loops = 0
                continue

            self.elapsed = datetime.now() - start_time
            if self.elapsed >= timedelta(seconds = self.check_interval):

                self.readjust()
                start_time = datetime.now()
                self.loops = 0
            else:
                # next chunk + sleep
                continue
            
    def readjust(self):
        """
        Calculate chunk size, block size and delay for next 
        interval
        """

        last_loops_time = self.elapsed.microseconds
        try:
            last_chunk_time = ( last_loops_time / self.loops ) - self.delay
        except TypeError:
            # first run, self. delay is not defined
            last_chunk_time = ( last_loops_time / self.loops )

        last_block_time = last_chunk_time / self.cs

#        medium_block_time = self.get_medium_block_time( last_block_time )


        # calculate cs, bs and delay for smooth operation
        # time needed to transport "bandwith" data
        total_time = self.bw_max / self.bs * last_block_time
        total_delay = 1000 * 1000 - total_time

        new_loops = int( total_delay / self.NICE_DELAY + 0.5 )
        self.delay = total_delay / new_loops / 1000.0 / 1000.0

        self.bs = min( self.bs_max, self.bw_max/ new_loops) # handle huge bs_max values
        self.cs = self.bw_max / new_loops / self.bs

        #sys.stderr.write("bs %s  block_time %s total_time %s\n" % (self.bs, last_block_time, medium_block_time))

    def get_medium_block_time(self, current_block_time):
        """store current block time in array, calculate weighted median of last 5 values"""

        self.block_times.append( current_block_time )

        if   len( self.block_times ) > 5:
            del self.block_times[0]

        bts = self.block_times
        if   len( bts ) == 5:
            return ( 1*bts[0] + 3*bts[1] + 2*bts[2] + 2*bts[3] + 3*bts[4]) / 10
        elif len( bts ) == 4:
            return ( 1*bts[0] + 2*bts[1] + 2*bts[2] + 3*bts[3] ) / 8
        elif len( bts ) == 3:
            return ( 1*bts[0] + 2*bts[1] + 3*bts[2] ) / 6
        elif len( bts ) == 2:
            return ( 1*bts[0] + 1*bts[1] ) / 2
        elif len( bts ) == 1:
            return current_block_time


     
    def transfer_chunk( self):
        """
        Transfer one chunk ( some blocks) of data and return. This is the atomic part
        of bandwith control which is user-defined.
        * raise BwLimitEOF in case there is no more data.
        * return True in case everything's ok
        * raise NotImplemented if this method is not overwritten by some child class

        * parameters which should be used here: self.bs, self.cs
        """

        raise NotImplementedError(
            "This method should be overwritten in a subclass! Method description:"
            "\n%s" % self.transfer_chunk.__doc__
        )



class PipeBwLimit(BwLimit):
    PIPE_BS_MAX   = 64 * 1024     # kernel limit for pipes, see http://home.gna.org/pysfst/tests/pipe-limit.html
    PIPE_BS_START = 4  * 1024    # start optimisation with 4k blocks
    def __init__(self, bs_max=PIPE_BS_MAX, bs_start=PIPE_BS_START, *args, **kwargs):

        BwLimit.__init__(self,bs_max=bs_max, bs_start=bs_start, *args, **kwargs)

        # Make sys.stdin binary
        sys.stdin = os.fdopen(sys.stdin.fileno(), 'rb', 0) 


    def transfer_chunk( self ):
        """ Forward piped data, onw chunk of blocks"""

        counter = 0
        bytes_in = True
        while counter < self.cs and bytes_in:
            counter +=1
            bytes_in = sys.stdin.read( self.bs )
            sys.stdout.write( bytes_in )
        if not bytes_in:
            raise BwLimitEOF("No more data!")



if __name__ == '__main__':
    pbwl = PipeBwLimit(bw_max = 1024*1024*10)
    pbwl.start()


    # test like time { rm test; cat 100MB_FILE | bwl > test; ll test; }
