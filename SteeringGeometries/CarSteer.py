#from motor import *
#from motors.motor import motor
from motors import motor
class CarSteer:
	"""Needs further abstaction. Describes a car with an absolute steering 
	control (steering can be centered, left or right).
	"""
	def __init__(self, tMotor, sMotor,freq=100):
		enableT, bMotorT, aMotorT = tMotor
		self.traction_motor = motor(enableT,aMotorT,bMotorT,freq)
		enable, bMotor, aMotor = sMotor
		self.steering_motor = motor(enable,aMotor,bMotor,freq)


	def motion(self, tractionDC, steeringDC):
		if tractionDC > 0:
			self.traction_motor.forward(tractionDC)
		elif tractionDC < 0:
			self.traction_motor.backward(-tractionDC)
		else:
			self.traction_motor.idle()
		if steeringDC > 0:
			self.steering_motor.forward(steeringDC)
		elif steeringDC <0:
			self.steering_motor.backward(-steeringDC)
		else:
			self.steering_motor.idle()


