class NavigatorException(Exception): pass

class NavigationService:

	def request(self, start, waypoint, end):
		# input: start location, waypoint location, end location
		# output: list of location
		raise NotImplementedError

class Navigator:

	def __init__(self, service):
		self.service = service

	def request(self, start, waypoint, end):
		return self.service.request(start, waypoint, end)