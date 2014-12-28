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
from geohasher import hasher
import math


class Location(object):
    """
    This is the base class for all location subclasses
    """
    
    __spec__ = ['lat', 'lon', 'name']
    __keyspec__ = None
    
    def __init__(self, **kwargs):

        self.lat = kwargs.get('lat', None)
        self.lon = kwargs.get('lon', None)
        self.name = kwargs.get('name', '').strip()
        

    def getId(self):

        return '%s:%s' % (self.__class__.__name__, ':'.join((str(getattr(self, x)) for x in self.__keyspec__ or self.__spec__)))

    @classmethod
    def getGeohashIndexKey(cls):

        return '%s:geohash' % cls.__name__

    def save(self, redisConn):

        
        #save all properties
        redisConn.hmset(self.getId(), dict(((k, getattr(self, k)) for k in \
                                        self.__spec__)))

        self._indexGeohash(redisConn)

        

    def _indexGeohash(self, redisConn):
        """
        Save the key of the object into the goehash index for this object type
        """

        redisConn.zadd(self.getGeohashIndexKey(), self.getId(), hasher.encode(self.lat, self.lon))


    def __str__(self):
        return "%s: %s" % (self.__class__.__name__, self.__dict__)
    
    @classmethod
    def load(cls, key, redisConn):
        """
        a Factory function to load a location from a given location key
        """
        
        d = redisConn.hgetall(str(key))
        
        if not d:
            return None
        
        #build a new object based on the loaded dict
        return cls(**d)


    @classmethod
    def getByLatLon(cls, lat, lon, redisConn):

        geoKey = hasher.encode(lat, lon)
        
        return cls.getByGeohash(geoKey, redisConn)

    @staticmethod
    def getDistance(geoHash1, geoHash2):
        """
        Estimate the distance between 2 geohashes in uint64 format
        """

#        return abs(geoHash1 - geoHash2)
        
        try:
            coords1 = hasher.decode(geoHash1)
            coords2 = hasher.decode(geoHash2)
            return math.sqrt(math.pow(coords1[0] - coords2[0], 2) +
                         math.pow(coords1[1] - coords2[1], 2))
        except Exception, e:
            print e
            return None



    @classmethod
    def getByGeohash(cls, geoKey, redisConn):
        """
        Get a location (used directly on a subclass only!) according to a geohash key
        """


        key = cls.getGeohashIndexKey()
        tx = redisConn.pipeline()
        tx.zrangebyscore(key, geoKey, 'inf', 0, 4, True)
        tx.zrevrangebyscore(key, geoKey, '-inf', 0, 4, True)
        ret = tx.execute()

        #find the two closest locations to the left and to the right of us
        candidates = filter(None, ret[0]) + filter(None, ret[1])
        
        closestDist = None
        selected = None
        if not candidates :
            return None

        for i in xrange(len(candidates)):
            
            gk = long(candidates[i][1])
            
            dist = Location.getDistance(geoKey, gk)
            if dist is None:
                continue
            
            if not closestDist or dist < closestDist:
                closestDist = dist
                selected = i
            
            
        if selected is None:
            return None

        
        return cls.load(str(candidates[selected][0]), redisConn)


        

        

        
        
        