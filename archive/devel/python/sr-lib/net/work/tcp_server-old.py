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
    'UserHandlerError'
    'ListenError'
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
EOL = '\n'
EOF = "bye"
DEFAULT_PORT = 5000
DEFAULT_ADDR = "0.0.0.0"

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


#----------------------------------------------------------------------------
# main class
#----------------------------------------------------------------------------
class TcpServer(asyncore.dispatcher):
    """
    DESCRIPTION
        Handle incoming connection requests, start one user_conn_handler
        instance per connection and run it
    FEATURES
    OPTIONS
    METHODS
    EXCEPTIONS
    LOGGING
    EXAMPLE
    """
    #------------------------------------------------------------------------
    # Standard Methods
    #------------------------------------------------------------------------
    def __init__ (self, 
            port, 
            address, 
            eol, 
            eof,
            max_conn    =None   , 
            timeout     =5      , 
            backlog     =5      ,
            user_conn_handler = None, 
        ):
        # handle parameters
        self.eol        = eol
        self.eof        = eof
        self.max_conn   = max_conn
        self.timeout    = timeout
        self.address       = address
        self.port       = port
        self.id         = "address %s, port %s" % ( address, port )
        self.user_conn_handler = user_conn_handler

        if user_conn_handler is None \
        or type( user_conn_handler ) is not type ( ConnectionHandler ):
            raise UserHandlerError(
                "Subclass pt.net.tcp_server.ConnectionHandler like "
                "\nclass MyConnectionHandler(ConnectionHandler)"
                "\n and hand it over to TcpServer as user_conn_handler = "
                "MyConnectionHandler!"
            )

        # initate server 
        asyncore.dispatcher.__init__(self)
        self.create_socket (socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()

        try:
            self.bind((address, port))
        except socket.error, emsg:
            if emsg[0] == 99:
                raise ListenError(
                    "Could not bind to %s, address not found" % address
                )
            else:
                raise 
        # backlog: maximum number of queued connections lower this to 5 if your 
        # OS complains
        if max_conn is None:
            self.listen ( backlog )
        else:
            self.listen( max_conn )

        # hold all clients in this list
        self.clients = []

        # success message
        log.info( "Tcp server now listening on %s" % self.id )


    def handle_accept(self):
        """Called when a client connects to socket"""

        # see if connection works
        try:
            conn, (address, port ) = self.accept()
        except socket.error, emsg:
            raise AcceptError(
                "Tcp server error accepting new connection\n%s" % emsg
            )
        except TypeError:
            raise AcceptError(
                "Tcp server not accepting new connection, socket is blocked'"
            )


        # create socket channel handler instance
        log.info(
            "Connection %s/%s accepted from address %s, port %s. " 
            % (len( self.clients ) + 1, self.max_conn, address, port)
        )
        client = self.user_conn_handler( 
            conn, 
            address,
            port,
            self.eol, 
            self.eof,
            server_ref = self
        )
        # append client to internal (TcpServer class) clients list
        self.clients.append( client )

        # check if number of clients does not exceed limit
        if len( self.clients ) > self.max_conn:
            client.HandleError( 
                "Ignoring connection from %s, maximum number of "
                "connections (%s) reached!" % ( self.id, self.max_conn )
            )


#        # break connection, notify client when max number of client is reached
#        client.check_nof_connections( 
#            len( asyncore.socket_map ),
#            self.max_conn
#        )

    def handle_connect(self):
        """place handshake stuff here"""
        log.debug( "Tcp Server handle_connect() called")

    def handle_close(self):
        log.debug( "Tcp Server handle_close() called")
        self.close()
            

    def start(self):
        log.info( 
            "Tcp server waitung for connections (max %s)" 
            % self.max_conn 
        )
        while asyncore.socket_map:
            asyncore.loop(timeout=self.timeout, count=1)


#----------------------------------------------------------------------------
# tcp connection handler
#----------------------------------------------------------------------------
class ConnectionHandler(asynchat.async_chat):
    """
    DESCRIPTION
        Handle incoming connection requests and data. One instance if this 
        class is created for each connection.
    """

    def __init__(self, conn, address, port, eol, eof, server_ref ):
        self.address = address
        self.port = port
        self.eol = eol
        self.eof = eof
        self.server_ref = server_ref
        self.id = "address %s, port %s" % ( address, port )

        log.debug(
            "Initiating handler instance for connection from %s" % self.id
        )
        # initiate instance low level methods
        asynchat.async_chat.__init__(self, conn )
        self.data = ''
        self.HandleConnect()

    def handle_error(self ):
        self.HandleError(
            "Connection failure, disconnecting client %s" % self.id )


    def collect_incoming_data(self, data):
        """Collect the data arriving on the connexion"""
        self.data += data

    def found_eol(self):
        """Handle end-of-line (one data partikel)"""
        # exit on hard wired client exit code
        data = self.data.strip( self.eol ).strip()
        if data == self.eof:
            self.handle_close()
        else:
            self.data = ''
            self.HandleRecv(data)

    def handle_close(self):
        log.info( "Disconnecting %s" % self.id )
        self.HandleDisconnect()
        self.server_ref.clients.remove( self )
        asynchat.async_chat.handle_close(self)

    #-------------------------------------------------------------------------
    # override these methods after subclassing ConnectionHandler
    #-------------------------------------------------------------------------
    def HandleRecv( self, data ):
        """This method is called when new data arrive at socket."""

        raise NotImplemented( 
            self.HandleRecv.__doc__ + "\nYou should override this "
            "method when you subclass ConnectionHandler!"
        )


    def HandleError(self, emsg):
        log.error( emsg )
        self.push( emsg + self.eol )
        self.close()

    def HandleConnect( self ):
        """This method when client connects"""
        log.error( 
            "HandleConnect not subclassed"
#            "%s \nYou should override this "
#            "method when you subclass ConnectionHandler!" % self.HandleConnect.__doc__
        )
    def HandleDisconnect(self):
        """
        This method is called before client is removed from
        server's client list
        """
        raise NotImplemented( 
            self.HandleDisconnect.__doc__ + "\nYou should override this "
            "method when you subclass ConnectionHandler!"
        )
    def Send(self, data, client=None):
        """
        Send data back to this or a specified client listed in
        self.server_ref.clients
        """
        raise NotImplemented( 
            self.Send.__doc__ + "\nYou should override this "
            "method when you subclass ConnectionHandler!"
        )
    def DisconnectClient(self, client=None):
        """
        Force client disconnect of this or a specified client listed in
        self.server_ref.clients
        """
        raise NotImplemented( 
            self.Disconnect.__doc__ + "\nYou should override this "
            "method when you subclass ConnectionHandler!"
        )


if __name__ == "__main__":
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

    # example class
    class MyConnectionHandler(ConnectionHandler):
        def __init__(self, conn, address, port, eol, eof, server_ref ):
            ConnectionHandler.__init__(
                self, conn, address, port, eol, eof, server_ref
            )

    def HandleRecv( self, data ):
        """This method is called when new data arrive at socket."""
        log.debug("MyConnectionHandler:received new data!")

    def HandleConnect( self ):
        """This method when client connects"""
        log.debug("MyConnectionHandler: new conection!")

    def HandleDisconnect(self):
        """
        This method is called before client is removed from
        server's client list
        """
        log.debug("MyConnectionHandler: cleint disconnected!")

    def Send(self, data, client=None):
        """
        Send data back to this or a specified client listed in
        self.server_ref.clients
        """

    def DisconnectClient(self, client=None):
        """
        Force client disconnect of this or a specified client listed in
        self.server_ref.clients
        """


    server = TcpServer( 
#        address     = '10.10.210.3' ,
        address      = DEFAULT_ADDR    ,
        port      = DEFAULT_PORT    , # port to listen on
        eol       = EOL             , # end of line identifier string
        eof       = EOF             , # end of data identifier string
        max_conn  = 2               , # maximum number of connections       
        timeout   = 10              , # seconds for each connection
        user_conn_handler = MyConnectionHandler,    
    )

    try:
        server.start()
    except KeyboardInterrupt:
        print "\nCrtl+C pressed. Shutting down."
        sys.exit(0)





 
    sys.exit(0)
    def Recv(self, data):
        """        
        You should override the Recv() method when you subclass 
        DefaultHandler. This method is called when new data arrive at socket
        """
        print self.Recv.__doc__
        # demo
        self.Send( "Debug: %s\n" % data )
        log.debug("Sending debug data from %s: %s" % ( self.client.id, data ) )
        if data == "kill":
            self.Disconnect()

    def Send(self, data, client=None):
        """
        Use this method to send data back to client, client parameter
        is optional but can be used to sent do other clients
        """
        if client is None:
            self.client.push( data )
        else:
            client.push( data )

    def Disconnect(self, data, client=None):
        """
        Use this method to send data back to client, client parameter
        is optional but can be used to sent do other clients
        """
        if client is None:
            self.client.handle_close()
        else:
            client.handle_close()

    def handleConnect(self):
        """        
        You should override the Connect() method when you subclass 
        DefaultHandler. This method is called when a nerw client connects.
        """
        print self.Connect.__doc__
        # demo
        self.Send( "Debug: Hello\n" )
        log.debug( "User connected %s" % self.client )

        for client in self.server_ref.clients:
            if client is not self.client:
                log.debug( "Other connected client: %s" % client )
        
    def handleDisconnect(self):
        """        
        You should override the Disconnect() method when you subclass 
        DefaultHandler. This method is called when a client disconnects
        """
        print self.Disconnect.__doc__
        # demo
        self.Send( "Debug: Bye bye!\n")
        log.debug( "debug: user disconnected %s" % self.client )
