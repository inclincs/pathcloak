class EntityException(Exception): pass

class Entity:

	def __init__(self, id=None, path=None, location=None, prev_location=None, speed=None):
		self.id = id
		self.path = path
		self.location = location
		self.prev_location = prev_location
		self.speed = speed