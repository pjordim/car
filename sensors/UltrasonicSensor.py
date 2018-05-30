import RPi.GPIO as GPIO
import time
from scipy.stats import mode
import numpy as np
class UltrasonicSensor:
	"""Describes a ultrasonic sensor.Meant to be used with HCSR04 and HY-SRF05 ultrasound 
	ranging sensors. Contains the sensor pinout description. Creates events for detecting
	 echoes. Contains the last measured distance and the echo pulse starting moment 
	 (expressend in seconds)for distance calculation. 
	"""
	
	def receive_pulse(self,pin):
		"""Describes how to act in a echo pulse reception. Notifies when a pulse is detected out
		of time or while it's not expecting it.
		"""
		edge = GPIO.input(pin)
		t = time.time()
		if self.measuring:
			if edge: # Rising edge
				self.receiving_start_instant = t
				self.received_start_pulse = True
			elif not edge and self.received_start_pulse: # Falling edge
				self.distance = int((t - self.receiving_start_instant)*17000)
				self.measuring = False
		#else:
		#	print 'Echo signal received out of time!'


	def __init__(self,triggerPin,echoPin, waitingTime):
		"""Constructor method. Receives the pins and sets them up. Adds a
		event detection for detecting echoes. 
		"""
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(triggerPin,GPIO.OUT)
		GPIO.setup(echoPin,GPIO.IN,pull_up_down=GPIO.PUD_UP)
		self.trigger = triggerPin
		self.echo = echoPin
		self.receiving_start_instant = -1
		self.waitingTime = waitingTime
		GPIO.add_event_detect(echoPin,GPIO.BOTH,callback = self.receive_pulse)
		self.measuring = False
		#self.sending_instant = None
		self.received_start_pulse = False
		self.distance = -1


	def _send_pulse(self):
		"""Sends the trigger pulse to the sensor. It's meant to be used in the measure function.
		"""
		GPIO.output(self.trigger, False)
		time.sleep(0.00001)
		GPIO.output(self.trigger, True)
		time.sleep(0.00001)
		GPIO.output(self.trigger, False)
		#self.sending_instant = time.time()


	def measure(self):
		"""By using the _send_pulse method sets the sensor to measure distance. Waits for the
		 echo pulse 'waitingTime' seconds and returns -1 if it doesn't happen in the expected
		  time or the distance if it does.
		"""
		self._send_pulse()
		self.measuring = True
		time.sleep(self.waitingTime)
		if self.measuring: #If waiting for too long signal is missing
			self.distance = -1
			#self.sending_instant = -1
			self.receiving_start_instant = -1
			self.received_start_pulse = False
			return -1
		else:
			if self.distance < 3000 and self.distance > 5:
				return self.distance
			else:
				return -2
	

	def measure_burst(self,measurements,sleepTime):
		measures = []
		for i in range(measurements):
			m = self.measure()
			if m>0:
				measures.append(np.round(m))
			time.sleep(sleepTime)
		if len(measures) is not 0:
			return  mode(measures)[0][0]
		else:
			return -1