#!/usr/bin/env python

"""asyncpipes.py: Asynchronous pipe communication using asyncore.

Extends file_dispatcher to provide extra functionality for reading from and
writing to pipes. Uses the observer pattern to provide notification of new
data and closed pipes.

References:
http://code.activestate.com/recipes/576962/ [observer.py]
http://parijatmishra.blogspot.com/2008/01/writing-server-with-pythons-asyncore.html
"""

import os
import sys

import asyncore
from errno import EPIPE, EBADF
from asyncore import file_dispatcher

from observer import Observable

if __name__ == '__main__':
    import optparse

__version__ = '$Revision: 0 $'.split()[1]

__usage__ = 'usage: %prog [options]'


class PipeDispatcher(Observable, file_dispatcher):
    """Generic class for dispatching pipe I/O using asyncore.

    Allows synchronous and asynchronous access to the pipe by delegating to
    the filehandle (though they should probably not be mixed).
    """
    # Event sent when the pipe is closed
    PIPE_CLOSED = 'closed'

    def __init__(self, fh, map=None, maxdata=512, ignore_broken_pipe=False):
        """Wrap a dispatcher around the passed filehandle.

        If the ignore_broken_pipe parameter is True, an OSError with errno
        of EPIPE or EBADF will call handle_close() instead of handle_expt().
        Useful in cases where broken pipes should be handled quietly."""
        self.maxdata = maxdata
        if ignore_broken_pipe:
            self.__ignore_errno = [EPIPE, EBADF]
        else:
            self.__ignore_errno = []
        self.__filehandle = fh
        file_dispatcher.__init__(self, os.dup(fh.fileno()), map=map)
        Observable.__init__(self)

    def __getattr__(self, attr):
        """Cheap delegation; check the filehandle and then the superclass"""
        if hasattr(self.__filehandle, attr):
            return getattr(self.__filehandle, attr)
        else:
            return file_dispatcher.__getattr__(self, attr)

    def close(self):
        """Closes the pipe and calls the _obs_notify() method."""
        if self.__filehandle:
            try:
                try:
                    file_dispatcher.close(self)
                except OSError, oe:
                    if oe.errno not in self.__ignore_errno:
                        traceback.print_exc(file=sys.stderr)
                try:
                    self.__filehandle.close()
                except OSError, oe:
                    if oe.errno not in self.__ignore_errno:
                        traceback.print_exc(file=sys.stderr)
            finally:
                self.__filehandle = None
                self._obs_notify(event=self.PIPE_CLOSED)

    def readable(self):
        """Returns true if the pipe is still open."""
        return (self.__filehandle is not None)

    def writable(self):
        """Returns true if the pipe is still open."""
        return (self.__filehandle is not None)

    def send(self, buffer):
        """Wrapper which checks for closed and broken pipes."""
        if self.__filehandle:
            try:
                return file_dispatcher.send(self, buffer)
            except OSError, oe:
                if oe.errno in self.__ignore_errno: self.handle_close()
                else: self.handle_expt()
        return 0

    def recv(self, buffer_size):
        """Wrapper which checks for closed and broken pipes."""
        if self.__filehandle:
            try:
                return file_dispatcher.recv(self, buffer_size)
            except OSError, oe:
                if oe.errno in self.__ignore_errno: self.handle_close()
                else: self.handle_expt()
        return ''

    def handle_close(self):
        """Calls self.close()"""
        self.close()

    def handle_expt(self):
        """Prints a traceback and calls handle_close() to close the pipe."""
        traceback.print_exc(file=sys.stderr)
        self.handle_close()


class InputPipeDispatcher(PipeDispatcher):
    """Push data to an input pipe using asyncore."""
    def __init__(self, fh, **keywmap):
        self.__buffer = None
        self.__offset = 0
        PipeDispatcher.__init__(self, fh, **keywmap)

    def readable(self):
        """Input pipes are never readable."""
        return False

    def writable(self):
        """If data is in the buffer and the pipe is open, return True."""
        return PipeDispatcher.writable(self) and (self.__buffer is not None)

    def handle_write(self):
        """Write up to maxdata bytes to the pipe."""
        if self.writable():
            self.__offset += self.send(
                    self.__buffer[self.__offset:self.__offset+self.maxdata])
            # If the buffer is all written, empty it.
            if self.__offset >= len(self.__buffer):
                self.__buffer = None
                self.__offset = 0

    def push_data(self, data):
        """Push some data by putting it in the write buffer. Raise EOFError
        if the pipe is already closed."""
        if not PipeDispatcher.writable(self):
            raise EOFError('Input pipe closed.')
        elif self.__buffer:
            # Since we have to construct a new string, remove the already-sent data.
            self.__buffer = self.__buffer[self.__offset:] + data
        else:
            self.__buffer = data
        self.__offset = 0


