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



import string
import re
import struct
from upoints.point import Point
import math
import logging
from contextlib import contextmanager
from location import Location

class AbstractIndex(object):
    
    def __init__(self, className):
        
        self.className = className
        
        

class TextIndex(AbstractIndex):
    '''
    classdocs
    '''
    
    trantab = string.maketrans("-_,", "   ")
    stopchars = "\"'\\`'[]{}()./?:)(*&^%$#@!="
    TMP_KEY_EXPIRATION = 600
    
    def __init__(self, className, fields, delimiter = ' '):
        '''
        Constructor
        '''
        AbstractIndex.__init__(self, className)
        self.fields = fields
        self.delimiter = delimiter
        
    def getKey(self, word):
        
        return 'ft:%s:%s' % (self.className, word)
    
    def exist(self, terms, redisConn):
        
        keys = [self.getKey(t) for t in terms]
        
        ret = []
        p = redisConn.pipeline()
        [p.exists(k) for k in keys]
        
        rx = p.execute()
        for idx, k in enumerate(keys):
            if rx[idx]:
                ret.append(terms[idx])
    
        return ret
                
    @staticmethod
    def normalizeString(str_):
        
        return str_.translate(TextIndex.trantab, TextIndex.stopchars).lower().strip().replace('  ', ' ')
    
    def save(self, obj, redisConn):
        
        indexKeys = set()
        for f in self.fields:
            [indexKeys.add(self.normalizeString(x.lower().strip())) for x in (getattr(obj, f, '').split(self.delimiter)) ]
            
        
        for x in indexKeys:
            redisConn.zadd(self.getKey(x), **{obj.getId(): 1/float(len(indexKeys)) })
            
        
    def getIds(self, redisConn, value, store = False):
        
        values = re.split(self.delimiter, self.normalizeString(value.lower().strip()))
        
        if not values:
            return []
        keys = [self.getKey(value) for value in values]
        
        if len(keys) == 1 and store:
            return keys[0]
        
        tmpKey = 'ft_tmp:%s:%s' % (self.className, " ".join(values))
        p = redisConn.pipeline(False)
        p.zinterstore(tmpKey, keys, aggregate = 'SUM')
        p.expire(tmpKey, self.TMP_KEY_EXPIRATION)
        if not store: 
            p.zrevrange(tmpKey, 0,-1, True)

            rx = p.execute()
            return [x[0] for x in rx[-1]]
        else:
            p.execute()
            #only return if we have any results
            return tmpKey if p[0] > 0 else None
    
    
from geohasher import hasher
import time
import itertools
TSTabs = 0
@contextmanager
def TimeSampler(func = None, actionDescription = ''):
    global TSTabs
    TSTabs += 1
    
    st = time.time()
    yield
    et = time.time()
    TSTabs -= 1
    msg =(TSTabs * '\t') + ('Action %s took %.03fms' % (actionDescription, 1000*(et - st)))
    
    if func:
        func(msg)
    else:
        logging.info(msg)
    
    
