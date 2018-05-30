import numpy as np
import cv2



#Frame handling must be fixed for findlines. It must be accessed or sent??

class GraphicProcessing:
	def __init__(self, geo, car, res):
		self.geo = geo
		self.car = car
		#self.car = car
		self.res = res
		self.top = 7*res[1]/10
		self.bottom = res[1]-1
		self.frameWidth = res[0]
		self.frameWidthMidpoint = float(self.frameWidth/2)
		self.kernels = {}
		self.setupKernels()
		self.filters = {}
		self.setupFilters()
		self.lastLanePosition = 0
		self.lastLaneXpoint = None
		self.hough = {}
		self.setupHough()
		self.error = 0
		self.n = 0


	def setupHough(self):
		self.hough['rho'] = 1
		self.hough['theta'] = np.deg2rad(1)
		self.hough['threshold'] = 30
		self.hough['minLineLength'] = 15
		self.hough['maxLineGap'] = 5


	def setupFilters(self):
		self.filters['lowerFilter'] = np.array([0,0,180])
		self.filters['upperFilter'] = np.array([179,255,255])


	def setupKernels(self):
		self.kernels['erode'] = np.ones((5,5),np.uint8)
		#self.kernels['']

	
	def filterByColour(self, image):
		hsv = cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
		#hsv[0] = equalize(hsv[0])
		mask = cv2.inRange(hsv,self.filters['lowerFilter'],self.filters['upperFilter'])
		return cv2.bitwise_and(image,image,mask=mask)


	def getControlParameters(self, lines):
		"""Given a list of lines in the conventional form, returns the X offset and X position to the lane measured
		on the closest point to the vehicle. Both returned parameters have a [-1,1] range so they are resolution 
		independent.
		"""
		if lines is not None:
			closestLaneXPoint = self.res[0]
			closestLaneYPoint = 0
			#Gets the lane coordinates of the closest point to the car
			for x1,y1,x2,y2 in lines[0]:
				if y1 > closestLaneYPoint:
					closestLaneYPoint=y1
					closestLaneXPoint=x1
				if y2 > closestLaneYPoint:
					closestLaneYPoint=y2
					closestLaneXPoint=x2

				#closestLaneXPoint = np.min([m,x1,x2])
			laneXOffset = float((closestLaneXPoint-self.frameWidthMidpoint)/self.frameWidthMidpoint)
			closestLaneXPoint = float(closestLaneXPoint/(self.frameWidthMidpoint))
			#print 'Lane X-Offset:',laneXOffset,'Lane X-Position',closestLaneXPoint
		else:
			laneXOffset = None
			closestLaneXPoint = None
		return laneXOffset,closestLaneXPoint


	def control_steering_single_point_proportional(self, laneXOffset,LaneXPoint):
		# make base = 0 :
		# if -5 >distance > 5 go forward
		filterControlBounds = lambda x: np.max([12,np.min([x,60])])
		base = 0
		baseForward = 30
		if laneXOffset is not None:
			laneXOffset = laneXOffset * 100
			absoluteLaneXOffset = laneXOffset * np.sign(laneXOffset)
			if absoluteLaneXOffset < 50:
				if laneXOffset<0:
					ctrl = (filterControlBounds(baseForward-absoluteLaneXOffset),filterControlBounds(baseForward+absoluteLaneXOffset),18)
					#print 'FORWARD SLIGHT CORRECTION LEFT'
				elif laneXOffset>0:
					ctrl = (filterControlBounds(baseForward+absoluteLaneXOffset),filterControlBounds(baseForward-absoluteLaneXOffset),18)
					#print 'FORWARD SLIGHT CORRECTION RIGHT'
				else:
					ctrl = (filterControlBounds(baseForward),filterControlBounds(baseForward),25)
					#print 'FORWARD'
			elif laneXOffset < 0:
				ctrl = (filterControlBounds(base-0.75*absoluteLaneXOffset),filterControlBounds(base+0.75*absoluteLaneXOffset),19)
				#print 'TURNING LEFT'
			else:
				ctrl = (filterControlBounds(base+0.75*absoluteLaneXOffset),filterControlBounds(base-0.75*absoluteLaneXOffset),19)
				#print 'TURNING RIGHT'
			#laneXOffset = laneXOffset/3
			#laneXOffset can be escalated
			#laneXOffset = 2*laneXOffset
			#ctrl = (filterControlBounds(base-laneXOffset),filterControlBounds(base+laneXOffset))
		
		else:
			if np.abs(self.lastLanePosition)<30:
				ctrl = (filterControlBounds(50),filterControlBounds(50),15)
				#print 'FORWARD WITH NO LINE'

			elif self.lastLanePosition < 0:
				ctrl = (filterControlBounds(-50),filterControlBounds(50),15)
				#print 'LOOKING FOR LINE ON THE LEFT SIDE'
				laneXOffset=self.lastLanePosition
			else:
				ctrl = (filterControlBounds(50),filterControlBounds(-50),15)
				#print 'LOOKING FOR LINE ON THE RIGHT SIDE'
			laneXOffset = self.lastLanePosition
		self.lastLanePosition = laneXOffset
		return ctrl


	def findLines(self, image, mode, WN):
		""" After trimming the frame, removes all but the white sections (lines), then applies some erosion to thinner the lines.
		Then the Lines are obtained by using HoughLines. Parameter extraction from the closest point and it's offset by using getControlParameters
		function. Using then the reference to control the vehicle. 
		"""
		frame = image[self.top:self.bottom,:]
		iFilter = self.filterByColour(frame)
		iGrey = cv2.cvtColor(iFilter, cv2.COLOR_BGR2GRAY)
		iErode = cv2.erode(iGrey,self.kernels['erode'],1) 
		lines = cv2.HoughLinesP(iErode,self.hough['rho'],self.hough['theta'], self.hough['threshold'],self.hough['minLineLength'],self.hough['maxLineGap'])
		laneXOffset,laneXpoint =  self.getControlParameters(lines)
		#ctrl = self.control_steering_single_point_proportional(laneXOffset,laneXpoint)
		if laneXpoint is None:
			if not self.car.getControl():
				self.geo.motion(0,0)
			else:
				if self.lastLaneXpoint is not None:
					laneXpoint = self.lastLaneXpoint
		if laneXpoint is not None:
			x = int(laneXpoint * 100 - 100)
			self.error += x**2
			self.n = self.n+1
			ctrl = [self.car.kinematics.LinearSpeedToDutyCycle(e) for e in self.car.kinematics.getLinearSpeed(int(x),self.car.kinematics.YPos)]
			(l,r) = ctrl
			l = max(-100,min(int(l),100))
			r = max(-100,min(int(r),100))
			#print 'From X Point:',x,':',l,r
			if self.car.getControl():
				self.geo.motion(l,r)
			else:
				self.geo.motion(0,0)
			self.lastLaneXpoint = laneXpoint
			if self.n%100==0:
				print 'Error cuad. Absoluto:',self.error,'. medio: ',self.error/self.n,'pix.'
		
			
			#self.geo.motion(0,0)
		#cv2.imshow(WN,eval(mode))
