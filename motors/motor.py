import RPi.GPIO as GPIO

class motor:
	"""Defines a motor pinout and provides a clear interface for controling motors by using PWM
	"""
	def __init__(self, enable, a, b,freq = 10):
		if GPIO.getmode() is not 11:
			GPIO.setmode(GPIO.BCM)
		GPIO.setup((enable,a,b), GPIO.OUT)
		self.a = a
		self.b = b
		self.enable = enable
		self.freq = freq
		self.pwm = GPIO.PWM(self.enable,self.freq)
		self.pwm.start(0)


	def changeFreq(self, freq):
		"""Changes the PWM frequency
		"""
		self.freq = freq
		self.pwm.ChangeFrequency(freq)


	def stop(self):
		"""Stops the PWM and destroys the pwm container
		"""
		self.pwm.stop()


	def forward(self, dutycycle):
		"""Clockwise rotation with the given dutycycle
		"""
		GPIO.output(self.a,GPIO.HIGH)
		GPIO.output(self.b,GPIO.LOW)
		self.pwm.ChangeDutyCycle(dutycycle)


	def backward(self, dutycycle):
		"""Counterclokwise rotation with the given dutycycle
		"""
		GPIO.output(self.a,GPIO.LOW)
		GPIO.output(self.b,GPIO.HIGH)
		self.pwm.ChangeDutyCycle(dutycycle)

	
	def brake(self):
		"""The motor brakes immediatly. Idle it's recommended better.
		"""
		self.pwm.ChangeDutyCycle(100)
		GPIO.output(self.a,GPIO.LOW)
		GPIO.output(self.b,GPIO.LOW)
		

	def idle(self):		
		"""Lets the motor free, stoping smoothly
		"""
		self.pwm.ChangeDutyCycle(0)
		GPIO.output(self.a,GPIO.LOW)
		GPIO.output(self.b,GPIO.LOW)