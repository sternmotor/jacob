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

# module export
__all__ = [
    'NumbersError',
    'renice',
]


import re
from pt.data.validate import is_float, VdtTypeError


class NumbersError(BaseException):
    """ Errors in numbers handling """



_re_digits_nondigits = re.compile(r'\d+|\D+')

def renice( format, number, separator="'"):
    """
    Add thousands separator to numbers, apply printf format string
    Input:  * value
            * max_digits: number of digits
    Returns: string 
    """
    
    try:
        value = is_float(number)
    except VdtTypeError:
        raise NumbersError(
            "Number '%s' handed over to renice() is no integer or "
            "float number !" % number
        )


    try:
        parts = _re_digits_nondigits.findall(format % (value,))
    except TypeError, emsg:
        raise NumbersError(
            "Error renicing numbers: some parameters in renice() call "
            "are not what it is expected at this place, see \n%s" 
            % renice.__doc__
        )
    for i in xrange(len(parts)):
        s = parts[i]
        if s.isdigit():
            parts[i] = _commafy(s, separator)
            break
    return ''.join(parts)
    
def _commafy(s, separator):

    r = []
    for i, c in enumerate(reversed(s)):
        if i and (not (i % 3)):
            r.insert(0, separator)
        r.insert(0, c)
    return ''.join(r)

if __name__ == "__main__":
    print renice( '%.4f', "40000.300000000")
