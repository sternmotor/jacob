#!/usr/bin/env python
# -*- coding: utf-8 -*-
#vim:fdm=marker
# unlock vim folding via zR, zo and lock folding via zM, zc
#----------------------------------------------------------------------------
"""                                                                     
DESCRIPTION    units constants                                      {{{1
"""

__version__ = "$Revision: 0.1.2010-10-07 $"
# $Source$


#----------------------------------------------------------------------------
# modules import, constants                                              {{{1
#----------------------------------------------------------------------------

# module export
__all__ = [
    'UnitError',
    'FACTORS1000',
    'FACTORS1024',
    'isValidUnit',
]


class UnitError(BaseException):
    """ Errors in unit handling """

FACTORS1000 = {
    'k'  : 1000,
    'M'  : 1000 * 1000,
    'G'  : 1000 * 1000 * 1000,
    'T'  : 1000 * 1000 * 1000 * 1000,
    'P'  : 1000 * 1000 * 1000 * 1000 * 1000,
    'E'  : 1000 * 1000 * 1000 * 1000 * 1000 * 1000,
}


FACTORS1024 = {
    'Ki' : 1024,
    'Mi' : 1024 * 1024,
    'Gi' : 1024 * 1024 * 1024,
    'Ti' : 1024 * 1024 * 1024 * 1024,
    'Pi' : 1024 * 1024 * 1024 * 1024 * 1024,
    'Ei' : 1024 * 1024 * 1024 * 1024 * 1024 * 1024,
}


def isValidUnit( unit ):
    """Test if given unit is valid"""

    if not unit in FACTOR1000.keys() and not unit in FACTORS1024.keys():
        raise UnitError(
            "Given unit is not one of "
            % ( ','.join( FACTORS1000.keys() + FACTORS1024.keys() ) )
        )
