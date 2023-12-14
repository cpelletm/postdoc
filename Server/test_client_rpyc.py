import rpyc

addresses=rpyc.discover("UPTIME ON CLEMENT LAPTOP")
c=rpyc.connect(*addresses[0])
service=c.root
print(service.uptime())