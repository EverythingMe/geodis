#Copyright 2011 Do@. All rights reserved.
#
#Redistribution and use in source and binary forms, with or without modification, are
#permitted provided that the following conditions are met:
#
#   1. Redistributions of source code must retain the above copyright notice, this list of
#      conditions and the following disclaimer.
#
#   2. Redistributions in binary form must reproduce the above copyright notice, this list
#      of conditions and the following disclaimer in the documentation and/or other materials
#      provided with the distribution.
#
#THIS SOFTWARE IS PROVIDED BY Do@ ``AS IS'' AND ANY EXPRESS OR IMPLIED
#WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
#FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> OR
#CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
#CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
#ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
#ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#The views and conclusions contained in the software and documentation are those of the
#authors and should not be interpreted as representing official policies, either expressed
#or implied, of Do@.

import re
import math
import itertools

from geohasher import hasher

from .countries import countries
from .location import Location
from .index import GeoBoxTextIndex, GeoboxIndex, TimeSampler
from .us_states import State

class Business(Location):
    """
    Wrapper for a city location object
    """

    #what we want to save for a city
    __spec__ = Location.__spec__ + ['continent', 'country', 'city', 'state', 'street', 'address', 'type']
    __keyspec__ = Location.__spec__ + ['street', 'city', 'state' ]

    _keys = {'name_radius': GeoBoxTextIndex('Business', [GeoboxIndex.RES_1KM , GeoboxIndex.RES_4KM, GeoboxIndex.RES_16KM],
                                            ('name', 'street'), ' ')}
    def __init__(self, **kwargs):

        super(Business, self).__init__(**kwargs)
        
        self.continent = kwargs.get('continent', '').strip()
        self.country = countries.get( kwargs.get('country', None), kwargs.get('country', '')).strip()        
        self.state = kwargs.get('state', '').strip()
        self.city = kwargs.get('city', '').strip() 
        
        self.address = kwargs.get('address', '').strip()
        
        self.street = re.sub('\\b(St|Rd|Blvd|Street|Drive|Dr)$', '', re.sub('^[0-9]+ ', '', self.address)).strip()
        self.zip = kwargs.get('zip', '').strip()
        
        _type =  kwargs.get('type', '').strip()
        if _type:
            
            self.type = _type.split('>')[-1].strip()
        else:
            self.type = ''
        
    def score(self, refLat, refLon, factor):
        
        ret = getattr(self, '_score', None)
        if not ret:
            
            if refLat and refLon:
                d = Location.getLatLonDistance((self.lat, self.lon), (refLat, refLon))
            
            
            ret = factor/d
            
            self._score = ret
        return ret
        
        
        
    @classmethod
    def getByRadius(cls, lat, lon, radius, redisConn, text = None):
        
        
        return cls.loadByNamedKey('name_radius', redisConn, lat, lon, radius, text)
        
        
        
if __name__ == '__main__':
    
    import redis, time
    
   
    r = redis.Redis(db = 8, host = 'localhost', port = 6375)
    
    
    lat = 32.702374
    lon = -117.137677
    
    #lat,lon = 32.0667,34.7667
    d = 2
    st = time.time()
    nodes = Business.getByRadius(lat, lon, 10, r, 'mcdonalds')
    #nodes.sort(lambda x,y: cmp(y.score(lat, lon), x.score(lat, lon)))
    et = time.time()
    print len(nodes)
    for n in nodes:
        print n.name, ',', n.address, Location.getLatLonDistance((lat, lon), (n.lat, n.lon)), "km"
    print 1000*(et-st)
#    for city in cities:
#        print city.name, city.country, Location.getLatLonDistance((lat, lon), (city.lat, city.lon))
    #import redis
    
    #c.save(r)
    #c =  City(lat = 40.1143, lon= -74.106, country = "United States", state= "New York", name = "New York")
    #c.save(r)