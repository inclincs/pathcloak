class Screen:

	@staticmethod
	def clear_line(line=None, count=1):
		result = ''
		for i in range(count):
			if line: result += '\033[{};0H'.format(int(line) + count - 1 - i)
			result += '\033[K'
		print(result, end='')

	@staticmethod
	def clear():
		print('\033[2J', end='')

	@staticmethod
	def move(x, y):
		print('\033[{y};{x}H'.format(x=x, y=y), end='')