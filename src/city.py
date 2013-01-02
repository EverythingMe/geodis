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
from index import TextIndex, GeoboxIndex, GeoBoxTextIndex
import re
from us_states import State
import math
import logging

class City(Location):
    """
    Wrapper for a city location object
    """

    #what we want to save for a city
    __countryspec__ = ['continent', 'country', 'continentId', 'countryId']
    __spec__ = Location.__spec__ + __countryspec__ + ['state', 'stateId', 'cityId', 'aliases', 'population']
    __keyspec__ = Location.__spec__ + ['country', 'state' ]
    
    __cityspec__ = set(__spec__) - set(__countryspec__)

    _keys = {'name': TextIndex('City', ('name', 'aliases'), ','),
             'geoname': GeoBoxTextIndex('City', [GeoboxIndex.RES_128KM], ('name', 'aliases'), ',')
             }
    
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
            population = float(self.population)
            dScore = 0.2
            if not population:
                population = 10
            popScore =  1 - math.exp(-0.00001*population)
            if refLat and refLon:
                d = Location.getLatLonDistance((self.lat, self.lon), (refLat, refLon))
                dScore =  max(0.6, 1 - 1/(1+math.exp(-0.02*d+2*math.e) ))

                logging.info("SCORE FOR %s, %s: distance %skm, population %s, score: %s", self.name, self.country, d, population, dScore * popScore)
            ret = popScore * dScore

            #print ret
            self._score = ret
        return ret
        
    def toCountry(self):
        """
        Removes all non-country and non-continent values from the city
        """
        for k in self.__cityspec__:
            self.__dict__[k]=None
        
    @classmethod
    def exist(cls, terms, redisConn):
        
        return cls._keys['name'].exist(terms, redisConn)
        
    @classmethod
    def getByName(cls, name, redisConn, referenceLat = None, referenceLon = None, countryLimit = None, limit = 5):
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
        return cities[:limit]
        
    @classmethod
    def getByRadius(cls, lat, lon, radius, redisConn, text = None, limit = 5):
        
        
        nodes = cls.loadByNamedKey('geoname', redisConn, lat, lon, radius, text or '')
        nodes.sort(lambda x,y: cmp(y.score(lat, lon), x.score(lat,lon)))
        return nodes[:limit]
        
if __name__ == '__main__':
    
    import redis, time
    
   
    r = redis.Redis(db = 8, host = 'localhost', port = 6375)
    
    #c =  City(lat = 40.7143, lon= -74.006, country = "United States", state= "New York", name = "New York")
    #c.save(r)
    lat =  51.5085
    lon =   -0.1
    
    #lat,lon = 32.0667,34.7667
    d = 128
    st = time.time()
    #cities = City.getByRadius(lat, lon, d, r, "haifa")
    cities = City.getByName('new york', r, lat, lon)
    et = time.time()
    print 1000*(et - st),"ms"
    print "Found %d cities!" % len(cities)
    print "\n".join(["%s, %s %.02fkm pop %s score %s" % (c.name, c.state,Location.getLatLonDistance((lat, lon), (c.lat, c.lon)), c.population, c.score(lat, lon)) for c in cities])
    
    
#    for city in cities:
#        print city.name, city.country, Location.getLatLonDistance((lat, lon), (city.lat, city.lon))
    #import redis
    
    #c.save(r)
    #c =  City(lat = 40.1143, lon= -74.106, country = "United States", state= "New York", name = "New York")
    #c.save(r)