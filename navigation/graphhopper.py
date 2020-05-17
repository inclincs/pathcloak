import requests

from gps import Location
from navigator import NavigationService



class Graphhopper(NavigationService):

   URL = 'http://192.168.0.100:8282/route?point={start}&point={end}&points_encoded=false&vehicle=car'
   
   # URL = 'http://pylon.hanyang.ac.kr:8282/route?point={start}&point={end}&points_encoded=false&vehicle=car'

   def __init__(self, url=URL):
      self.url = url

   def request(self, start, waypoint, end):
      path = []

      response = requests.get(self.url.format(start='{},{}'.format(start.lat, start.lon), end='{},{}'.format(end.lat, end.lon)))
      
      if response.status_code == requests.codes.ok:
         for location in response.json()['paths'][0]['points']['coordinates']:
            l = ~Location(*location)
            if len(path) == 0 or path[-1] != l: path.append(l)
         return path
      else:
         print('Graphhopper error:', response.status_code, response.content)

      return None

if __name__ == '__main__':
   gh = Graphhopper()
   print(gh.request(Location.fromString('37.30730,126.83952'), None, Location.fromString('37.30912,126.83620')))
