class Timer:

	def __init__(self, target, interval, time_func, sleep_func):
		self.start_time = time_func()
		self.end_time = self.start_time + target if target else None
		self.intermediate_time = self.start_time + interval
		self.interval = interval
		self.time_func = time_func
		self.sleep_func = sleep_func

	def __iter__(self):
		self.intermediate_time = self.start_time + self.interval
		
		return self

	def __next__(self):
		if self.expired(): raise StopIteration()
		while not self.update():
			self.sleep_func(self.intermediate_time - self.time_func())
		return self.time_func() - self.start_time


	def update(self):
		if self.time_func() > self.intermediate_time:
			self.intermediate_time += self.interval
			return True
		return False

	def expired(self):
		return self.end_time and (self.end_time == self.start_time or self.end_time < self.intermediate_time)