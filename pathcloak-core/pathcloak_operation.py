import time
import uuid
import queue, threading
import random
import requests

from screen import Screen
from graphhopper import Graphhopper
from gps import Location
from entity import Entity, EntityException
from path import Path
from navigator import Navigator, NavigatorException
from state import State, StateContext



class Broadcast(State):

	info_line = 0

	def generate_subpath(self, path, location, distance):
		now, start, _ = path.approximate(location)

		cum = -(path[now] >> start)
		for i, d in enumerate(path.distances[now:]):
			cum += d
			if cum > distance:
				r = cum - distance
				end = (path[now + i] * r + path[now + i + 1] * (d-r)) / d

				return Path([start] + path[now + 1:now + 1 + i] + [end])

		return None


	def request(self, *args, **kwargs):
		t_process = time.time()
		ctx = self.context


		m = message = args[0]


		if message['type'] == 'broadcast':


			pid = peer_id = m['id']
			pl = peer_location = Location.fromString(m['location'])
			ppl = peer_previous_location = Location.fromString(m['prev_location'])
			ps = peer_speed = float(m['speed'])

			if ps < 0.00001 or ctx.self.speed < 0.00001: return

			# Info
			Screen.clear_line(self.info_line + 16)
			self.info_line = (self.info_line + 1) % 5
			print('[ Receive ] ({time:.2f}) {type:<9} '.format(time=time.time() - ctx.t_start, type=m['type'].upper()), end='')
			print('상대: {pid:<}, 위치: {pl}, 속력: {ps:.1f} m/s {ps2:.1f} km/h'.format(pid=pid, pl=pl, ps=ps * 1000, ps2=ps * 3600))



			self_path = self.generate_subpath(ctx.path, ctx.self.location, ctx.time_threshold * ctx.self.speed)
			if self_path == None: return


			t_naviation = time.time()
			response = Navigator(Graphhopper()).request(ppl, pl, self_path[-1])
			t_naviation = time.time() - t_naviation
			if response == None: return
			Screen.clear_line(30)
			print('navi: {:.2f}ms'.format(t_naviation*1000))


			fake_path = Path(response)
			fake_distance = ctx.time_threshold * ps
			
			fd, margin = fake_path.total_distance, ctx.time_margin

			# Log
			ctx.log('condition|{vid}|{t}|{id}|{pid}|{s}|{w}|{e}|{p}|{path_distance}|{peer_speed}\n'.format(
				vid=ctx.id, id=ctx.self.id, pid=pid, t=time.time(), s=ppl, w=pl, e=self_path[-1], p=fake_path, path_distance=fake_path.total_distance, peer_speed=ps
			))

			# Screen.clear_line(23)
			# print('[ Condition ] {:.2f} < {:.2f} < {:.2f}'.format(fd / (ps * (1+margin)), ctx.time_threshold, fd / (ps * (1-margin))))

			if fake_distance * (1 - ctx.time_margin) < fake_path.total_distance < fake_distance * (1 + ctx.time_margin):
				ctx.timer = time.time()
				ctx.self.path = self_path
				ctx.peer = Entity(random.randint(0, 10000), fake_path, pl, ppl, ps)
				# READY state
				ctx.state = Ready(ctx)

				# TRY message
				ctx.queue.put(('try', ctx.self.id, pid, ctx.self.location, ctx.self.prev_location, ctx.self.speed))
			else:
				pass

			t_process=time.time() - t_process
			Screen.clear_line(31)
			print('process: {:.2f}ms, process-navi: {:.2f}ms'.format(t_process * 1000, (t_process - t_naviation) * 1000))


		elif message['type'] == 'try':


			pid = peer_id = m['id']
			id = self_id = m['pid']
			pl = peer_location = Location.fromString(m['location'])
			ppl = peer_previous_location = Location.fromString(m['prev_location'])
			ps = peer_speed = float(m['speed'])


			if ps < 0.00001 or ctx.self.speed < 0.00001: return

			
			# Info
			Screen.clear_line(self.info_line + 16)
			self.info_line = (self.info_line + 1) % 5
			print('[ Receive ] ({time:.2f}) {type} '.format(time=time.time() - ctx.t_start, type=m['type'].upper()), end='')
			if ctx.self.id != id: print('내꺼 아님 ', end='')
			print('상대방 id: {pid}, 위치: {pl}, 속력: {ps:.1f} m/s {ps2:.1f} km/h'.format(pid=pid, pl=pl, ps=ps * 1000, ps2=ps * 3600))

			if ctx.self.id != id: return

			self_path = self.generate_subpath(ctx.path, ctx.self.location, ctx.time_threshold * ctx.self.speed)
			if self_path == None: return


			response = Navigator(Graphhopper()).request(ppl, pl, self_path[-1])
			if response == None: return


			fake_path = Path(response)
			fake_distance = ctx.time_threshold * ps

			fd, margin = fake_path.total_distance, ctx.time_margin

			ctx.log('condition|{vid}|{t}|{id}|{pid}|{s}|{w}|{e}|{p}|{path_distance}|{peer_speed}\n'.format(
				vid=ctx.id, id=ctx.self.id, pid=pid, t=time.time(), s=ppl, w=pl, e=self_path[-1], p=fake_path, path_distance=fake_path.total_distance, peer_speed=ps
			))

			# Screen.clear_line(23)
			# print('[ Condition ] {:.2f} < {:.2f} < {:.2f}'.format(fd / (ps * (1+margin)), ctx.time_threshold, fd / (ps * (1-margin))))

			if fake_distance * (1 - ctx.time_margin) < fake_path.total_distance < fake_distance * (1 + ctx.time_margin):
				ctx.self.id = random.randint(0, 10000)
				ctx.self.path = self_path
				ctx.peer = Entity(random.randint(0, 10000), fake_path, pl, ppl, ps)
				# PAIR state
				ctx.state = Pair(ctx)

				# PAIRED message
				ctx.queue.put(('paired', ctx.self.id, pid, True))

				# Log
				ctx.log('pair|{vid}|{t}|{id}|{p}\n'.format(
					vid=ctx.id, id=ctx.self.id, t=time.time(), p=ctx.self.path
				))
			else:
				# PAIRED message
				ctx.queue.put(('paired', ctx.self.id, pid, False))
				# BROADCAST message
				ctx.queue.put(('broadcast', ctx.self.id))


		elif message['type'] == 'paired':
			if len(ctx.waiting_slot) == 0: return


			pid = peer_id = m['id']
			id = self_id = m['pid']
			whether = m['whether']




			if whether == True:
				for w in ctx.waiting_slot:
					if w[0][0] == id:
						ctx.self.path = w[0][1]
						ctx.peer = w[0][2]

						# Log
						ctx.log('accepted|{vid}|{t}|{id}\n'.format(
							vid=id, id=ctx.peer.id, t=time.time()
						))
						ctx.timer = None
						ctx.self.id = random.randint(0, 10000)
						# PAIR state
						ctx.state = Pair(ctx)

						# PAIRED message
						ctx.queue.put(('paired', ctx.self.id, pid, True))

						break
			else:
				ctx.waiting_slot = [ w for w in ctx.waiting_slot if w[0][0] != id ]


		


