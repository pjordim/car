import time 

class PID:
	__init__(self,kp,kd,ki):
		self.kp = kp
		self.kd = kd
		self.ki = ki
		self.prev_error = 0
		self.integral = 0
		self._t


	getOutput(self, setPoint, measuredPoint):
		t = time.time()
		dt = t - self._t
		error = setPoint - measuredPoint
		self.integral = self.integral + (error * dt)
		derivative = (error-self.prev_error)/dt
		output = self.kp * error + self.ki *self.integral + self.kd * derivative
		self.prev_error = error
		self._t = t
		return output


	getGains(self):
		return kp,kd,ki