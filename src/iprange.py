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


import socket, struct, re
from city import City
from zipcode import ZIPCode
from geohasher import hasher
import struct

class IPRange(object):

    _indexKey = 'iprange:locations'
    def __init__(self, rangeMin, rangeMax, lat, lon, zipcode = ''):

        self.rangeMin = rangeMin
        self.rangeMax = rangeMax
        self.lat = lat
        self.lon = lon
        self.zipcode = zipcode

        #encode a numeric geohash key
        self.geoKey = hasher.encode(lat, lon)
        
        self.key = '%s:%s:%s' % (self.rangeMin, self.rangeMax, self.zipcode)

    def save(self, redisConn):
        """
        Save an IP range to redis
        @param redisConn a redis connectino or pipeline
        """
        
        redisConn.zadd(self._indexKey, '%s@%s' % (self.geoKey, self.key) , self.rangeMax)
        
        
    def __str__(self):
        """
        textual representation
        """
        return "IPRange: %s" % self.__dict__

    @staticmethod
    def get(ip, redisConn):
        """
        Get a range and all its data by ip
        """
        
        ipnum = IPRange.ip2long(ip)

        #get the location record from redis
        record = redisConn.zrangebyscore(IPRange._indexKey, ipnum ,'+inf', 0, 1, True)
        if not record:
            #not found? k!
            return None

        #extract location id
        try:
            geoKey,rng = record[0][0].split('@')
            
            lat,lon = hasher.decode(long(geoKey))
            
            rngMin, rngMax, zipcode =  rng.split(':')
            rngMin = int(rngMin)
            rngMax = int(rngMax)
        except IndexError:
            return None

        #address not in any range
        if not rngMin <= ipnum <= rngMax:
            return None
        
        return IPRange(rngMin, rngMax, lat, lon, zipcode)

    @staticmethod
    def getZIP(ip, redisConn):
        """
        Get a zipcode location object based on an IP
        will return None if you are outside the US
        """

        range = IPRange.get(ip, redisConn)


        if not range or not re.match('^[0-9]{5}$', range.zipcode):
            return None

        return ZIPCode.getByKey(redisConn, name = range.zipcode)






    @staticmethod
    def getCity(ip, redisConn):
        """
        Get location object by resolving an IP address
        @param ip IPv4 address string (e.g. 127.0.0.1)
        @oaram redisConn redis connection to the database
        @return a Location object if we can resolve this ip, else None
        """

        range = IPRange.get(ip, redisConn)
        if not range:
            return None

        

        #load a location by the
        return City.getByGeohash(hasher.encode(range.lat, range.lon), redisConn)


    @staticmethod
    def ip2long(ip):
        """
        Convert an IP string to long
        """
        ip_packed = socket.inet_aton(ip)
        return struct.unpack("!L", ip_packed)[0]
    