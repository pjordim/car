import RPi.GPIO as GPIO
from picamera import PiCamera
from time import sleep
from SteeringGeometries.CarDifferential import CarDifferential
from Control.CinematicaInversa import CinematicaInversa
from Car import Car
import sensors.CameraControl
import numpy as np
import sys
import serial
def main():
        geo = CarDifferential((13,26,19),50)    
	#geo = CarDifferential((21,16,20),(26,13,19),100)
	kinematics = CinematicaInversa(100,np.deg2rad(20),0.09,0.125,0.07,10,0.043)
	ser = serial.Serial('/dev/serial0', 115200)
	minDistance = 15
	res = (320, 240)
	#res = (460,320)
	fps = 35
	#cam = cameraSetup(res,40,hf=True,vf=True,mode='backlit')
	roboto = Car('roboto', geo, kinematics, ser, minDistance)
	##Control from camera
	roboto.runCamera(res,fps)
	GPIO.cleanup()
	sys.exit()
	##Control from parameters for calibration
		# roboto.geo.motion(30,30)
		# sleep(0.02)
		# roboto.geo.motion(20,20)
		# sleep(5)
		
	##Ranging sensors for test
		#print 'Measuring about to start...'
		
		#for i in range (5) :
			#print 'Motion value is ',(i)*10,'%'
			#roboto.geo.motion((i)*10,(i)*10)
			#sleep(0.2)	
		#roboto.geo.motion(0,0)
		#for i in range (11):
		#	print roboto.sr.measure()
		#	sleep(0.001)
			#print roboto.sc.measure()
			#sleep(0.2)
			#print roboto.sl.measure()
			#sleep(0.2)
		# print roboto.sl.measure_burst(7,0.001)
		# sleep(0.1)
		# print roboto.sc.measure_burst(7,0.001)
		# sleep(0.1)
		# print roboto.sr.measure_burst(7,0.001)
		# sleep(0.1)

try:
	main()
	#sleep(0.01)
except SystemExit:
	pass
except:
	print('Exception caught in Roboto')
	#GPIO.cleanup()
	raise