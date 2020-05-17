import math



class Vector:

	class Element:

		def __init__(self, index):
			self.index = index

		def __get__(self, instance, cls):
			return instance.get(self.index)

		def __set__(self, instance, value):
			instance.set(self.index, value)

	def __init__(self, *args):
		self.__elements = list(args)

	def __repr__(self):
		return repr(self.__elements)

	def __getitem__(self, item):
		return self.__elements[item]

	def __setitem__(self, item, value):
		self.__elements[item] = value

	get, set = __getitem__, __setitem__

	def __len__(self):
		return len(self.__elements)

	def __add__(self, other):
		if len(self.__elements) != len(other): raise ValueError
		return self.__class__(*[ self.__elements[i] + other[i] for i in range(len(self.__elements)) ])

	def __sub__(self, other):
		if len(self.__elements) != len(other): raise ValueError
		return self.__class__(*[ self.__elements[i] - other[i] for i in range(len(self.__elements)) ])

	def __mul__(self, other):
		if type(other) == int or type(other) == float:
			other = [ other ] * len(self.__elements)
			return self.__class__(*[ self.__elements[i] * other[i] for i in range(len(self.__elements)) ])
		elif len(self.__elements) != len(other): raise ValueError
		return sum([ self.__elements[i] * other[i] for i in range(len(self.__elements)) ])

	__rmul__ = __mul__

	def __truediv__(self, other):
		if type(other) == int or type(other) == float:
			other = [ other ] * len(self.__elements)
		elif len(self.__elements) != len(other): raise ValueError
		return self.__class__(*[ self.__elements[i] / other[i] for i in range(len(self.__elements)) ])

	def __eq__(self, other):
		if other == None: return False
		elif len(self.__elements) != len(other): raise ValueError
		for i in range(len(self.__elements)):
			if self.__elements[i] != other[i]:
				return False
		return True

	def __ne__(self, other):
		if other == None: return True
		elif len(self.__elements) != len(other): raise ValueError
		for i in range(len(self.__elements)):
			if self.__elements[i] != other[i]:
				return True
		return False

	def __reversed__(self):
		return self.__class__(*self.__elements[::-1])
	
	__invert__ = __reversed__

	def __lshift__(self, other):
		if len(self.__elements) != len(other): raise ValueError
		result = 0
		for i in range(len(self.__elements)):
			result += (self.__elements[i] - other[i]) ** 2
		return math.sqrt(result)

	__rshift__ = __lshift__