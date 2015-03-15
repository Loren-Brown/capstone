import socket, sys

port = int(sys.argv[1])

print 'Starting Client'
print 'Type quit to quit'
clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
	clientsocket.connect(('localhost', port))
except socket.error, msg:
	print 'Connect failed. Error Code: ' + str(msg[0])+ 'Error Message: ' + str(msg[1])

while 1:
	usr = raw_input('##')
	if usr.lower() == 'quit':
		break
	clientsocket.send(usr.lower())
print 'Closing socket'
clientsocket.shutdown(socket.SHUT_RDWR)
clientsocket.close()
	