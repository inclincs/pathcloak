import time

from gps import Location, Time
from obu import OBU
from producer import Producer




class GPSReceiver:

	def __init__(self, gps):
		self.gps = gps


	def request(self, message=None):
		flag = {
			'time': True if message == None or message == 'time' else False,
			'location': True if message == None or message == 'location' else False
		}



		if type(self.gps) == OBU:
			obu = self.gps

			if obu.socket:
				if not obu.send('time location'): raise Exception('obu send error')
				data = obu.recv(1024)
				if data:
					global_time, latitude, longitude = map(float, data.decode().strip('\0').split(','))
					return Time(global_time) if flag['time'] else None, Location(latitude, longitude) if flag['location'] else None



		elif type(self.gps) == Producer:
			producer = self.gps

			return Time(time.time(), local=True) if flag['time'] else None, Location(*producer.get()) if flag['location'] else None
		


		return None, None