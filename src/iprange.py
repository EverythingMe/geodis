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
import socket, struct
from location import Location
import geohash

class IPRange(object):

    _indexKey = 'iprange:locations'
    def __init__(self, rangeMin, rangeMax, lat, lon):

        self.rangeMin = rangeMin
        self.rangeMax = rangeMax

        #encode a numeric geohash key
        self.geokey = geohash.encode_uint64(lat, lon)
        
        self.key = '%s:%s' % (self.rangeMin, self.rangeMax)

    def save(self, redisConn):
        
        redisconn.zadd(self._indexKey, '%s@%s' % (self.geoKey, self.key) , self.rangeMax)
        

    @staticmethod
    def getLocation(self, ip, redisConn):


        ipnum = self.ip2long(ip)

        #get the location record from redis
        record = redisConn.zrangebyscore(self._indexKey, ipnum, 'inf', 0, 1)

        if not record:
            #not found? k!
            return None

        #extract location id
        try:
            geoKey = record[0].partition('@')[0]
        except IndexError:
            return None

        #load a location by the
        return Location.getByGeohash(geoKey)


    @staticmethod
    def ip2long(ip):
        ip_packed = socket.inet_aton(ip)
        return struct.unpack("!L", ip_packed)[0]
    