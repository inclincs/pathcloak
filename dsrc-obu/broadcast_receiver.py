import time
import json
import threading
import socket

from screen import Screen



class BroadcastAcceptor(threading.Thread):

	def __init__(self, core, port):
		super().__init__()

		self.core = core

		self.acceptor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.acceptor.bind(('', port))
		self.acceptor.listen(5)


	def run(self):
		try:
			while True:
				client, address = self.acceptor.accept()

				BroadcastReceiver(self.core, client).start()
		except KeyboardInterrupt:
			print('digest server end')
			exit(0)

		


class BroadcastReceiver(threading.Thread):

	def __init__(self, core, client):
		super().__init__()

		self.core = core

		self.client = client

		self.data = ''

		self.try_count = 0

		self.rx_slot = []


	def run(self):
		while True:
			data = self.client.recv(1024)
			if data == None or len(data) == 0: break

			self.data += data.decode().replace('\0', '')
			

			temp = self.data.split('}')
			self.data = temp[-1]
			
			raws = [ t + '}' for t in temp[:-1] ]
			for raw in raws:
				self.core.log('rx|{vid}|{time}|{message}\n'.format(vid=self.core.id, time=time.time(), message=raw))
				message = json.loads(raw)

				if 'location' in message:
					Screen.clear_line(22)
					print('distance:', Location.fromString(message['location']) >> self.core.self.location)

				t_current = time.time()
				self.core.waiting_slot = [ w for w in self.core.waiting_slot if w[1] + 1 > t_current ]
				# Screen.clear_line(22)
				# print(self.core.waiting_slot)

				self.rx_slot.append(time.time())
				if len(self.rx_slot) > 5: self.rx_slot = self.rx_slot[1:]
				
				if len(self.rx_slot) < 5 or self.rx_slot[-1] - self.rx_slot[0] > 1: continue
				# Screen.clear_line(22)
				# print(self.rx_slot)

				if 'try_count' in message:
					if int(message['try_count']) <= self.try_count:
						continue
					else:
						self.try_count = int(message['try_count'])

				if 'speed' in message and float(message['speed']) < self.core.min_speed / 3600: continue
				
				with self.core.lock:
					self.core.request(message)

		self.client.close()