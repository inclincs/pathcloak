import time
import json
import threading

from screen import Screen



class BroadcastSender(threading.Thread):

	def __init__(self, core, obu):
		super().__init__()

		self.core = core

		self.obu = obu

		self.message = None
		self.broadcast = None

		self.info_line = 0

		self.try_count = 0


	def run(self):
		while True:
			self.time = time.time()
			if self.core.queue.qsize() > 0:
				self.message = self.core.queue.get()
				refresh = True
			else:
				refresh = False
			
			message = self.message

			if message == None:
				time.sleep(0)
				continue


			self.broadcast = { 'type': message[0], 'id': message[1] }


			# Info
			if refresh:
				Screen.clear_line(self.info_line + 10)
				self.info_line = (self.info_line + 1) % 5
				print('[ Send ] ({time:.2f}) {type:<9} '.format(time=time.time() - self.core.t_start, type=self.broadcast['type'].upper()), end='')


			if message[0] == 'broadcast':
				self.broadcast.update({
					'location': str(self.core.self.location),
					'prev_location': str(self.core.self.prev_location),
					'speed': '{:.5f}'.format(self.core.self.speed)
				})
				if refresh: print('id: {id}, location: {l}, speed: {s:.1f} m/s {s2:.1f} km/h'.format(id=message[1], l=self.core.self.location, s=self.core.self.speed * 1000, s2=self.core.self.speed * 3600))
			elif message[0] == 'try':
				if refresh: self.try_count += 1
				self.broadcast.update({
					'pid': message[2],
					'location': str(message[3]),
					'prev_location': str(message[4]),
					'speed': '{:.5f}'.format(message[5]),
					'try_count': '{}'.format(self.try_count)
				})
				if refresh: print('id: {id}, pid: {pid}, location: {l}, speed: {s:.1f} m/s {s2:.1f} km/h'.format(id=message[1], pid=message[2], l=message[3], s=message[5] * 1000, s2=message[5] * 3600))
			elif message[0] == 'paired':
				self.broadcast.update({
					'pid': message[2],
					'whether': message[3]
				})
				if refresh: print('id: {id}, pid: {pid}, pairing?: {whether}'.format(id=message[1], pid=message[2], whether=message[3]))
			else:
				continue


			raw = json.dumps(self.broadcast, sort_keys=True)

			# TX
			self.obu.send('broadcast{message}'.format(message=raw))

			if message[0] == 'paired' and message[3] == False:
				time.sleep(0.1)

			# Log
			if refresh:
				self.core.log('tx|{vid}|{time}|{message}\n'.format(vid=self.core.id, time=time.time(), message=raw))


			time.sleep(0.02) # 0.03
