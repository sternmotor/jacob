#!/usr/bin/env python
# -*- coding: utf-8 -*-

from config import *

#----------------------------------------------------------------------------
# test structure
#----------------------------------------------------------------------------

if __name__ == "__main__":
    import sys


    try:
        config = ConfigFile( "test.conf", create_empty = True )
    except ConfigError, emsg:
        print emsg
        sys.exit(1)

    config['Hallo4'] = {}
    config['Hallo4']['mick1'] = 'jjj'
    config['Hallo4']['mick2'] = 'yes'
    config['Hallo4']['mick7'] = [ 'hhhh', 'jjjj', 'hallo', ]
   
#    config.purgVe()
    print config
    config.write()

    # keine Ahnung:
    print config['Hallo4']['mick2']
    print config['Hallo4'].keys()
#    print config['Hallo4'].as_bool(['mick2'])
