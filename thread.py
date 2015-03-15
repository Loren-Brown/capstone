# cs.???? = currentstate, any variable on the status tab in the planner can be used.
# Script = options are
# Script.Sleep(ms)
# Script.ChangeParam(name,value)
# Script.GetParam(name)
# Script.ChangeMode(mode) - same as displayed in mode setup screen 'AUTO'
# Script.WaitFor(string,timeout)
# Script.SendRC(channel,pwm,sendnow)
#

import sys
import socket, threading
sys.path.append(r"c:\Python27\Lib\site-packages")
sys.path.append(r"c:\Python27\Lib")
import os, time, subprocess, clr

import MissionPlanner
clr.AddReference("MissionPlanner.Utilities")

print 'Start Script'
for chan in range(1,9):
	Script.SendRC(chan,1500,False)
	Script.SendRC(3,Script.GetParam('RC3_MIN'),True)
	Script.Sleep(1000)	
print 'Setup Done'


class ClientThread(threading.Thread):

	def __init__(self,ip,port,clientsocket):
		threading.Thread.__init__(self)
		self.ip = ip
		self.port = port
		self.csocket = clientsocket
		print "[+] New thread started for "+ip+":"+str(port)

	def run(self):   
		global cmd
		print "Connection from : "+ip+":"+str(port)

		clientsock.send('Welcome to the servernn')

		data = "dummydata"

		while len(data):
			data = self.csocket.recv(2048)
			print "Client(%s:%s) sent : %s"%(self.ip, str(self.port), data)
			self.csocket.send("You sent me : "+data)
			
			sem.acquire()
			print 'added comand'
			cmd = data.lower()
			sem.release()
			
			#End Loop 'close'
			if data.lower() == 'close':
				break

		print "Client at "+self.ip+" disconnected..."

######GOBAL#######		
host = 'localhost'
port = 0
user_alt = -5000.0
cmd = ''
sem = threading.BoundedSemaphore(value=1)
##################

serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

serversock.bind((host,port))
print 'Open Port: ',
print serversock.getsockname()[1]

serversock.listen(5)
print 'Listening for incoming connections...'
try:
	(clientsock, (ip, port)) = serversock.accept()
except socket.error, msg:
	print 'Accept failed. Error Code: ' + str(msg[0])+ 'Error Message: ' + str(msg[1])

print 'Found Client'

newthread = ClientThread(ip, port, clientsock)
newthread.start()

print 'Arming Ground Avoidance'

#####################
#
#  Thread Is Running
#
#####################

while True:

	#print cs.alt

	if cs.alt > user_alt:
		temp = ''
		
		sem.acquire()
		temp = cmd
		cmd = ''
		if not temp == '':
			print 'removed comand'
		sem.release()
		
		#Ping Command
		if temp == 'ping':
			start_time = int(round(time.time() * 1000))
			m = cs.mode
			end_time = int(round(time.time() * 1000))
			print (end_time - start_time)
			
		#Reset Min Altitude
		if temp[:3] == 'min':
			user_alt = int(temp[3:])
			print 'New Minimum Altitude Set: ' + string(user_alt)
			
		#Close command
		if temp == 'close':
			print 'Waiting for thread to return'
			Script.Sleep(2000) #ms
			serversock.shutdown(socket.SHUT_RDWR)
			serversock.close()
			print 'Ending Script...'
			break

	else:
		print 'TOO LOW!'

		print 'Seting flight mode to LOITER'
		#Script.ChangeMode("LOITER")
		MAV.setMode("LOITER")
		Script.Sleep(1000) #ms
		print 'Checking flight mode'
		print cs.mode

		print 'Wait for drone (2 sec)'
		Script.Sleep(3000) #ms

		print 'Setting New Waypoint'
		wp = MissionPlanner.Utilities.Locationwp()
		print 'Moving up 1m'
		new_alt = cs.alt + 1
		MissionPlanner.Utilities.Locationwp.lat.SetValue(wp,cs.lat)
		MissionPlanner.Utilities.Locationwp.lng.SetValue(wp,cs.lng)
		MissionPlanner.Utilities.Locationwp.alt.SetValue(wp,new_alt)
		print 'Waypoint Set'
		MAV.setGuidedModeWP(wp)

		print 'Waiting on waypoint'
		while(cs.alt < new_alt) :
			
			print 'current alt: ',
			print cs.alt
			print 'target alt: ',
			print new_alt
			Script.Sleep(500) #ms

		print 'Seting flight mode to STABILIZE'
		#Script.ChangeMode("STABILIZE")
		MAV.setMode("STABILIZE")
		Script.Sleep(2000) #ms

		print 'Checking flight mode'
		print cs.mode

		print 'Done'
		print 'Disabling ground avoidance'
		break



