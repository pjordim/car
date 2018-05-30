"""@package I2C
Allows communcation by using I2C (Inter-Integrated Circuit)
"""
import smbus
import time

class I2C:
	
	def init(self,bus = smbus.SMBus(0), address = 0x70):
		self.bus = bus
		self.address = address


	def write(self,offset,value):
		self.bus.write_byte_data(self.address, offset, value)
		return -1

	def read(self,address, offset):
		lecture = self.bus.read_byte_data(address, offset)
		return lecture

