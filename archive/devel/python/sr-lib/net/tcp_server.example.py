#!/usr/bin/env python
# -*- coding: utf-8 -*-
#vim:fdm=marker
# unlock vim folding via zR, zo and lock folding via zM, zc
#----------------------------------------------------------------------------
"""                                                                     
 DESCRIPTION  socket server class implementation example
 
       
 CHANGELOG    
    10-08-25 * new

 TODO
 
 THANKS TO
        Daniel d'Andrada T. de Carvalho Location: Helsinki, Finland 

"""

__version__ = "$Revision: 1.0 $"
# $Source$


#----------------------------------------------------------------------------
# modules import, constants                                              {{{1
#----------------------------------------------------------------------------
import tcp_server
import logging
log = logging.getLogger( __name__ )


#----------------------------------------------------------------------------
# subclassed connection handler
#----------------------------------------------------------------------------
class MyConnectionHandler(tcp_server.ConnectionHandler):
    """
    DESCRIPTION
        Handle incoming connection requests and data. One instance if this 
        class is created for each connection.

    METHODS 
        * to be used directly
            Send(self, data, client=None)          
            forceDisconnect(self, client=None)

        * to be overridden
            postConnect(self)
            receivedData(self, data )
            preDisconnect(self)
    """

    def __init__(self, conn, addr, id, server_ref ):

        # leave this and __init__ invokation as - is
        tcp_server.ConnectionHandler.__init__(
            self, conn, addr, id, server_ref
        )

        # put your stuff here

    def postConnect(self):
        """Client just connected succesfully"""
        log.debug( "postConnect: subclassed!" )

        self.Send( self.eol + "Welcome!" + self.eol )

    def receivedData(self, data ):
        """Data stream to eol received"""
        log.debug( "receivedData: subclassed!" )

        if data == "kill":
            msg = ("Received Kill-All signal!")
            log.info(msg )
            for client in self.server_ref.client_list:
                client.Send( msg + self.eol) 
                client.forceDisconnect()
            self.forceDisconnect()
        else:
            for client in self.server_ref.client_list:
                client.Send( data +self.eol )


    def preDisconnect(self):
        """Data stream to eof receivedi or other close command"""
        log.debug( "preDisconnect: subclassed!" )


#----------------------------------------------------------------------------
# shell executable
#----------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    import os
    import pt.terminal
    import pt.logger   # set up logger

    # initialize logger
    log = pt.logger.Logger(
        # style = "plain",
        # name         = __name__ , # __name__ or self.__class__.__name__ 
        level        = logging.DEBUG,  
        #level        = logging.INFO,  
        file_file    = None,      # None = no file logging
        file_level   = logging.DEBUG,         
    )


    server = tcp_server.TcpServer( 
        ip      = "0.0.0.0"    , # do not use variable addr, used internally!
        port      = 5000   , # port to listen on
        #eol       = EOL             , # end of line identifier string
        eol       = '\n'             , # end of line identifier string
        eof       = 'bye'             , # end of data identifier string
        max_conn  = 1               , # maximum number of connections       
        timeout   = 10              , # seconds for each connection
        ConnHandler = MyConnectionHandler,    
    )

    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()
        print "\nCrtl+C pressed. Shutting down."
        sys.exit(0)


