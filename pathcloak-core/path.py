from gps import Location



class Path:

	def __init__(self, path, now=0):
		if len(path) < 2: raise Exception('path is very short: {}'.format(len(path)))
		
		self.__path = list(path) if type(path) == list else None
		self.now = now
		
		self.__distances = [ self.__path[i] >> self.__path[i + 1] for i in range(len(self.__path) - 1) ]
		self.__total_distance = 0
		for d in self.__distances: self.__total_distance += d
		self.__pair = [ (self.__path[i], self.__path[i + 1]) for i in range(len(self.__path) - 1) ]


	@property
	def now(self): return self.__now

	@now.setter
	def now(self, value): self.__now = 0 if int(value) < 0 else len(self.__path) - 1 if int(value) >= len(self.__path) else int(value)

	@property
	def distances(self): return self.__distances

	@property
	def total_distance(self): return self.__total_distance

	@property
	def pair(self): return self.__pair

	@property
	def copy(self): return Path(self.__path, self.__now)


	def approximate(self, location):
		l = location

		mi, mn, md = None, None, None
		for i, (pa, pb) in enumerate(self.__pair):
			
			n, d = None, None
			if pa == pb:
				n, d = pa, pa >> l
			else:
				b_a = pb - pa
				t = (l - pa) * b_a / (b_a * b_a)
				if t < 0:
					n, d  = pa, pa >> l
				elif t > 1:
					n, d  = pb, pb >> l
				else:
					n = pa + t * b_a
					d = n >> l

			if md == None or d < md:
				mi, mn, md = i, n, d

		return mi, mn, self.__path[mi] >> l


	def __lshift__(self, other): return self.approximate(other)
	
	def __abs__(self): return self.__path

	def __getitem__(self, index): return self.__path[index]

	def __repr__(self): return repr(self.__path)

	def __len__(self): return len(self.__path)