class Ready(State):

	info_line = 0

	def request(self, *args, **kwargs):
		ctx = self.context


		m = message = args[0]


		if message['type'] == 'try':


			pid = peer_id = m['id']
			id = self_id = m['pid']
			pl = peer_location = Location.fromString(m['location'])
			ppl = peer_previous_location = Location.fromString(m['prev_location'])
			ps = peer_speed = float(m['speed'])

			
			


			# Info
			Screen.clear_line(self.info_line + 16)
			self.info_line = (self.info_line + 1) % 5
			print('[ Receive ] ({time:.2f}) {type} '.format(time=time.time() - ctx.t_start, type=m['type'].upper()), end='')
			if ctx.self.id != id: print('내꺼 아님 ', end='')
			print('상대방 id: {pid}, 위치: {pl}, 속력: {ps:.1f} m/s {ps2:.1f} km/h'.format(pid=pid, pl=pl, ps=ps * 1000, ps2=ps * 3600))

			if ctx.self.id != id: return

			
			ctx.timer = None
			ctx.self.id = random.randint(0, 10000)
			# PAIR state
			ctx.state = Pair(ctx)

			# PAIRED message
			ctx.queue.put(('paired', ctx.self.id, pid, True))


		elif message['type'] == 'paired':


			pid = peer_id = m['id']
			id = self_id = m['pid']
			whether = m['whether']


			


			# Info
			Screen.clear_line(self.info_line + 16)
			self.info_line = (self.info_line + 1) % 5
			print('[ Receive ] ({time:.2f}) {type} '.format(time=time.time() - ctx.t_start, type=m['type'].upper()), end='')
			if ctx.self.id != id: return
			print('바뀐 상대방 id: {pid}, pairing 가능 여부: {whether}'.format(pid=pid, whether=whether))

			if ctx.self.id != id: return

			
			if whether == True:
				# Log
				ctx.log('accepted|{vid}|{t}|{id}\n'.format(
					vid=ctx.id, id=ctx.peer.id, t=time.time()
				))
				ctx.timer = None
				ctx.self.id = random.randint(0, 10000)
				# PAIR state
				ctx.state = Pair(ctx)

				# PAIRED message
				ctx.queue.put(('paired', ctx.self.id, pid, True))
			else:
				# Log
				ctx.log('rejected|{vid}|{t}|{id}\n'.format(
					vid=ctx.id, id=ctx.peer.id, t=time.time()
				))
				ctx.timer = None
				ctx.self.path = None
				ctx.peer = None
				# BROADCAST state
				ctx.state = Broadcast(ctx)

				# BROADCAST message
				ctx.queue.put(('broadcast', ctx.self.id))


