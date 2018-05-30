import thread
import time
class DistanceControl():
	def __init__(self, car,control, controlIndex, sensor, thresholdDistance):
		self.car = car
		self.control = control
		self.controlIndex = controlIndex
		self.sensor = sensor
		self.thresholdDistance = thresholdDistance

	def CheckDistances(self,closingEvent):
		try:
			while not closingEvent.isSet():
				distance = 1000
				time.sleep(1)
				distances = self.sensor.readline().split()[:2]
				for d in distances:
					#print ('Distance measured is ',d,'cm')
					if d > 0:
						distance = min(distance,d)
					#distance = min(distance,sensor.measure_burst(10,0.1))
					#distance = min(distance,sensor.measure())
                                        print("pues algo fa",d)
				if distance <= self.thresholdDistance:
					print 'Found a close obstacle in', distance, 'cm'
					self.control = self.car.setControl(self.controlIndex, False)
				else:
					self.control = self.car.setControl(self.controlIndex, True)
			else:
				print ('Aborting CheckDistances thread!')
				thread.exit()
				#return
		except SystemExit:
			pass
		except Exception as e:
                        print(e)
			print ('Exception caught on CheckDistances')
			closingEvent.set()
			thread.exit()
			raise
		

