#!/usr/bin/env python
# -*- coding: utf-8 -*-
#vim:fdm=marker
# unlock vim folding via zR, zo and lock folding via zM, zc
#----------------------------------------------------------------------------
"""                                                                     
 DESCRIPTION  socket server class adaption
 
       
 CHANGELOG    
    10-08-25 * rework: logging implemented
    10-01-13 * copied from "http://danieldandrada.blogspot.com/2007/09/
               python-socketserverthreadingtcpserver.html"

 TODO
 
 THANKS TO
        Daniel d'Andrada T. de Carvalho Location: Helsinki, Finland 


asyncore.dispatcher()
 * writable is called by the asyncore framework to check if the dispatcher 
   has data to send. The default implementation always returns True.
 * readable is called to check if the dispatcher is ready to process incoming
   data, if any. The default implementation always returns True.
 * handle_connect is called when a connection is successfully established.
 * handle_expt is called when a connection fails (Windows), or 
   when out-of-band data arrives (Unix).
 * handle_accept is called when a connection request is made to a listening 
   socket. The callback should call the accept method to get the client 
   socket. In most cases, the callback should create another socket handler 
   to handle the actual communication.
 * handle_read is called when there is data waiting to be read from the 
   socket. The callback should call the recv method to get the data.
 * handle_write is called when data can be written to the socket. Use the 
   send method to write data.
 * handle_close is called when the socket is closed or reset.
 * handle_error(type, value, traceback) is called if a Python error occurs 
   in any of the other callbacks. The default implementation prints an 
   abbreviated traceback to sys.stdout.
"""

__version__ = "$Revision: 0.2.2010-02-12 $"
# $Source$


#----------------------------------------------------------------------------
# modules import, constants                                              {{{1
#----------------------------------------------------------------------------

# module export
__all__ = [
    'TcpServer',
    'Error',
    'AcceptError',
    'UserHandlerError',
    'ListenError',
    'Close',
]

# standard
import socket
import asyncore
import asynchat
#import traceback
import logging
log = logging.getLogger( __name__ )

# extra modules

# constants
EOL = '\n\r'
EOF = "bye"
DEFAULT_PORT = 5000
DEFAULT_ADDR = "0.0.0.0"
ALLOW_REUSE_ADDR   = True
REQUEST_QUEUE_SIZE = 5
MAX_CONN     = 100
TIMEOUT      = 10 # seconds

#----------------------------------------------------------------------------
# error classes                                                          {{{1
#----------------------------------------------------------------------------
class Error(BaseException):
    """Base class for TcpServer errors"""
class AcceptError(Error):
    """Error accepting connections"""
class ConnectionError(Error):
    """Error during single connection handling - closing connection"""
class UserHandlerError(Error):
    """Errors running caller - defined subclass methods"""
class ListenError(Error):
    """Errors binding tcp dispatcher to port and addressess"""

class Close(BaseException):
    """End asyncore loop"""

class ConnectionHandler(asynchat.async_chat):
    """
    DESCRIPTION
        Handle incoming connection requests and data. One instance if this 
        class is created for each connection.
    """

    def __init__(self, conn, addr, id, server_ref, cfg ):
        self.addr = addr
        self.id   = id
        self.eol  = server_ref.eol 
        self.eof  = server_ref.eof
        self.server_ref = server_ref
        self.cfg = cfg

        log.debug(
            "Initiating handler instance for connection from %s" % self.id
        )

        asynchat.async_chat.__init__(self, conn )
        self.set_terminator(self.eol)

        self.data = ''
        self.postConnect()

        log.debug ("eol:%s" % self.eol)

    def collect_incoming_data(self, data):
        """Collect the data arriving on the connexion"""
        self.data += data

    def found_terminator(self):
        """Handle end-of-line (one data partikel)"""
        # exit on hard wired client exit code
        data = str( self.data ).strip().strip("'")
        if data == self.eof:
            log.debug( "End-of-file found: %s" % self.id )
            self.handle_close()
        else:
            self.data = ''
            self.receivedData( data )

    def handle_close(self):
        log.info( "Disconnecting %s" % self.id )
        self.preDisconnect()
        self.server_ref.client_list.remove( self )
        asynchat.async_chat.handle_close(self)


    # Action handlers, use them
    def Send(self, data, client=None):
        """
        Send data back to this or a specified client listed in
        self.server_ref.clients
        """
        if client is None:
            self.push( data )
        else:
            client.push( data )

    def forceDisconnect(self, client=None):
        """
        Force client disconnect of this or a specified client listed in
        self.server_ref.clients
        """
        if client is None:
            self.handle_close()
        else:
            client.handle_close()

    # Event handlers: subclass these
    def postConnect(self):
        """Client just connected succesfully"""
        log.debug( "postConnect: subclass me!" )

    def receivedData(self, data ):
        """Data stream to eol received"""
        log.debug( "receivedData: subclass me!" )
    
    def preDisconnect(self):
        """Data stream to eof receivedi or other close command"""
        log.debug( "preDisconnect: subclass me!" )



 
