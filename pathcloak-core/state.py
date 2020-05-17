class StateException( Exception ): pass

class State:

	def __init__(self, context):
		self.__context = context

	@property
	def context(self): return self.__context

	def request(self, *args, **kwargs): raise NotImplementedError

	def __eq__(self, other):
		if type(other) == str:
			return self.__class__.__name__.upper() == other.upper()
		else:
			return isinstance(self, other.__class__)

	def __repr__(self):
		return self.__class__.__name__


class StateContext:

	def __init__(self, state=None):
		self.__state = state

	@property
	def state(self):
		return self.__state

	@state.setter
	def state(self, value):
		if isinstance(value, State):
			self.__state = value
		else:
			raise StateException('not a State: {v}'.format(v=value))

	def request(self, *args, **kwargs):
		if self.__state != None:
			self.__state.request(*args, **kwargs)
