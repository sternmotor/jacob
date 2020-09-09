#!/usr/bin/env python3
"""simple error class"""


# objects exported from this module file
__all__ = (
    'KnownError',
)

class KnownError(BaseException):
    """Well known error condition leading to regular script error exit (no exception)"""
    pass

