import numpy as np

class CinematicaInversa:
	def __init__(self, maxSignal, maxAngle, maxXPos, track, YPos, dt, LsDcF):
		"""Given the following values, allows the calculations needed for a inverse kinematic:
			maxSignal = maxValue of dutycylcle
			maxAngle = the maximum angle that can be seen by the camera
			maxXPos = the maximum x value that can be seen by the camera
			track = vehicle's width track. Distance from left to right wheel
			YPos = distance from the center of the vehicle's axis to the camera's closest point
			dt = time expected to be considered into the speed calculations.
		"""
		self.maxSignal = maxSignal
		self.maxAngle = maxAngle
		self.maxXPos = maxXPos
		#self.YPos = YPos
		self.track  = track
		self.YPos = YPos
		self.dt = 1.0/dt
		self.LinearSpeedDutyCycleFactor = 1.0/LsDcF
		self.angleFactor = maxSignal / maxAngle
		self.xPosFactor = maxSignal / maxXPos
	#IC = CinematicaInversa(100,numpy.deg2rad(20),0.09,0.125,0.125 0.2,0.043)


	def getLinearSpeed(self, xoffset, ypos):
		"""Returns the linear speed of a differential configuration from the target point x and y coordinates"""
		angle = xoffset / self.angleFactor
		correctedAngle = angle + np.deg2rad(90)
		#print 'Angle:',np.rad2deg(angle),'degrees'
		#print 'Corrected Angle:',np.rad2deg(correctedAngle),'degrees'

		xpos = xoffset / self.xPosFactor
		#print 'Xpos:',xpos,'m'
		vx = (xpos * np.cos(correctedAngle)) / self.dt
		vy = (ypos * np.sin(correctedAngle)) / self.dt
		#print 'V(x):',vx,'m/s V(y):', vy,'m/s'
		v = np.sqrt(vx**2 + vy**2) #instead of v = vx + vy /2
		#print 'V:',v,'m/s'
		deltaV = (self.track * angle) / self.dt
		#print 'DeltaV:', deltaV, 'm/s'
		#deltaV was deltaV / 2
		vl = v + 1.9*deltaV 
		vr = v - 1.9*deltaV
		#print 'Vl', vl,'m/s Vr', vr,'m/s'
		return (vl, vr)


	def LinearSpeedToDutyCycle(self, v):
		"""Returns the dutycycle value needed to apply to achive a given speed"""
		return v * self.LinearSpeedDutyCycleFactor