class Pair(State):

	def request(self, *args, **kwargs): pass



class Core(StateContext):

	def __init__(self, id, navigation_info, log_file=None):
		super().__init__()
		
		self.id = id

		self.s, self.w, self.e, _ = navigation_info
		self.path = Path(navigation_info[-1])

		self.log_file = log_file

		self.t_start = None
		
		self.state = Broadcast(self)
		self.queue = queue.Queue()
		self.lock = threading.Lock()

		self.self = Entity(random.randint(0, 10000), None, self.s, self.s, 0)
		self.peer = None

		self.time_threshold = 30
		self.time_margin = 0.35

		self.timer = None

		self.log_queue = queue.Queue()

		self.waiting_slot = []
		

	def log(self, message):
		self.log_queue.put(message)
		if self.log_file:
			with open(self.log_file, 'a') as f:
				f.write(message)


	def start(self):
		# Start time
		self.t_start = time.time()

		# Log
		self.log('navigation|{vid}|{t}|{id}|{s}|{w}|{e}|{p}\n'.format(
			vid=self.id, id=self.self.id, t=time.time(), s=self.s, w=self.w, e=self.e, p=self.path
		))

		# Broadcast
		self.state = Broadcast(self)
		self.queue.put(('broadcast', self.self.id))
		

	def update(self, gps_time, gps_location):
		# Message (Real)
		messages = [ '{vid},{cid},{type},{t},{l},{s}'.format(vid=self.id, cid=self.self.id, type='real', t=gps_time, l=gps_location, s=self.self.speed) ]

		# Log
		self.log('vehicle|{vid}|{t}|{id}|{l}|{pl}|{s}\n'.format(
			vid=self.id, id=self.self.id, t=time.time(), l=self.self.location, pl=self.self.prev_location, s=self.self.speed
		))
		
		with self.lock:
			if self.state == 'PAIR':
				# Fake
				ratio = self.get_ratio(gps_location)

				Screen.clear_line(7)
				print('[ Fake ] ratio: {r}'.format(r=ratio))

				if ratio >= 1:
					self.self.id = random.randint(0, 10000)
					self.self.path = None
					self.peer = None
					# BROADCAST state
					self.state = Broadcast(self)
					# BROADCAST message
					self.queue.put(('broadcast', self.self.id))
				else:
					fl = self.get_location(ratio)

					# Fake Location Update
					self.peer.prev_location, self.peer.location = self.peer.location, fl

					# Fake Speed Update
					self.peer.speed = 0.8 * self.peer.speed + 0.2 * (self.peer.prev_location >> self.peer.location)

					# Log
					self.log('fake|{vid}|{t}|{id}|{l}|{r}\n'.format(
						vid=self.id, id=self.peer.id, t=time.time(), l=fl, r=ratio
					))

					# Message (Fake)
					messages.append('{vid},{cid},{type},{t},{l},{s}'.format(vid=self.id, cid=self.peer.id, type='fake', t=gps_time, l=fl, s=self.peer.speed))
			elif self.state == 'READY':
				# Time out
				if self.timer and time.time() - self.timer > 1:
					# Log
					self.log('timeout|{vid}|{t}|{id}\n'.format(
						vid=self.id, id=self.peer.id, t=time.time()
					))

					# Waiting slot
					self.waiting_slot.append(((self.self.id, self.self.path.copy, self.peer), time.time()))

					self.timer = None
					self.self.path = None
					self.peer = None
					# BROADCAST state
					self.state = Broadcast(self)
					# BROADCAST message
					self.queue.put(('broadcast', self.self.id))

		# Location Update
		self.self.prev_location, self.self.location = self.self.location, gps_location

		# Speed Update
		self.self.speed = 0.8 * self.self.speed + 0.2 * (self.self.prev_location >> self.self.location)

		return messages


	def get_ratio(self, location):
		p = self.self.path

		p.now, n, _ = p.approximate(location)

		cum = p[p.now] >> n
		for d in p.distances[:p.now]: cum += d

		self.log('ratio|{vid}|{t}|{id}|{l}|{appr}|{ratio}\n'.format(
			vid=self.id, id=self.self.id, t=time.time(), l=self.self.location, appr=n, ratio=cum / p.total_distance
		))

		return cum / p.total_distance


	def get_location(self, ratio):
		p = self.peer.path

		if ratio == 0:
			return Location(*p[0])
		elif ratio < 1:
			distance = p.total_distance * ratio

			cum = 0
			for i, d in enumerate(p.distances):
				cum += d

				if cum == distance:
					return Location(*p[i + 1])
				elif cum > distance:
					s = cum - distance
					return (p[i] * s + p[i + 1] * (d-s)) / d
		else:
			return Location(*p[-1])
