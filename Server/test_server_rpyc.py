import rpyc
import time
from rpyc.utils.server import ThreadedServer
import sys
sys.path.append('/home/clement/Postdoc/python/Perso/')
import GUI_lib as glib

'''Important: Finding the server on the network
In order to be found on the network, the servers must be started AFTER a registry server is running.'''

#In order to be found on the network, the service must follow the naming convention:
#XService, it can then be found with name X (case insensitive)
class MyService(rpyc.Service):
    ALIASES=["UPTIME ON CLEMENT LAPTOP"]
    #Action happening the first time the service is instanciated
    def __init__(self) -> None:
        self.t0=time.time()

    #Action happening when a client calls the service
    def on_connect(self, conn):
        print("Connection established with : ", conn)

    #Action happening when a client calls the service
    def on_disconnect(self, conn):
        print("Connection lost with : ", conn)

    #Note : by default, all atributes are hidden from the client
    #In order to be accessible, they must either start with "exposed_" 
    #Or you need to set the protocol_config={"allow_public_attrs": True} in the server
    def uptime(self):
        return time.time()-self.t0

if __name__ == "__main__":
    '''Important: Using an instance (MyService()) instead of the class (MyService) means
    that all the clients will access the same instance of the service.
    If using a class instead, a new instance will be created for each client.
    For most practical use, you should use an instance instead of a class (to share data and instrument between the clients)'''

    '''port=0 means that the OS will choose a random port, 
    protocol_config={"allow_public_attrs": True} makes all attributes from the server accessible to the client,
    auto_register=True means that the service will be automatically registered on the network'''
    t = ThreadedServer(MyService(), port = 0, protocol_config={"allow_public_attrs": True}, auto_register=True)
    t.start()
    