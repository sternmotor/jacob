#!/usr/bin/env python
# -*- coding: utf-8 -*-
#vim:fdm=marker
# unlock vim folding via zR, zo and lock folding via zM, zc
#----------------------------------------------------------------------------
"""                                                                     
DESCRIPTION    handle number printing                                      {{{1
"""

__version__ = "$Revision: 0.1.2010-10-07 $"
# $Source$


#----------------------------------------------------------------------------
# modules import, constants                                              {{{1
#----------------------------------------------------------------------------

import array

# module export
__all__ = [
    'uniq',
    'text2list',
]

def uniq( list ):
    """
    Return unified list (where doublettes are removed)
    """
    set = {}
    map(set.__setitem__, list, [])
    return set.keys()

def text2list(text):
    """Convert a text to array of lines, strip it but leave white lines"""
    def strip_line(line):
        if line.strip == '':
            return line
        else:
            return line.strip()

    return map( strip_line, text.splitlines() )


    



if __name__ == "__main__":
    print uniq( ["1","2","3","3"])
#    print renice( '%.4f', "40000.300000000")

    text="""\
    sfsdfds
    sfdsfsffsf
  
    sfweferrfrfefre
    """
    print text
    print text2list(text)
