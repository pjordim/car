#from motors.motor import *
# from motors import motor
from motors.motor import motor
#from sensor import UltrasonicSensor

class CarDifferential:
	"""Needs further abstaction. Describes a car with a differential control (steering through different speed on each side).
	It's meant to be used through a L298N driver where motors on same side are connected to same control output.
	"""
	def __init__(self,pins,freq = 100):
		enable, aMotor, bMotor = pins
		self.left_motor = motor(enable,aMotor,bMotor,freq)

	def motion(self, LeftDC, RightDC):
		if LeftDC > 0:
			self.left_motor.forward(LeftDC)
		elif LeftDC < 0:
			self.left_motor.backward(-LeftDC)
		else:
			self.left_motor.idle()


