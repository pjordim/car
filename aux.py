import cv2,numpy as np,RPi.GPIO as GPIO
from picamera import PiCamera

M1a = 16  #black
M1b = 20  #white
M1e = 21  #black 
M2a = 13  #grey
M2b = 19   #purple
M2e = 26 #brown
M3a = 23   #orange
M3b = 24  #yellow
M3e = 25 #purple
M4a = 22   #green
M4b = 27  #blue
M4e = 17 #red
#Equalization
def equalize(image):
	return cv2.equalizeHist(image)

def clahe(image,clipLimit = 2.0, tileGridSize = (8,8)):
	#Local equalization (contrast limited adaptative histogram equalization)
	clahe = cv2.createCLAHE(clipLimit, tileGridSize)
	return clahe.apply(image)

#Colour for points
def inverseColour (c):	
	#Given a colour in three RGB values, returns the opposite 1-R,1-G,1-B
	return (255 - c[0], 255 - c[1], 255 - c[2])
#Filters,transformation and processing
def filterByColour (image,lowerFilter,upperFilter):
	hsv = cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
	#hsv[0] = equalize(hsv[0])
	
	mask = cv2.inRange(hsv,lowerFilter,upperFilter)
	return cv2.bitwise_and(image,image,mask=mask)

def dilate (image,kernel): #denoiseKernel
	return cv2.dilate(image,kernel,iterations=1)

def erode (image,kernel,iterations): #wholeKernel
	return cv2.erode(image,kernel,iterations=iterations)

def denoise(image,kernel): #denoiseKernel
	return cv2.filter2D(image, -1, denoiseKernel)

def sobel(image,xorder = 0, yorder=1, ksize = 5):
	return cv2.Sobel(image, cv2.CV_8U,xorder,yorder,ksize)

def canny(image, sigma = 0.5):
	v = np.median(image)
	l = int(max(0,(1.0-sigma) * v ))
	u = int(min(255, (1.0 + sigma) * v ))
	return cv2.Canny(image,l, u)
	#return cv2.Canny(image,100, 150)

def hough(image,rho = 1,theta = np.deg2rad(1), threshold = 100):
	blank = np.zeros((len(image),len(image[0])),np.uint8)
	lines = cv2.HoughLines(image,rho, theta, threshold)
	if lines != None:
		for rho,theta in lines[0]:
			a = np.cos(theta)
			b = np.sin(theta)
			x0 = a*rho
			y0 = b*rho
			x1 = int(x0 + 1000*(-b))
			y1 = int(y0 + 1000*(a))
			x2 = int(x0 - 1000*(-b))
			y2 = int(y0 - 1000*(a))
			cv2.line(blank,(x1,y1),(x2,y2),(255,255,255),2)
			#cv2.imwrite('houghlines3.jpg',img)
	return blank

#image,rho = 1,theta = np.deg2rad(1), threshold = 20,minLineLength = 30, maxLineGap = 5
def probabilistic_hough(image,rho,theta,threshold,minLineLength,maxLineGap):
	lines = cv2.HoughLinesP(image,rho, theta, threshold,minLineLength,maxLineGap)
	return lines, (len(image),len(image[0]))

def hough_correction_angle(image,rho = 1,theta = np.deg2rad(1), threshold = 1,minLineLenght = 5, maxLineGap = 20):
	lines = cv2.HoughLinesP(image,rho, theta, threshold,minLineLenght,maxLineGap)
	midpoint = len(image)/2
	if lines != None:
		for x1,y1,x2,y2 in lines[0]:
			a1 = angle(x1,y1,x2,y2)
			#print a1
			#correction()

def angle(x0,y0,x1,y1,forwardAngle):
	#forwardAngle is arctan(forwardAngle)
	return np.arctan2(y1-y0,x1-x0)-forwardAngle
#	if x1==x0:
#		return ninety
#	else:
#		return np.arctan((y1-y0)/(x1-x0))