class GeoboxIndex(AbstractIndex):

    
    RES_1KM = 1
    RES_4KM = 4
    RES_16KM = 16
    RES_64KM = 64
    RES_128KM = 128
    
    #Mapping bit resultions to *very* rough geo box size precision
    BIT_RESOLUTIONS = {
                   
        RES_1KM: 35,
        RES_4KM: 39,
        RES_16KM: 43,
        RES_64KM: 47,
        RES_128KM: 49
    }
    
    def __init__(self, className, resolutionsInKM):
        
        AbstractIndex.__init__(self, className)
        self.resolutions = resolutionsInKM
        
        
    def getKey(self, resolution, cell):
        
        return 'box:%s:%s:%x' % (self.className, resolution, cell >> 32)
    
        
    def getGeocell(self, lat, lon, bitres):
        
        return (hasher.encode(lat, lon) & int('1'*(64 - bitres) + '0'*bitres, 2))
        
    def save(self, obj, redisConn):
        
        
        p = redisConn.pipeline()
        for r in self.resolutions:
            
            cell = self.getGeocell(obj.lat, obj.lon, self.BIT_RESOLUTIONS[r])
            
            k = self.getKey(r, cell)
            #print _hash
            p.zadd(k, **{obj.getId(): hasher.encode(obj.lat, obj.lon)})
            
        p.execute()
        
        
    def getIds(self, redisConn, lat, lon,  radius, store = False ):
        
        
        res = None
        for r in self.resolutions:
            if r >= radius:
                res = r 
                break
        
        
        if not res:
            logging.warn("Radius too big for available resolutions")
            return []
        closest = set()
        
        
        if radius > 0 and radius <= self.RES_128KM:  
            bitres = self.BIT_RESOLUTIONS[res]
            cell = self.getGeocell(lat, lon, bitres)
            closest.add(self.getKey(res, cell))
            p = Point(lat, lon)
            
            with TimeSampler(None, 'collecting cells'):
                for bearing in (0, 45, 90, 135, 180, 225, 270, 315):
                        
                    dest = p.destination(bearing, math.sqrt(2 * (radius**2)) if bearing % 90 else radius)
                    
                    cell = self.getGeocell(dest.latitude, dest.longitude, self.BIT_RESOLUTIONS[res])
                    
                    closest.add(self.getKey(res, cell))
            
            
            tmpKey = 'box:%s:%s,%s' % (self.className, lat,lon)
            if not store:
                redisConn.zunionstore(tmpKey, list(closest))
                return redisConn.zrevrange(tmpKey, 0, -1, withscores=True)
            else:
                return list(closest)

            
            
        return [] if not store else None

            
class GeoBoxTextIndex(AbstractIndex):
    """
    Mashup of textual and geobox indices
    """
    
    def __init__(self, className, resolutionsInKM, fields, delimiter = ' '):
        
        self.geoIndex = GeoboxIndex(className, resolutionsInKM)
        self.textIndex = TextIndex(className, fields, delimiter)
        
    def save(self, obj, redisConn):
        
        self.geoIndex.save(obj, redisConn)
        self.textIndex.save(obj, redisConn)
        
        
    def getIds(self, redisConn, lat, lon,  radius, text = ''):
        
        if not text:
            
            ids = self.geoIndex.getIds(redisConn, lat, lon, radius, False)
            nodes = filter(lambda c: c and Location.getLatLonDistance((lat, lon), c[1]) <= radius, ids)
            return [id[0] for id in ids]
        else:
            
            #store matching elements from text key
            nameKey = self.textIndex.getIds(redisConn, text, True)
            geoKeys = self.geoIndex.getIds(redisConn, lat, lon, radius, True)
        
            if nameKey and geoKeys:
                
                tmpKey = 'tk:%s::%%s' % (hash('%s' % [lat,lon,radius,text or '']))
                with TimeSampler(None, 'Getting shit done'):
                    p = redisConn.pipeline(False)
                    for id, gk in enumerate(geoKeys):
                        p.zinterstore(tmpKey % id, {gk: 1, nameKey: 0}, 'SUM')
                    for id, gk in enumerate(geoKeys):
                        p.zrevrange(tmpKey % id, 0, -1, True)
                    
                    rx = p.execute()
                with TimeSampler(None, 'Filtering shit out'):
                    ids = filter(lambda x:  Location.getLatLonDistance((lat, lon), x[1]) <= radius, ((x[0], hasher.decode(long(x[1]))) for x in itertools.chain(*(rx[len(geoKeys):]))))
                    
                return [id[0] for id in ids]
            else:
                return []
        
    
class IndexableObject(object):
    
    _keys_ = {}
    
    def save(self, redisConn):
        
        for k in self._keys_.values():
            k.save(self, redisConn)
    