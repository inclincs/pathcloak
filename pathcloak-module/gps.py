import datetime
import geopy.distance

from vector import Vector



class Location( Vector ):

	def __init__(self, x, y):
		super().__init__(x, y)

	lat, lon = latitude, longitude = Vector.Element(0), Vector.Element(1)

	def __lshift__(self, other):
		return geopy.distance.vincenty((other.lat, other.lon), (self.lat, self.lon)).km

	def __rshift__(self, other):
		return geopy.distance.vincenty((self.lat, self.lon), (other.lat, other.lon)).km

	def __repr__(self):
		return '[{lat:.05f}, {lon:.05f}]'.format(lat=float(self.lat), lon=float(self.lon))

	@property
	def list(self):
		return [self.lat, self.lon]
	
	@property
	def string(self): return '{}, {}'.format(self.lat, self.lon)

	@property
	def copy(self): return Location(self.lat, self.lon)

	@staticmethod
	def fromString(string, reverse=False):
		return Location(*list(map(str.strip, string.strip('[]').split(',')))[::-1 if reverse else 1])



class Time:

	def __init__(self, time, local=False):
		if type(time) == str:
			time = float(time)
		elif type(time) == datetime:
			time = time.timestamp()
		elif type(time) == float:
			pass
		else:
			raise Exception('{time} is not available type:{type}'.format(time=time, type=type(time)))

		if local:
			self.l = time
		else:
			self.g = time


	@property
	def global_time(self): return self.__g

	@global_time.setter
	def global_time(self, value):
		self.__g = value
		self.__l = datetime.datetime.fromtimestamp(value).replace(tzinfo=datetime.timezone.utc).astimezone().timestamp()

	@property
	def g(self): return self.__g

	@g.setter
	def g(self, value):
		self.__g = value
		self.__l = datetime.datetime.fromtimestamp(value).replace(tzinfo=datetime.timezone.utc).astimezone().timestamp()
	
	@property
	def local_time(self): return self.__l

	@local_time.setter
	def local_time(self, value):
		self.__l = value
		self.__g = datetime.datetime.utcfromtimestamp(value).timestamp()

	@property
	def l(self): return self.__l

	@l.setter
	def l(self, value):
		self.__l = value
		self.__g = datetime.datetime.utcfromtimestamp(value).timestamp()

	def __repr__(self):
		return str(self.__g)

	def __eq__(self, other):
		return self.__g == other.g