def GPIOsetup():
	GPIO.setmode(GPIO.BCM)
	freq = 10
	M1a = 16  #black
	M1b = 20  #white
	M1e = 21  #black 
	M2a = 13  #grey
	M2b = 19   #purple
	M2e = 26 #brown
	M3a = 23   #orange
	M3b = 24  #yellow
	M3e = 25 #purple
	M4a = 22   #green
	M4b = 27  #blue
	M4e = 17 #red
	GPIO.setup((M1a,M1b,M1e), GPIO.OUT)
	GPIO.setup((M2a,M2b,M2e), GPIO.OUT)
	GPIO.setup((M3a,M3b,M3e), GPIO.OUT)
	GPIO.setup((M4a,M4b,M4e), GPIO.OUT)

	en1 = GPIO.PWM(M1e,freq)
	en2 = GPIO.PWM(M2e,freq)
	en3 = GPIO.PWM(M3e,freq)
	en4 = GPIO.PWM(M4e,freq)

	GPIO.output((M1e,M2e,M3e,M4e), GPIO.HIGH)

	en1.start(0.0)
	en2.start(0.0)
	en3.start(0.0)
	en4.start(0.0)
	return (freq, M1a,M1b,M1e,M2a,M2b,M2e,M3a,M3b,M4e,en1,en2,en3,en4)

def motion(y1,y2,control,GPIOparams,maxcontrol = 12):
	(freq, M1a,M1b,M1e,M2a,M2b,M2e,M3a,M3b,M4e,en1,en2,en3,en4) = GPIOparams
	if not control:
		GPIO.output([M2a,M2b,M4a,M4b], GPIO.LOW)
		en1.ChangeDutyCycle(0)
		en2.ChangeDutyCycle(0)
		en3.ChangeDutyCycle(0)
		en4.ChangeDutyCycle(0)
		return
	else:	
		if y1>0:
			# Forward motion
			GPIO.output(M1b, GPIO.LOW)
			GPIO.output(M1a, GPIO.HIGH)
			GPIO.output(M3b, GPIO.LOW)
			GPIO.output(M3a, GPIO.HIGH)
		elif y1<0:
			# Backward motion
			GPIO.output(M1a, GPIO.LOW)
			GPIO.output(M1b, GPIO.HIGH)
			GPIO.output(M3a, GPIO.LOW)
			GPIO.output(M3b, GPIO.HIGH)
			y1=y1*-1
		else:
			GPIO.output([M1a,M1b,M3a,M3b], GPIO.LOW)
		if y2>0:
			# Forward motion
			GPIO.output(M2a, GPIO.HIGH)
			GPIO.output(M2b, GPIO.LOW)
			GPIO.output(M4a, GPIO.HIGH)
			GPIO.output(M4b, GPIO.LOW)
		elif y2<0:
			# Backward motion
			GPIO.output(M2b, GPIO.HIGH)
			GPIO.output(M2a, GPIO.LOW)
			GPIO.output(M4b, GPIO.HIGH)
			GPIO.output(M4a, GPIO.LOW)
			y2=y2*-1
		else:
			GPIO.output([M2a,M2b,M4a,M4b], GPIO.LOW)
		#print(y1,y2)
		left_axis = np.max([0,np.min([1,y1])]) * maxcontrol
		right_axis= np.max([0,np.min([1,y2])]) * maxcontrol
		#print(y1,y2,left_axis, right_axis)
		en1.ChangeDutyCycle(left_axis)
		en2.ChangeDutyCycle(right_axis)
		en3.ChangeDutyCycle(left_axis)
		en4.ChangeDutyCycle(right_axis)

def cameraSetup(res,fps,hf,vf,mode):
	camera = PiCamera()
	camera.resolution = res
	camera.framerate = fps
	camera.hflip = hf
	camera.vflip = vf
	#camera.iso = 0
	camera.meter_mode = mode
	return camera
		