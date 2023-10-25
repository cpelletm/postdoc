import socket

HEADER=64 # size in bytes of the message length
PORT=5050 # port to connect to
FORMAT="utf-8" # encoding format of the communications between server and clients
DISCONNECT_MESSAGE="DISCONNECT" # message to disconnect from the server
SERVER="127.0.1.1"
ADDR=(SERVER,PORT)

client=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client.connect(ADDR)