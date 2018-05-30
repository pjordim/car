from __future__ import print_function
import threading, Queue, time, thread, cv2,sys, numpy as np
from picamera.array import PiRGBArray
from picamera import PiCamera, exc
import picamera
from GraphicProcessing.GraphicProcessing import GraphicProcessing
from Control import DistanceControl

#Must check how CameraControl handles control boolean
#Implement a ctrl list for TrafficLight and LineMissing
class CameraControl:


	def __init__(self, car, control,controlIndex, distanceControl, trafficlightDetector, res, fps, hf, vf, mode, agent):
		self.control = control
		self.controlIndex = controlIndex
		self.distanceControl = distanceControl
		self.trafficlightDetector = trafficlightDetector
		self.car = car
		self.carControl = car.getControl()
		self.geo = car.getGeo()
		self.res = res
		self.fps = fps
		self.cam = None
		self.cameraSetup( hf, vf, mode)
		self.agent = agent
		self.prevColourList = []

		#UI modes
		self.modes = ['frame','iFilter','iGrey','iErode']
		self.disp = 0
		self.mode = self.modes[self.disp]
		#UI related
		self.WN = 'window name'
		#Video Frame Buffer
		self.bufferLength = 5
		self.imageBuffer = []
		self.imageBufferSetup()
		#Threads
		self.threads = []
		self.i = 0
		self.ThreadsSetup()
		#self.ThreadsStart()
		#self.ThreadsJoin()

			
	def cameraSetup(self,hf,vf,mode):
		try:
			self.cam = PiCamera()
			self.cam.resolution = self.res
			self.cam.framerate = self.fps
			self.cam.hflip = hf
			self.cam.vflip = vf
			self.cam.meter_mode = mode
                        self.rawCapture = PiRGBArray(self.cam, size=(320, 240))
		except picamera.exc.PiCameraMMALError:
			print ('Camera MMAL operation fails for whatever reason.')
			if self.cam is not None:
				self.cam.close()
			sys.exit()
		except:
			if self.cam is not None:
				self.cam.close()
			thread.exit()


	def ThreadsSetup(self):
		self.readyEvent = threading.Event()
		self.readyEvent2 = threading.Event()
		self.closingEvent = threading.Event() # Closing event can be avoided by making the threads daemonic
		self.threads.append(threading.Thread(target=self.getFrame, args=()))
		self.threads.append(threading.Thread(target=self.LaneControl, args=()))
		#self.threads.append(threading.Thread(target=self.detectTrafficLights, args=()))
		self.threads.append(threading.Thread(target=self.distanceControl.CheckDistances,args=(self.closingEvent,)))
		#self.threads.append(threading.Thread(target=self.trafficlightDetector.detectTrafficLight, args = (frame,self.closingEvent)))
		

	def ThreadsStart(self):
		for thread in self.threads:
			thread.start()

		
	def ThreadsJoin(self):
		try:
			for thread in self.threads:
				thread.join()
				print('A thread exited!')
		except RuntimeError:
			print ('Exited successfully!')
		except:
			print('Exception on ThreadsJoin in CameraControl')
			raise


	def ChangeDisp(self, disp):
		self.disp = disp
		self.mode  = self.modes[self.disp]


	def imageBufferSetup(self):
		for i in range(self.bufferLength):
			self.imageBuffer.append([])

	
	def getFrame(self):
		try:
                        print("getframe")
			#stime = time.time()
			#frames = 0
			for frame in self.cam.capture_continuous(self.rawCapture, format="bgr",use_video_port=True):
				self.rawCapture.truncate(0)
				if self.closingEvent.isSet():
					print ("Aborting getFrame thread!")
					thread.exit()
					#return
				self.imageBuffer[self.i] = frame.array
				self.i = (self.i+1)%self.bufferLength
				self.readyEvent.set()
				self.readyEvent2.set()
				#findLines(image,UseGUI,self.control,GPIOparams)
				#frames = frames + 1
				#fps = frames/(time.time() - stime)
				#print int(fps), ' fps'
		except SystemExit:
                        print("getframe2")
			self.cam.close()
			pass
		except:
			print('>> Uncaught exception on getFrame. Cleaning before exit')
			self.rawCapture.truncate(0)
			self.cam.close()
			self.closingEvent.set()
			print('>> Everything is closed. See you next time!')
			raise


	def LaneControl(self):
		"""Called once, stays active till exception or close key pressed. Setting up the UI first.
		 Then detects a ready event in a loop and finds the lines which are applied to the car control. """
		try:
			disp = 0
			cv2.namedWindow(self.WN,cv2.WINDOW_NORMAL)
			cv2.resizeWindow(self.WN,self.res[0],self.res[1])
			cv2.moveWindow(self.WN, 200, 200)
			cv2.createTrackbar('DispMode',self.WN,self.disp,len(self.modes)-1,self.ChangeDisp)
			CloseKey = ord("q")
			ControlKey = ord("c")
			gp = GraphicProcessing(self.geo, self.car, self.res)
			startTime = time.time()
			processedFrames = 0
			while not self.closingEvent.isSet():
				self.readyEvent.wait(0.5)
				if self.readyEvent.isSet():
					image = self.imageBuffer[(self.i-1)%self.bufferLength]
					gp.findLines(image, self.mode, self.WN)
					processedFrames = processedFrames + 1
					#print (int(processedFrames/(time.time() - startTime)) , 'processed fps', end ='\r')
					cv2.imshow(self.WN,image)
					key = cv2.waitKey(1)&0xFF
					self.readyEvent.clear()
					if key != 255:
						if key == CloseKey:
							print ('Aborting LaneControl thread!')
							self.closingEvent.set()
							cv2.destroyAllWindows()
							self.car.geo.motion(0,0)
							thread.exit()
							#break
						elif key == ControlKey:
							self.control = self.car.changeControl(self.controlIndex)
							print ('Control changed to', self.control,'Global control:', self.car.getControls())
			else:
				print ('Aborting LaneControl thread!')
				cv2.destroyAllWindows()
				self.car.geo.motion(0,0)
				thread.exit()
				
		except SystemExit:
			pass
		except:
			print ('Uncaught Exception on LaneControl thread')
			self.closingEvent.set()
			cv2.destroyAllWindows()
			self.car.geo.motion(0,0)
			raise


	def detectTrafficLights(self):
		#NEED TO CHECK ARGS AND MAYBE MOVE TO IT'S OWN CLASS
		try:
			# cv2.namedWindow('Trafficlight Detector',cv2.WINDOW_NORMAL)
			# cv2.resizeWindow('Trafficlight Detector',self.res[0],self.res[1])
			# cv2.moveWindow('Trafficlight Detector', 200, 200)	
			while not self.closingEvent.isSet():
				self.readyEvent2.wait(0.1)
				if self.readyEvent2.isSet():
					image = self.imageBuffer[(self.i-1)%self.bufferLength]
					frame = image[int(0.2*self.res[1]):int(1*self.res[1]),:]#int(0.2*self.res[0]):int(0.8*self.res[0])] 
					img, colourList = self.trafficlightDetector.detectTrafficLight(frame)
					if colourList is not None:
						#processedFrames = processedFrames + 1
						#print (int(processedFrames/(time.time() - startTime)) , 'processed fps', end ='\r')
						#cv2.imshow('TrafficLight',img)
						if 'RED' in colourList: #and 'RED' not in self.prevColourList:
							#self.agent.sendmsg()
							self.trafficlightDetector.control = self.car.setControl(self.trafficlightDetector.controlIndex,False)
							self.agent.sendChangeRequest()

							#print ('>Red Trafficlight detected. ChangePetition requested\n  Control changed to', self.trafficlightDetector.control,'.Global control:', self.car.getControls())
						
						# elif 'RED' in colourList or 'ORANGE' in colourList:
						# 	#self.agent.sendChangeRequest()
						# 	#self.agent.sendmsg()
						# 	self.trafficlightDetector.control = self.car.setControl(self.trafficlightDetector.controlIndex,False)
						# 	print ('>Red/Orange Trafficlight detected.\n  Control changed to', self.trafficlightDetector.control,'.Global control:', self.car.getControls())
						elif 'GREEN' in colourList:# and 'RED' not in colourList and 'ORANGE' not in colourList:
							#print ('>Green Trafficlight detected.\n  Control changed to', self.trafficlightDetector.control,'.Global control:', self.car.getControls())
							self.trafficlightDetector.control = self.car.setControl(self.trafficlightDetector.controlIndex,True)
						# elif 'RED' not in colourList and 'ORANGE' not in colourList:
						# 	print ('>Red and Orange Trafficlight not detected.\n  Control changed to', self.trafficlightDetector.control,'.Global control:', self.car.getControls())
						# 	self.trafficlightDetector.control = self.car.setControl(self.trafficlightDetector.controlIndex,True)
						elif 'RED' in self.prevColourList or 'ORANGE' in self.prevColourList:# and 'RED' not in colourList:
							#print ('>Red and Orange Trafficlight vanished away.\n  Control changed to', self.trafficlightDetector.control,'.Global control:', self.car.getControls())
							self.trafficlightDetector.control = self.car.setControl(self.trafficlightDetector.controlIndex,True)
					
						#cv2.imshow('TrafficLight',img)
						#cv2.waitKey(1)
						self.prevColourList = colourList[:]
					self.readyEvent2.clear()
			if self.closingEvent.isSet():
					print ('Aborting detectTrafficLights thread!')
					thread.exit()
					#cv2.destroyAllWindows()
					
		except SystemExit:
			pass
		except:
			print ('Uncaught Exception on detectTrafficLights')
			self.closingEvent.set()
			raise
			thread.exit()
			#cv2.destroyAllWindows()
