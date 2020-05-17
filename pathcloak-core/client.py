#-*- coding: utf-8 -*-

import os, sys
import time, datetime
import random
import requests
import threading

import configuration
from screen import Screen
from graphhopper import Graphhopper
from gps import Location
from producer import Producer
from obu import OBU
from gps_receiver import GPSReceiver
from navigator import Navigator
from core import Core
from broadcast_receiver import BroadcastAcceptor
from broadcast_sender import BroadcastSender
from timer import Timer



def run(vehicle_id, log_file, test=None, simulation=None):
	# Clear Screen
	print('\033[2J')
	print('\033[0;0f', end='')



	# Test
	if test:
		print('Test')
		print('  id: {}'.format(test['id']))
		print('  trial: {}'.format(test['trial']))
		print('  name: {}'.format(test['data']['name']))
		print('  area: {}'.format(test['data']['area']))
		print('  description: {}'.format(test['data']['desc']))
		print()



	# PathCloak
	print('PathCloak')



	# Configuration
	c = configuration

	print('  vehicle id: {}'.format(vehicle_id))
	


	# Simulation
	if simulation:
		simulation['producer'] = Producer.fromXML(os.sep.join(c.data_path + ('simulation', '{name}_{vehicle}.gpx'.format(name=simulation['id'], vehicle=vehicle_id))))
		print('  simulation: {name}'.format(name=simulation['id']))



	# Target Server
	server_url = '{ip}:{port}/pathcloak'.format(**c.server)

	print('  target server: {server_url}'.format(server_url=server_url))



	# On-Board Unit
	while True:
		obu_tx = OBU(**c.obu['tx'])
		if obu_tx.socket != None: break
		time.sleep(0.5)

	print('  obu tx: {ip}, {port}'.format(**c.obu['tx']))



	# GPS Receiver
	gps_receiver = GPSReceiver(simulation['producer'] if simulation else obu_tx)

	print('  gps receiver')



	# Location
	if test:
		# server에 s w e path 요청
		test_vehicle = test['data'][vehicle_id]
		s = Location(*test_vehicle['s'])
		if simulation: s = Location(*simulation['producer'][0])
		print('  start location: {s}'.format(s=s))
		w = Location(*test_vehicle['w']) if 'w' in test_vehicle else Location(0, 0)
		e = Location(*test_vehicle['e'])
		print('  end location: {e}'.format(e=e))
		path = [ Location(*p) for p in test_vehicle['path'] ]
	else:
		while True:
			_, s = gps_receiver.request('location')
			if s != Location(-5000, -5000): break

		print('  start location: {s}'.format(s=s))

		while True:
			print('  input your end location > ', end='')
			if simulation:
				e = Location(*simulation_producer[-1])
			else:
				try:
					e = Location.fromString(input())
				except:
					continue
			print('  end location: {e}'.format(e=e))

			w = s
			while s >> w < 0.005:
				while True:
					_, w = gps_receiver.request('location')
					if w != Location(-5000, -5000): break
			
			t_navigate = time.time()
			path = Navigator(Graphhopper()).get_path(s, w, e)

			print('  navigator')
			print('    elapsed time: {t}'.format(t=time.time() - t_navigate))
			print('    result: {result}'.format(result=path != None))

			if path == None:
				print('can not get path data from navigator')
				exit()
			else: break



	# Core
	core = Core(vehicle_id, (s, w, e, path), log_file)
	core.min_speed = test['min_speed']
	print('  core')



	# Broadcast Sender
	sender = BroadcastSender(core, obu_tx)

	print('  broadcast sender')
	


	# Broadcast Acceptor
	acceptor = BroadcastAcceptor(core, c.obu['rx']['port'])

	print('  broadcast receiver(acceptor)')

	print()
	print('press enter to start pathcloak...')
	input()



	# Start
	print('\033[2J\033[0;0f', end='')
	print('PathCloak{}{}'.format(' Test {} {}'.format(test['id'], test['trial']) if test else '', ' (Simulation)' if simulation else ''))

	core.start()

	sender.start()
	acceptor.start()


	Screen.clear_line(2, 2)
	print("[ Core ] Time: {:4d} s  Average Speed: {:.1f} m/s {:.1f} km/h".format(int(time.time() - core.t_start), core.self.speed * 1000, core.self.speed * 3600))


	for elapsed in Timer(None, 1, time.time, time.sleep):
		Screen.clear_line(2, 2)
		print("[ Core ] Vehicle id: {}    Time: {:3d} s    Average Speed: {:.1f} m/s {:.1f} km/h".format(vehicle_id, int(time.time() - core.t_start), core.self.speed * 1000, core.self.speed * 3600))
		t, l = gps_receiver.request()

		messages = core.update(t, l)

		random.shuffle(messages)

		try:
			Screen.clear_line(4, 3)
			print('[ Client ] ({:.2f}) \n {}'.format(time.time() - core.t_start, '\n '.join(messages)))
			response = requests.post(
				server_url,
				{
					'key': 'pathcloak',
					'traces': '\n'.join(messages),
					'test_id': str(test['id']),
					'test_trial': str(test['trial'])
				},
				timeout=0.5
			)

			Screen.clear_line(8)
			if response.status_code == requests.codes.ok:
				print('[ Server ] ({:.2f}) {}'.format(time.time() - core.t_start, response.content))
			else:
				print('[ Server ] ({:.2f}) {}'.format(time.time() - core.t_start, response.status_code))
		except (ConnectionRefusedError, requests.exceptions.ConnectionError, requests.packages.urllib3.exceptions.MaxRetryError, requests.exceptions.ReadTimeout):
			pass


		logs = []
		while core.log_queue.qsize() > 0:
			l = core.log_queue.get().strip('\n')
			logs.append(l)

		try:
			response = requests.post(
				server_url,
				{
					'key': 'log',
					'logs': '\n'.join(logs),
					'test_id': str(test['id']),
					'test_trial': str(test['trial'])
				},
				timeout=0.5
			)
		except (ConnectionRefusedError, requests.exceptions.ConnectionError, requests.packages.urllib3.exceptions.MaxRetryError, requests.exceptions.ReadTimeout):
			pass



if __name__ == '__main__':
	import sys

	log_file = None
	# Client(sys.argv[1], log_file).run()