class OutputPipeDispatcher(PipeDispatcher):
    """Get data from an output pipe using asyncore."""
    # Event sent when new data is available in the pipe
    PIPE_DATA = 'data'

    def __init__(self, fh, universal_newlines=False, **keywmap):
        self._universal_newlines = universal_newlines
        self.__data = []
        self.__endedcr = False
        PipeDispatcher.__init__(self, fh, **keywmap)

    def writable(self):
        """Output pipes are never writable."""
        return False

    def handle_read(self):
        """Read up to maxdata bytes, queue the data, and call _obs_notify()"""
        if self.readable():
            data = self.recv(self.maxdata)
            if data:
                self.__data.append(data)
                self._obs_notify(self.PIPE_DATA)

    def _translate_newlines(self, data):
        data = data.replace("\r\n", "\n")
        data = data.replace("\r", "\n")
        return data

    def fetch_data(self, clear=False):
        """Return all the accumulated data from the pipe as a string,
        and optionally clear the accumulated data."""
        if self.__data:
            datastr = ''.join(self.__data)
            if clear:
                self.__data[:] = []
            if datastr and self._universal_newlines:
                # Take care of a newline split across cleared reads.
                stripnl = self.__endedcr
                if clear:
                    self.__endedcr = (datastr[-1] == '\r')
                if stripnl and datastr[0] == '\n':
                    return self._translate_newlines(datastr[1:])
                else:
                    return self._translate_newlines(datastr)
            else:
                return datastr
        else:
            return ''


if __name__ == '__main__':
    class TestAsyncPipe:
        """A test class that loops data through a pipe."""
        def __init__(self, maxprint,
                loops=5, maxwrite=1024, maxread=1024, lineterm='\n'):
            self._maxprint = maxprint
            self._lineterm = lineterm
            self._loops = loops
            rp, wp = os.pipe()
            self._inpipe = InputPipeDispatcher(os.fdopen(wp, 'wb'),
                    maxdata=maxwrite)
            self._outpipe = OutputPipeDispatcher(os.fdopen(rp, 'rb'),
                    maxdata=maxread, universal_newlines=(lineterm != '\n'))
            self._inpipe.obs_add(self)
            self._outpipe.obs_add(self)

        def _printdata(self, data):
            if not data:
                printable = ''
            elif len(data) > self._maxprint + 1:
                printable = ': ' + repr(data[:self._maxprint] + '...' + data[-1])
            else:
                printable = ': ' + repr(data)
            print '%d bytes received%s' % (len(data), printable)

        def handle_notify(self, pipe, event):
            if event == OutputPipeDispatcher.PIPE_DATA:
                data = pipe.fetch_data(clear=False)
                self._printdata(data)
                if data.endswith('\n'):
                    self._loops -= 1
                    if self._loops:
                        data = pipe.fetch_data(clear=True).strip()
                        self._inpipe.push_data(data + self._lineterm)
                    else:
                        self._inpipe.close()
                        self._outpipe.close()
            else:
                print '%s %s' % (str(pipe.__class__), event)


    optparser = optparse.OptionParser(usage=__usage__, version=__version__)
    optparser.disable_interspersed_args()
    optparser.add_option('--data', default='0123456789',
            help='Data string to be sent')
    optparser.add_option('--copies', type=int, metavar='N', default=1,
            help='Repeat the data N times (to test large transfers)')
    optparser.add_option('--maxread', type='int', metavar='BYTES', default=1024,
            help='Maximum data to read in each chunk')
    optparser.add_option('--maxwrite', type='int', metavar='BYTES', default=1024,
            help='Maximum data to write in each chunk')
    optparser.add_option('--loops', type='int', metavar='N', default=5,
            help='Number of loops to execute')
    optparser.add_option('--lineterm', type='choice', metavar='TERM',
            choices=['CR','CRLF','LF'], default='LF',
            help='Line terminator to send (CR, CRLF, or LF)')
    (options, args) = optparser.parse_args()
    # Return options as dictionary.
    optdict = lambda *args: dict([(k, getattr(options, k)) for k in args])

    # Translate the line terminator to an escape sequence.
    lineterm = {'CR':'\r', 'CRLF':'\r\n', 'LF':'\n'}[options.lineterm]
    pipe_handler = TestAsyncPipe(len(options.data), lineterm=lineterm,
            **optdict('loops','maxwrite','maxread'))
    pipe_handler._inpipe.push_data(options.data * options.copies + lineterm)
    asyncore.loop()

