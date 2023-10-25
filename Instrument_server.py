import rpyc
from rpyc.utils.server import ThreadedServer
import GUI_lib as glib
import time

class generalInstrumentService(rpyc.Service):
    #Service name is both the name of the service on the network,
    #and the name of the associated config file
    serviceName='general instrument'
    computerName=glib.computerDic['computer name']

    #Action happening the first time the service is instanciated
    def __init__(self) -> None:
        self.timeCreated=time.time()
        self.__class__.ALIASES=[self.serviceName+' ON '+self.computerName]
        self.config=glib.localVariableDic(self.serviceName+'.json')

    #Action happening when a client calls the service
    def on_connect(self, conn):
        print("Connection established to :%s with :%s "%(self.serviceName, conn))

    #Action happening when a client calls the service
    def on_disconnect(self, conn):
        print("Connection lost to :%s with :%s "%(self.serviceName, conn))

    #Note : by default, all atributes are hidden from the client
    #In order to be accessible, they must either start with "exposed_" 
    #Or you need to set the protocol_config={"allow_public_attrs": True} in the server
    def uptime(self,format='days'):
        #Format = 'days' or 'seconds'
        Deltat=time.time()-self.timeCreated
        if format=='days':
            nDays=int(Deltat/86400)
            nHours=int((Deltat-nDays*86400)/3600)
            nMinutes=int((Deltat-nDays*86400-nHours*3600)/60)
            nSeconds=int(Deltat-nDays*86400-nHours*3600-nMinutes*60)
            return f'{nDays} days, {nHours} hours, {nMinutes} minutes, {nSeconds} seconds'
        elif format=='seconds':
            return Deltat

class dummyInstrumentService(generalInstrumentService):
    serviceName='dummy instrument'
    def __init__(self) -> None:
        super().__init__()


def createServer(service, port=0,protocol_config={"allow_public_attrs": True}, auto_register=True, sameInstance=True):
    '''port=0 means that the OS will choose a random port, 
    protocol_config={"allow_public_attrs": True} makes all attributes from the server accessible to the client,
    auto_register=True means that the service will be automatically registered on the network
    sameInstance=True means that all the clients will access the same instance of the service.'''
    if sameInstance:
        import inspect
        if inspect.isclass(service):
            service=service()
    #The way rpyc servers work is that if you send a service class to the server (eg MyService),
    #the server will create a new instance of the service class for each client.
    #If you send an instance of the service class (eg MyService()), the server will share the same instance between all the clients.
    t = ThreadedServer(service, port = port, protocol_config=protocol_config, auto_register=auto_register)
    t.start()

if __name__ == "__main__":
    pass
    # createServer(generalInstrumentService, sameInstance=True)