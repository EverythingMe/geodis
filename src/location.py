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
import geohash
import math

class Location(object):

    CITY = 'city'
    VENUE = 'venue'

    def __init__(self, **kwargs):
        
        self.lat = kwargs.get('lat', None)
        self.lon = kwargs.get('lon', None)
        self.name = kwargs.get('name', '').strip()
        self.country = countries.get( kwargs.get('country', None), kwargs.get('country', '')).strip()
        self.state = kwargs.get('state', None).strip()
        self.zipcode = kwargs.get('zipcode', '').strip()

        self.key = ':'.join(('loc', self.name, self.country, self.state, self.zipcode))

    def save(self, redisConn):


        redisConn.hmset(self.key, dict(((k, getattr(self, k)) for k in \
                                        ('lat', 'lon', 'name', 'country', 'state', 'zipcode'))))

        
        redisConn.zadd('locations:geohash',  self.key, geohash.encode_uint64(self.lat, self.lon))

    def __str__(self):
        return "Location: %s" % self.__dict__
    
    @staticmethod
    def load(key, redisConn):
        """
        a Factory function to load a location from a given location key
        """
        d = redisConn.hgetall(key)
        if not d:
            return None

        #build a new object based on the loaded dict
        return Location(**d)

    @staticmethod
    def getByLatLon(lat, lon, redisConn):
        geoKey = geohash.encode_uint64(lat, lon)
        
        return Location.getByGeohash(geoKey, redisConn)
        
    @staticmethod
    def getByGeohash(geoKey, redisConn):
        
        tx = redisConn.pipeline()
        tx.zrangebyscore('locations:geohash', geoKey, 'inf', 0, 1, True)
        tx.zrangebyscore('locations:geohash', '-inf', geoKey, 0, 1, True)
        ret = tx.execute()

        #find the two closest locations to the left and to the right of us
        
        right = ret[0][0] if ret[0] else None
        left = ret[1][0] if ret[1] else None

        hashRight = long(right[1]) if right else None
        hashLeft = long(left[1]) if left else None

        if not hashLeft and not hashRight:
            return None
        
        deltaRight = abs(long(geoKey) - (hashRight or 0))
        deltaLeft = abs(long(geoKey )- (hashLeft or 0))

        selected = right if deltaRight < deltaLeft else left


        return Location.load(selected[0], redisConn)


        

        

        
        
        