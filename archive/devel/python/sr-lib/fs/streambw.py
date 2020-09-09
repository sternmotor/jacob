#! /usr/bin/env python
import sys
import time

import  pt.terminal



while 1:
    #data = sys.stdin.read(256)
    data = sys.stdin.read(4)
    if data != '':
        sep= open("s").read()
        # do some processing of the contents of
        # the data variable
        data = sep+data
        # end of data processing command group
        sys.stdout.write(data)
        time.sleep(0.1)

    else:
        sys.stdout.flush()
        break
