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

from countries import countries
from location import Location
from index import TextIndex, GeoboxIndex
import re
from us_states import State
import math

class City(Location):
    """
    Wrapper for a city location object
    """

    #what we want to save for a city
    __spec__ = Location.__spec__ + ['continent', 'country', 'state', 'continentId', 'countryId', 'stateId', 'cityId', 'aliases', 'population']
    __keyspec__ = Location.__spec__ + ['country', 'state' ]

    _keys = {'name': TextIndex('City', ('name', 'state', 'aliases'), ','),
             'geobox': GeoboxIndex('City', [GeoboxIndex.RES_16KM, GeoboxIndex.RES_128KM]) }
    
    def __init__(self, **kwargs):

        super(City, self).__init__(**kwargs)
        
        self.continent = kwargs.get('continent', '').strip()
        self.country = countries.get( kwargs.get('country', None), kwargs.get('country', '')).strip()        
        self.state = kwargs.get('state', '').strip()
        
        self.continentId = kwargs.get('continentId', 0)
        self.countryId = kwargs.get('countryId', 0)
        self.stateId = kwargs.get('stateId', 0)
        self.cityId = kwargs.get('cityId', 0)
        
        aliases = set(filter(lambda x: re.match('^[a-zA-Z0-9,\\-\'": ]+$', x), kwargs.get('aliases', '').split(',')))
        state = State.get(self.state)
        if state:
            aliases.add("%s %s" % (self.name, state.code))
            aliases.add("%s %s" % (self.name, state.name))
        
        self.aliases = ",".join(aliases)
        
        #index <city state> as an alias
        
        self.population = kwargs.get('population', 0)
        
    def score(self, refLat, refLon):
        
        ret = getattr(self, '_score', None)
        if not ret:
            population = self.population
            if not population:
                population = 10
            if refLat and refLon:
                d = Location.getLatLonDistance((self.lat, self.lon), (refLat, refLon))
            
            ret = math.log(float(1000*population)) - math.log(d if d>=1 else 1.00000001)
            self._score = ret
        return ret
        
        
    @classmethod
    def getByName(cls, name, redisConn, referenceLat = None, referenceLon = None, countryLimit = None):
        """
        Load a citiy or a list of city by name or alias to the city. for example, name can be New York or NYC
        @return a list of City objects that can be empty
        """
        
        cities = cls.loadByNamedKey('name', redisConn, name)
        
        #if no need to sort - just return what we get
        if len(cities) > 1 and referenceLat and referenceLon:
            
            #sort by distance to the user
            cities.sort(lambda x,y: cmp(cls.getLatLonDistance((x.lat, x.lon), (referenceLat, referenceLon)), 
                                        cls.getLatLonDistance((y.lat, y.lon), (referenceLat, referenceLon))
                                    ))
        
        if countryLimit:
            cities = filter(lambda x: x.country.lower() == countryLimit.lower(), cities)
        return cities
        
    @classmethod
    def getByRadius(cls, lat, lon, radius, redisConn, text = None):
        
        
        
        if not text:
            cities =  cls.loadByNamedKey('geobox', redisConn, lat, lon, radius, store = bool(text))
            cities = filter(lambda c: Location.getLatLonDistance((lat, lon), (c.lat, c.lon)) <= radius, cities)
            return cities
        else:
            
            #store matching elements from text key
            nameKey = cls.getIdsByNamedKey('name', redisConn, text, store = True)
            geoKey = cls.getIdsByNamedKey('geobox', redisConn, lat, lon, radius, store = True)
            
            if nameKey and geoKey:
            
                ids = redisConn.sinter(geoKey, nameKey)
                
                cities = cls.multiLoad(ids, redisConn)
                return filter(lambda c: c and Location.getLatLonDistance((lat, lon), (c.lat, c.lon)) <= radius, cities)
            else:
                return []
#        k = cls._keys['geobox']
#        k.getIds((lat, lon), radius, redisConn)
    
        
if __name__ == '__main__':
    
    import redis, time
    
   
    r = redis.Redis(db = 8, host = 'chuck')
    
    #c =  City(lat = 40.7143, lon= -74.006, country = "United States", state= "New York", name = "New York")
    #c.save(r)
    lat =  40.714
    lon =   -74.00
    
    #lat,lon = 32.0667,34.7667
    d = 20000
    st = time.time()
    cities = City.getByRadius(lat, lon, d, r, "jerusalem")
    et = time.time()
    print 1000*(et - st),"ms"
    cities.sort(lambda x,y: cmp(y.score(lat, lon), x.score(lat,lon)))
    print "Found %d cities!" % len(cities)
    print ["%s, %s %.02fkm pop %s score %s" % (c.name, c.state,Location.getLatLonDistance((lat, lon), (c.lat, c.lon)), c.population, c.score(lat, lon)) for c in cities]
    
    
#    for city in cities:
#        print city.name, city.country, Location.getLatLonDistance((lat, lon), (city.lat, city.lon))
    #import redis
    
    #c.save(r)
    #c =  City(lat = 40.1143, lon= -74.106, country = "United States", state= "New York", name = "New York")
    #c.save(r)