#!/usr/bin/env python
# see http://eli.thegreenplace.net/2010/06/25/aes-encryption-of-files-in-python-with-pycrypto/
   
__all__=[ 'decrypt_string', 'encrypt_string' ]

from   Crypto.Cipher import AES
import hashlib
import random
import struct
import math

DEFAULT_MODE = AES.MODE_CBC
CHUNK_SIZE   = 64
IV_SIZE      = 16


#------------------------------------------------------------------------------
# main functions
#------------------------------------------------------------------------------


def _adjustPasswordLength( text ):
    """
    adjust key length otherwise AES complains
    return string which is ok
    """
    return hashlib.sha256(text).digest()

def encrypt_string( string, password, mode=DEFAULT_MODE, chunk_size=CHUNK_SIZE, iv_size=IV_SIZE ):

    iv = ''.join(chr(random.randint(0, 0xFF)) for i in range(iv_size))
    key = _adjustPasswordLength(password)
    encryptor = AES.new(key, mode, iv)

    # iv and original string length need to be stored in output string.
    # string length needs to be paddes to be be divisible by 16 so 
    # original string length is important

    length_struct = struct.pack('<Q', len(string))
    enc = length_struct + iv

    # v = value to split, l = size of each chunk
    f = lambda v, l: [v[i*l:(i+1)*l] for i in range(int(math.ceil(len(v)/float(l))))]
    chunks = f( string, chunk_size)

    for chunk in chunks:
        if len(chunk) % chunk_size != 0:
            chunk += ' ' * (chunk_size - len(chunk) % chunk_size)
        enc += encryptor.encrypt( chunk )
    
    return enc


def decrypt_string( string, password, mode=DEFAULT_MODE, chunk_size=CHUNK_SIZE, iv_size=IV_SIZE ):
    """ cursor 0, 1 = slice of string currently processed"""
    key = _adjustPasswordLength(password)

    cursor_0 = 0
    cursor_1 = struct.calcsize('Q')
    orig_size = struct.unpack('<Q', string[cursor_0:cursor_1] )[0]

    cursor_0 = cursor_1
    cursor_1 = cursor_0 + iv_size
    iv = string[cursor_0:cursor_1]

    decryptor = AES.new(key, mode, iv)
    plain = ''

    while True:
        cursor_0 = cursor_1
        cursor_1 = cursor_0 + chunk_size
        chunk = string[cursor_0:cursor_1]
        if len(chunk) == 0:
            break
        plain += decryptor.decrypt(chunk)

    return plain[:orig_size]


#------------------------------------------------------------------------------
# test structure
#------------------------------------------------------------------------------
if __name__ == "__main__":

    import sys
    from pt.terminal import *
#    from pt.crypt import *


    password = '012678cdef   eofdeof  w edwe dedw dw e dw'

    text="gal wedeiwf                   erfref"
    print text

    enc= encrypt_string( text, password )
    print enc

    print decrypt_string( enc, password )
