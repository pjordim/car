import threading, Queue, time, thread, cv2, numpy as np
import RPi.GPIO as GPIO
from Control.DistanceControl import DistanceControl
from GraphicProcessing.TrafficLightDetector import TrafficLightDetector
from picamera.array import PiRGBArray
from picamera import PiCamera
from sensors.CameraControl import CameraControl
from GraphicProcessing.BlobDetector import setBlobDetector	
from Communication.CarAgent import CarAgent
import spade
WN = 'window name'
modes = ['frame','iFilter','iGrey','iErode']
disp = 0
mode = modes[disp]


def ChangeDisp(disp):
	global mode
	mode = modes[disp]


class Car:
	def __init__(self, name, geo, kinematics, ser, minDistance):
		self.name = name # robot name
		self.geo = geo # robot steering geometry
		self.kinematics = kinematics
		self.ser = ser # sensors
		self.control = []
		self.minDistance = minDistance
		#self.control = CameraControl(self.geo, camRes,fps,hf=True,vf=True,mode='backlit')


	def getAController(self):
		"""Creates a new control set to False, adding it to the control list and returning it"""
		self.control.append(False)
		return self.control[-1],len(self.control)-1
	

	def getAControllerValue(self, value):
		"""Creates a new control set to given value, adding it to the control list and returning it"""
		self.control.append(value)
		return self.control[-1],len(self.control)-1


	def getControl(self):
		"""Will return a True value only if all elements in the control list are True,
		False if there is any False in the control list."""
		return all(self.control)


	def getControls(self):
		"""Returns the whole control array"""
		return self.control
	

	def changeControl(self,i):
		"""Sets the ith control to its opposite value. """
		self.control[i] = not self.control[i]
		return self.control[i]


	def setControl(self,i,value):
		"""Sets the ith control to the given value."""
		self.control[i]=value
		return self.control[i]


	def getGeo(self):
		"""Returns car's geometry"""
		return self.geo
	

	def runCamera(self,camRes,fps):
		"""Creates a distance control by using the ultrasonic sensor and also a trafficlight detector. After it, starts to use the camera for getting
		lane references to control the car."""
		try:
			ultrasonicCtrl, ultrasonicCtrlIndex = self.getAControllerValue(True)
			distanceControl = DistanceControl(self, ultrasonicCtrl, ultrasonicCtrlIndex, self.ser, self.minDistance)
			trafficLightCtrl, trafficLightCtrlIndex = self.getAControllerValue(True)
			trafficlightDetector = TrafficLightDetector(self,trafficLightCtrl,trafficLightCtrlIndex, setBlobDetector(), np.ones((3,3),np.uint8), np.array([244,124,119]), np.array([255,133,137]))
			ctrl,ctrlIndex = self.getAController()
			agent = CarAgent("caragent@127.0.0.1", "secret")
			agent.start()
			cc = CameraControl(self,ctrl,ctrlIndex,distanceControl,trafficlightDetector,camRes,fps,hf=True,vf=True,mode='backlit',agent = agent)
			cc.ThreadsStart()
			cc.ThreadsJoin()
		except spade.Agent.AgentNotRegisteredError:
			print "Spade Agent couldn't register. Check Spade platform state."
			GPIO.cleanup()
			raise
			exit()

		except:
			print('Caught an exception on runCamera in Car')
			raise
			exit()
