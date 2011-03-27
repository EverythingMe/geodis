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
import struct

class Location(object):

    CITY = 'city'
    VENUE = 'venue'

    def __init__(self, **kwargs):
        
        self.lat = kwargs.get('lat', None)
        self.lon = kwargs.get('lon', None)
        self.name = kwargs.get('name', '').strip()
        self.country = countries.get( kwargs.get('country', None), kwargs.get('country', '')).strip()
        self.state = kwargs.get('state', '').strip()
        self.zipcode = kwargs.get('zipcode', '').strip()
        
        self.key = ':'.join(('loc', self.name, self.country, self.state, self.zipcode)).lower()

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
        
        d = redisConn.hgetall(str(key))
        
        if not d:
            return None
        
        #build a new object based on the loaded dict
        return Location(**d)

    @staticmethod
    def getByLatLon(lat, lon, redisConn):
        geoKey = geohash.encode_uint64(lat, lon)
        
        return Location.getByGeohash(geoKey, redisConn)

    @staticmethod
    def getDistance(geoHash1, geoHash2):
        """
        Estimate the distance between 2 geohashes in uint64 format
        """

        return abs(geoHash1 - geoHash2)
        
        try:
            coords1 = geohash.decode_uint64(geoHash1)
            coords2 = geohash.decode_uint64(geoHash2)
            print coords1, coords2
            return math.sqrt(math.pow(coords1[0] - coords2[0], 2) +
                         math.pow(coords1[1] - coords2[1], 2))
        except Exception, e:
            print e
            return None



    @staticmethod
    def getByGeohash(geoKey, redisConn):
        
        tx = redisConn.pipeline()
        tx.zrangebyscore('locations:geohash', geoKey, 'inf', 0, 1, True)
        tx.zrevrangebyscore('locations:geohash', geoKey, '-inf', 0, 1, True)
        ret = tx.execute()

        #find the two closest locations to the left and to the right of us
        candidates = filter(None, ret[0]) + filter(None, ret[1])
        
        closestDist = None
        selected = None
        if not candidates :
            return None

        for i in xrange(len(candidates)):
            
            gk = (candidates[i][1])
            #gk = struct.unpack('i', struct.pack('f', candidates [i][1]))[0]
            
            
            dist = Location.getDistance(geoKey, gk)
            if dist is None:
                continue
            
            
            if not closestDist or dist < closestDist:
                closestDist = dist
                selected = i
            
            
        if selected is None:
            return None

        
        return Location.load(str(candidates[selected][0]), redisConn)


        

        

        
        
        