#----------------------------------------------------------------------------
# dispatcher class (supervisor for client connections)
#----------------------------------------------------------------------------
class TcpServer(asyncore.dispatcher):
    """
    DESCRIPTION
        Handle incoming connection requests, start one user_conn_handler
        instance per connection and run it
    """

    # class config
    allow_reuse_address         = ALLOW_REUSE_ADDR
    request_queue_size          = REQUEST_QUEUE_SIZE
    address_family              = socket.AF_INET
    socket_type                 = socket.SOCK_STREAM

    # instance config
    def __init__(
        self,
        ip, port, 
        eol      = EOL, 
        eof      = EOF,
        max_conn = MAX_CONN,
        timeout  = TIMEOUT,
        ConnHandler = ConnectionHandler,
        ConnHandler_cfg = None
    ):

        # handle instance data
        self.addr = ( ip, int( port ) )
        self.id   = self.getId( self.addr )
        self.eol  = eol
        self.eof  = eof
        self.max_conn = int( max_conn )
        self.timeout  = float( timeout )

        self.ConnHandler       = ConnHandler
        self.ConnHandler_cfg   = ConnHandler_cfg

        self.startListening()
        self.client_list = []
        self.stop = self.handle_close

        log.debug( "Tcp server now listening on %s" % self.id  )



    def start(self):
        log.info( 
            "Tcp server waiting for connections (max %s), timeout %s seconds" 
            % (self.max_conn, self.timeout) 
        )
        while asyncore.socket_map:
            try:
                asyncore.loop(timeout=self.timeout, count = self.max_conn )
            except KeyboardInterrupt:
                log.info( "User break, stopping connection and server" )
                self.stop()

    def handle_connect(self):
        """place handshake stuff here"""
        log.debug( "Tcp Server handle_connect() called")

    def handle_close(self):

        for client in self.client_list:
            log.info( "Shutting down connection to client %s" % client.id)
            try:
                client.push( emsg + self.eol )
                client.close()
            except:
                pass
        log.info(   
            "Tcp Server %s shutting down, see server logging" % self.id
        )
        self.close()
        raise Close( "Ending asynchore loop")

    def handle_accept(self):
        """
        Called when a client connects to socket. Establish connection
        even in case there's more than max_conn to send a message back to 
        client.
        """

        nof_conn = len( self.client_list ) # current number of connections

        # see if connection works
        try:
            conn, addr = self.accept()
        except socket.error, emsg:
            raise AcceptError(
                "Tcp server error accepting new connection\n%s" % emsg
            )
        except TypeError:
            raise AcceptError(
                "Tcp server not accepting new connection, socket is blocked'"
            )

        id = self.getId(addr)
        log.info(
            "Connection %s/%s accepted from %s" 
            % ( nof_conn + 1, self.max_conn, id )
        )

        client = self.ConnHandler( conn, addr, id, self, self.ConnHandler_cfg )
        self.client_list.append( client )
        if nof_conn + 1 > self.max_conn:
            client.push( 
                "Maximum number of connections (%s) exceeded at host %s, bye!"
                % (self.max_conn, self.id) + self.eol
            )
            client.handle_close()
#            self.client_list.remove( client )
            log.error(
                "Client %s exceeded limit (%s) for number of connections, "
                "disconnected now" % (id, self.max_conn)
            )

    def getId(self, addr):
        """Convert addr tupel to adress, port string"""
        return "address %s, port %s" % (addr[0], addr[1])

    def startListening(self):
        # initiate dispatcher
        log.debug( "Initiating dispatcher class" )
        asyncore.dispatcher.__init__(self)
        log.debug( "Creating socket")
        self.create_socket(self.address_family, self.socket_type)

        if self.allow_reuse_address:
            self.set_reuse_addr()

        # bind to socket, listen
        log.debug( "Binding to socket %s" % self.id )
        try: 
            self.bind( self.addr ) # bind expects tupel
        except socket.error, emsg:
            if emsg[0] == 99:
                raise ListenError(
                    "Could not bind to %s, address not found" % self.id
                )
            else:
                raise 

        log.debug(
            "Listening: backlog=%d (maximum number of queued connections, "
            "lower this to 5 if your OS complains)" % self.request_queue_size)
        self.listen(self.request_queue_size)

#-----------------------------------------------------------------------------
if __name__ == "__main__":
#-----------------------------------------------------------------------------
    import sys
    import os
    import pt.terminal
    import pt.logger   # set up logger

    # initialize logger
    log = pt.logger.Logger(
        # style = "plain",
        name         = __name__ , # __name__ or self.__class__.__name__ 
        level        = logging.DEBUG,  
        file_file    = None,      # None = no file logging
        file_level   = logging.DEBUG,         
    )


    server = TcpServer( 
#        addr      = '10.10.210.3' ,
        ip      = DEFAULT_ADDR    , # do not use variable addr, used internally!
        port      = DEFAULT_PORT    , # port to listen on
        #eol       = EOL             , # end of line identifier string
        eol       = '\n'             , # end of line identifier string
        eof       = EOF             , # end of data identifier string
        max_conn  = 2               , # maximum number of connections       
        timeout   = 10              , # seconds for each connection
        ConnHandler = ConnectionHandler,    
    )

    try:
        server.start()
    except KeyboardInterrupt:
        print "\nCrtl+C pressed. Shutting down."
        sys.exit(0)


