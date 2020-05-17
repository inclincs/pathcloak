import socket



class OBU:

	def __init__(self, ip, port):
		for _ in range(10):
			try:
				self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				self.socket.connect((ip, port))
				break
			except Exception as e:
				# print(e)
				self.socket = None
				time.sleep(0.5)

		self.connected = self.socket is not None



	def send(self, message):
		try:
			self.socket.send(message.encode('utf-8'))
		except:
			self.close()
			return False
		else:
			return True


	def recv(self, size):
		try:
			data = self.socket.recv(size)
			if data == None: self.close()
			return data
		except Exception as e:
			print(e)
			self.close()
			return None


	def close(self):
		try:
			self.socket.close()
		finally:
			self.socket = None


	def request(self, message):
		if not self.send(message): error('request send error')
		response = self.recv(1024)
		if response == None: error('request recv error')
		return response