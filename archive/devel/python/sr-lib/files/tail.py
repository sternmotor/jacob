#!/usr/bin/env python


import sys
import os

def tail(filepath, nol=10, read_size=1024):
  """
  This function returns the last "nol" lines of a file.
  Args:
    filepath: path to file
    nol: number of lines to print
    read_size:  data is read in chunks of this size (optional, default=1024)
  Raises:
    IOError if file cannot be processed.
  """
  f = open(filepath, 'rU')    # U is to open it with Universal newline support
  offset = read_size
  f.seek(0, 2)
  file_size = f.tell()
  while 1:
    if file_size < offset:
      offset = file_size
    f.seek(-1*offset, 2)
    read_str = f.read(offset)
    # Remove newline at the end
    if read_str[offset - 1] == '\n':
      read_str = read_str[:-1]
    lines = read_str.split('\n')
    if len(lines) >= nol:  # Got nol lines
      return "\n".join(lines[-nol:])
    if offset == file_size:   # Reached the beginning
      return read_str
    offset += read_size
  f.close()


