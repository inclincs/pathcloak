import os, sys
import json

import client
# from client import Client
from navigator import Navigator
from gps import Location



# class TestClient(Client):

# 	def __init__(self, vehicle_id, logger, simulation):
# 		super.__init__(vehicle_id, logger)



# 	def get_location(self):
# 		import configuration as c
# 		# server에 s w e path 요청
# 		test_vehicle = test['data'][c.vehicle]
# 		s = ~Location(*test_vehicle['s'])
# 		w = ~Location(*test_vehicle['w'])
# 		e = ~Location(*test_vehicle['e'])
# 		print('  start location: {s}'.format(s=s))
# 		print('  end location: {e}'.format(e=e))
# 		path = [ ~Location(*p) for p in test_vehicle['path'] ]

# 	def get_navigation_path(self, start, waypoint, end):
# 		pass


'''

Test Scenario




'''
if __name__ == '__main__':
	if len(sys.argv) == 6:
		
		import configuration



		vehicle_id = sys.argv[4]

		test_data_id = sys.argv[1]
		test_id = int(sys.argv[2])
		test_trial = int(sys.argv[3])
		test_speed = int(sys.argv[5])
		test_data_file = os.sep.join(configuration.data_path + ('test', '{test_data_id}.txt'.format(test_data_id=test_data_id)))
		with open(test_data_file, 'r') as input_file:
			test_data = json.load(input_file)[test_id - 1]

		simulation_id = 'trace_1'
		# simulation_producer = Producer.fromXML(os.sep.join(configuration.data_path + ('simulation', '{name}.gpx'.format(name=simulation_id))))



		log_file = os.sep.join(configuration.data_path + ('test', 'trace_{test_id}_{test_trial}.txt'.format(test_id=test_id, test_trial=test_trial)))

		test = {
			'id': test_id,
			'trial': test_trial,
			'data': test_data,
			'min_speed': test_speed
		}

		simulation = {
			'id': simulation_id
			# 'producer': simulation_producer
		}

		# TestClient(configuration.vehicle, None, test).run()
		# client.run(vehicle_id, log_file, test)
		client.run(vehicle_id, log_file, test)
	else:
		print('usage: {0} (data id) (test id) (test trial)'.format(sys.argv[0]))