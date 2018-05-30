#from motors.motor import *
from motors import motor


class CarDifferential2:
	"""Needs further abstaction. Describes a car with a differential control (steering through different speed on each side).
	It's meant to be used through two L298N driver where each motor is connected to a different control output and 
	motors on same side are meant to move in the same way.
	"""
	def __init__(self,lMotor1, lMotor2, rMotor1, rMotor2,freq = 100):
		enable, aMotor, bMotor = lMotor1
		self.left_motor1 = motor(enable,aMotor,bMotor,freq)
		enable, aMotor, bMotor = lMotor1
		self.left_motor2 = motor(enable,aMotor,bMotor,freq)
		enable, aMotor, bMotor = rMotor1
		self.right_motor1 = motor(enable,aMotor,bMotor,freq)
		enable, aMotor, bMotor = rMotor2
		self.right_motor2 = motor(enable,aMotor,bMotor,freq)

	def motion(self, LeftDC, RightDC):
		if LeftDC > 0:
			self.left_motor1.forward(LeftDC)
			self.left_motor2.forward(LeftDC)

		elif LeftDC < 0:
			self.left_motor1.backward(-LeftDC)
			self.left_motor2.backward(-LeftDC)
		else:
			self.left_motor1.idle()
			self.left_motor2.idle()
		if RightDC > 0:
			self.right_motor1.forward(RightDC)
			self.right_motor2.forward(RightDC)
		elif RightDC < 0:
			self.right_motor1.backward(-RightDC)
			self.right_motor2.backward(-RightDC)
		else:
			self.right_motor1.idle()
			self.right_motor2.idle()


