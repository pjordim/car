import numpy as np, cv2.cv as cv
import BlobDetector, cv2
from BlobDetector import *
from Colour import *

class TrafficLightDetector:
	def __init__(self,car,control,controlIndex,blobDetector,kernel, lowTrafficLight, upTrafficLight):
		self.car = car
		self.control = control
		self.controlIndex = controlIndex
		#self.res = res
		self.blobDetector = blobDetector
		self.kernel = kernel 
		self.lowTrafficLight = lowTrafficLight
		self.upTrafficLight = upTrafficLight

	##TrafficLight(res, setBlobDetector(),np.ones((3,3),np.uint8),np.array([244,124,119]),np.array([255,133,137]))


	def detectTrafficLight(self,frame):
		try:
			"""Detects trafficlights by checking the hotspots in LAB colourspace"""
			#Better if frame gets trimmed before being passed to detectTrafficLight
			#frame = frame[int(0.3*self.res[1]):int(0.6*self.res[1]),int(0.3*self.res[0]):int(0.6*self.res[0])]
			#denoised = cv2.filter2D(frame, -1, kernel)
			lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
			maskTL = cv2.inRange(lab, self.lowTrafficLight, self.upTrafficLight)
			maskedTL = cv2.bitwise_and(frame,frame, mask=maskTL)
			#GreenClosed = cv2.morphologyEx(resGreen,cv2.MORPH_OPEN,kernel)
			#TLDilate = cv2.dilate(maskedTL, np.ones((2,2),np.uint8))
			_,TLThresh = cv2.threshold(maskedTL,127,255,cv2.THRESH_BINARY_INV)
			TLBlobs = getBlobs(TLThresh,self.blobDetector)
			colour = []
			for blob in TLBlobs:
				x,y = map(int,blob.pt)
				colour.append(averageColour(frame,x,y))
				#print blob.pt, blob.size, blob.angle, blob.response
				#print x,y,'::',frame[y][x],'::',lab[y][x]
				#print frame[y][x]
			blobImg = drawBlobs(frame,TLBlobs,(255,0,0))	
			#cv2.imshow('TrafficLight Blobs',blobImg)	
			return blobImg,colour 
		except ValueError:
			print 'Point position out of bounds'
