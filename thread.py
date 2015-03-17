# cs.???? = currentstate, any variable on the status tab in the planner can be used.
# Script = options are
# Script.Sleep(ms)
# Script.ChangeParam(name,value)
# Script.GetParam(name)
# Script.ChangeMode(mode) - same as displayed in mode setup screen 'AUTO'
# Script.WaitFor(string,timeout)
# Script.SendRC(channel,pwm,sendnow)
#

import sys, math, socket, threading, os, time, subprocess, clr
sys.path.append(r"c:\Python27\Lib\site-packages")
sys.path.append(r"c:\Python27\Lib")
#import os, time, subprocess, clr

import MissionPlanner
clr.AddReference("MissionPlanner.Utilities")

# * * * * * * * * * * * * * * * * * * * * * * *
#
# translates latitude and longitude against an angle and magnitude
#
# * * * * * * * * * * * * * * * * * * * * * * *

def translate(mag, lat, lon, angle):
	distanceNorth = math.cos(math.radians(angle)) * mag
	distanceEast = math.sin(math.radians(angle)) * mag
	print 'Distance North to start point: ',
	print distanceNorth
	print 'Distance East to start point: ',
	print distanceEast
	earthRadius = 6371000.0
	newLat = lat + (distanceNorth / earthRadius) * 180.0 / math.pi
	newLon = lon + (distanceEast / (earthRadius * math.cos(newLat * 180.0 / math.pi))) * 180 / math.pi
	ret = [newLat, newLon]
	return ret
	
'''def translate2(mag, lat, lon, angle):
	distanceNorth = math.sin(angle) * mag
	distanceEast = math.cos(angle) * mag
	lat_const = 111111.0/1.0 #111111 meters in 1 deg Latitude
	new_lat = lat + (distanceNorth * lat_const)
	lon_const = (111111.0 * math.cos(new_lat))/1.0
	new_lon = lon + (distanceEast * lon_const)
	ret = [new_lat, new_lon]
	return ret
'''	

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

	#print cs.alt,
	#print ' (',
	#print cs.alt_error,
	#print ' ERR)'

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
			
		#Close Script
		if temp == 'close':
			print 'Waiting for thread to return'
			Script.Sleep(2000) #ms
			serversock.shutdown(socket.SHUT_RDWR)
			serversock.close()
			print 'Ending Script...'
			break
			
		#Return Home and Land
		if temp == 'home':
			MAV.setMode("STABILIZE")
			Script.Sleep(2000) #ms
			print 'Current Flight Mode: ',
			print cs.mode
			MAV.setMode("RTL")
			Script.Sleep(2000) #ms
			print 'Current Flight Mode: ',
			print cs.mode
			
		#Land
		if temp == 'land':
			MAV.setMode("LAND")
			Script.Sleep(2000) #ms
			print 'Current Flight Mode: ',
			print cs.modes
			break
			
		#Manual Control (Auto)
		if temp == 'manual':
			MAV.setMode("AUTO")
			Script.Sleep(2000) #ms
			print 'Current Flight Mode: ',
			print cs.modes
			
		#Dev-mode reset
		if temp == 'devreset':
			MAV.setMode("AUTO")
			Script.Sleep(2000) #ms
			print 'Current Flight Mode: ',
			print cs.mode
			
		# Calculated Decent
		if temp[:4] == 'calc':
		
			usr_args = temp.split()
			s_alt = cs.alt
			if s_alt < 10:
				print 'Your altitude is too low to use for a calculated decent.'
				print 'Switching to the optional starting altitude argument.'
				s_alt = s_alt = float(usr_args[6])
				
			usr_args = temp.split()
			f_lat = float(usr_args[1])
			f_lon = float(usr_args[2])
			f_alt = float(usr_args[3])
			angle = float(usr_args[4])
			dir = float(usr_args[5])
			
			h = s_alt - f_alt
			mag = h / math.tan(angle)
			
			pair = translate(mag, f_lat, f_lon, dir+180)
			s_lat = pair[0]
			s_lon = pair[1]
			
			print 'Ground Distance: ',
			print mag
			print 'Starting Latitude:  ',
			print s_lat
			print 'Starting Longitude: ',
			print s_lon
			print 'Starting Altitude:  ',
			print s_alt
			print 'Building waypoints'
			print 'traveling....'
			Script.Sleep(2000) #ms
			print 'At Start Point. '
			Script.Sleep(1000) #ms
			print 'CAMERA ON'
			Script.Sleep(1000) #ms
			print 'Traveling to endpoint...'
			Script.Sleep(2000) #ms
			print 'At endpoint'
			print 'CAMERA OFF'
			print 'Done'
			
			
		#Launch
		if temp == 'launch':
			print 'Getting home(ground) cordinates'
			high_alt = 2
			low_alt = 1
			home_lat = cs.lat
			home_lon = cs.lng
			home_alt = cs.alt
			Script.Sleep(2000) #ms
			
			print 'Target Air Speed: ',
			print cs.targetairspeed
			
			print 'Building waypoint 1 ', 
			print high_alt,
			print 'm above home(ground)'
			wp1 = MissionPlanner.Utilities.Locationwp() # creating waypoint
			MissionPlanner.Utilities.Locationwp.lat.SetValue(wp1,home_lat)     # sets latitude
			MissionPlanner.Utilities.Locationwp.lng.SetValue(wp1,home_lon)     # sets longitude
			MissionPlanner.Utilities.Locationwp.alt.SetValue(wp1,home_alt + high_alt )     # sets altitude
			
			print 'Building waypoint 2 ', 
			print low_alt,
			print 'm above home(ground)'
			wp2 = MissionPlanner.Utilities.Locationwp() # creating waypoint
			MissionPlanner.Utilities.Locationwp.lat.SetValue(wp2,home_lat)     # sets latitude
			MissionPlanner.Utilities.Locationwp.lng.SetValue(wp2,home_lon)     # sets longitude
			MissionPlanner.Utilities.Locationwp.alt.SetValue(wp2,home_alt + low_alt )     # sets altitude
			
			print 'Flying to waypoint 1'
			MAV.setGuidedModeWP(wp1)
			#Script.Sleep(20000) #ms
			while cs.alt < (home_alt + high_alt - 1):
				Script.Sleep(1000) #ms
			
			print 'CAMERA ON'
			print 'Decending to waypoint 2'
			MAV.setGuidedModeWP(wp2)
			while cs.alt > (home_alt + low_alt + 1):
				Script.Sleep(1000) #ms
			
			print 'CAMERA OFF'
			print 'Landing'
			MAV.setMode("LAND")
			Script.Sleep(2000) #ms
			print 'Current Flight Mode: ',
			print cs.mode
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
		#break



