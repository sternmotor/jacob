 #
 # An example that uses stacklesssocket to provide a chat like application.
 # The users connect via telnet to the IP:port of the server and type in any
 # text and all users connected receives it.
 # The server identifies an special character to close the connection and handle
 # the connected client list.
 #
 # The example is based on mud.py but uses the standard dispatcher creating a
 # tasklet for each connectedclient.
 #
 # Author: Carlos Eduardo de Paula <carlosedp@gmail.com>
 #
 # This code was written to serve as an example of Stackless Python usage.
 # Feel free to email me with any questions, comments, or suggestions for
 # improvement.
 #
 # But a better place to discuss Stackless Python related matters is the
 # mailing list:
 #
 #   http://www.tismer.com/mailman/listinfo/stackless
 #
 #
 # *** Code modified by Chad Lung to work with Flash CS4 ***
 # Original code can be found here:
 # http://stacklessexamples.googlecode.com/svn/trunk/examples/networking/chatServer.py
 #
  
 import sys, time
 #import time
 import stackless
  
 import stacklesssocket
 #sys.modules["socket"] = stacklesssocket
 stacklesssocket.install()
 import socket
  
 class Server(object):
     def __init__(self, conn):
         self.clients = {}
         # Create an INET, STREAMing socket
         self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
         self.serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
         # Bind the socket to an addres, and a port
         self.serversocket.bind(conn)
         # Become a server socket
         self.serversocket.listen(5)
         stackless.tasklet(self.acceptConn)()
  
     def acceptConn(self):
         while self.serversocket.accept:
             # Accept connections from outside
             (clientsocket, address) = self.serversocket.accept()
             # Now do something with the clientsocket
             # In this case, each client is managed in a tasklet
             stackless.tasklet(self.manageSocket)(clientsocket, address)
             stackless.schedule()
  
     def manageSocket(self, clientsocket, address):
         # Record the client data in a dict
         self.clients[clientsocket] = address
         print "Client %s:%s connected..." % (address[0],address[1])
         # For each send we expect the socket returns 1, if its 0 an error ocurred
         if not clientsocket.send('Connection OK Type "quit" to quit.\0'):
             clientsocket.close()
             return
         data = ''
         while clientsocket.connect:
             data += clientsocket.recv(4096)
  
             print data
  
             if data == '':
                 break
             # If we detect a \0 filter the event
             if '\0' in data:
                 if data == '\0':
                     if not clientsocket.send("Empty string sent\0"):
                         break
                 elif data == 'quit\0':
                     # If the user sends a q!, close the connection and remove from list
                     print "Closed connection for %s:%s\0" % (address[0],address[1])
                     del self.clients[clientsocket]
                     break               
                 elif data == 'look\0':
                     # Show the connected clients
                     clientsocket.send("There are %d users connected:\0" % len(self.clients))
                     clientsocket.send("Name\tHost\t\tPort\0")
                     clientsocket.send("-" * 40 +"\0")
                     for clientIP, clientPort in self.clients.itervalues():
                         clientsocket.send("Unknown\t"+ str(clientIP) +"\t"+ str(clientPort) +"\0")
                 else:
                     # Send the message to all connected clients
                     for client in self.clients:
                         if client is clientsocket:
                             if not client.send('\rYou said: %s\0' % data):
                                 break
                         else:
                             if not client.send('\rClient %s said: %s\0' % (address,data)):
                                 break
                 data = ''
             stackless.schedule()
         clientsocket.close()
  
 if __name__ == "__main__":
     print "test"
#     host = "127.0.0.1"
#     port = 12131
#     print "Starting up server on IP:port %s:%s" % (host, port)
#     s = Server((host,port))
#     stackless.run()

