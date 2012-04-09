'''
Created on Aug 1, 2011

@author: dvirsky
'''
import string
import re
import struct
from upoints.point import Point
import math
import logging
from contextlib import contextmanager

class AbstractIndex(object):
    
    def __init__(self, className):
        
        self.className = className
        
        

class TextIndex(AbstractIndex):
    '''
    classdocs
    '''
    
    trantab = string.maketrans("-_,", "   ")
    stopchars = "\"'\\`'[]{}()./?:)(*&^%$#@!="
    
    def __init__(self, className, fields, delimiter = ' '):
        '''
        Constructor
        '''
        AbstractIndex.__init__(self, className)
        self.fields = fields
        self.delimiter = delimiter
        
    def getKey(self, word):
        
        return 'ft:%s:%s' % (self.className, word)
    
        
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
        
        if not store: 
            p.redisConn.zrevrange(tmpKey, 0,-1, True)
            rx = p.execute()
            return rx[1]
        else:
            p.execute()
            return tmpKey
    
    
from geohasher import hasher
import time
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
        print(msg)
    
    
class GeoboxIndex(AbstractIndex):
    
    """
    32 0.240432060456 0.132627007902 0.551619478909 [0.05893519217898018, 0.38803435884590953, 0.17061034090581972, 0.3441483498944039]
    33 0.429340492891 0.182343722042 0.424706555895 [0.3476247302094993, 0.6262698544116606, 0.17061034090581972, 0.5728570460373499]
    34 0.677839149544 0.316082721918 0.466309333314 [0.6588715093068189, 0.9830738266472073, 0.17061034090581972, 0.8988009213178181]
    35 1.12624164897 0.30154353069 0.267743189009 [1.1083801580416732, 1.417530627019095, 0.642278422577068, 1.3367773882431662]
    36 1.46724583483 0.332171630791 0.226391258306 [1.1083801580416732, 1.417530627019095, 1.3349158501539038, 2.008156704105536]
    37 1.8956834915 0.68572253006 0.361728386165 [1.1083801580416732, 1.417530627019095, 2.188047698607938, 2.8687754823448746]
    38 2.23525472614 1.21532273735 0.543706595555 [1.1083801580416732, 1.417530627019095, 2.188047698607938, 4.22706042090925]
    39 3.95252802068 0.40060653151 0.10135450765 [3.4449835365021437, 3.6936505157934114, 4.444417609532014, 4.22706042090925]
    40 5.96420748641 1.4566850957 0.24423783026 [5.802784690856734, 3.6936505157934114, 6.76247927981638, 7.597915459166355]
    41 6.89545308199 2.10307822278 0.304994928944 [9.5277670731716, 3.6936505157934114, 6.76247927981638, 7.597915459166355]
    42 10.1720804781 5.06584969054 0.498015101382 [15.407057504345847, 3.6936505157934114, 6.76247927981638, 14.825134612275146]
    43 15.70244991714 2.04756389559 0.130397325499 [15.407057504345847, 13.400257598456868, 15.000279762805896, 19.00240181989064]
    44 24.292986036 4.38468754964 0.180491914133 [30.699389541143074, 21.831510517887356, 25.638642265223208, 19.00240181989064]
    45 31.8215333913 6.61916801118 0.208009083968 [30.699389541143074, 21.831510517887356, 39.87297766519753, 34.88225584089087]
    46 50.1508310507 12.0322946168 0.239922138172 [30.699389541143074, 51.88388009921769, 63.52509668667202, 54.494957875912235]
    47 68.8983399339 10.3380081521 0.150047274899 [55.87272234387575, 72.6342479741102, 63.52509668667202, 83.56129273113031]
    48 110.37846446 17.2585540341 0.156357982678 [107.07695662530108, 127.4129835389735, 123.46262494617825, 83.56129273113031]
    49 141.164054402 15.81918507 0.112062416576 [158.29102264631186, 127.4129835389735, 123.46262494617825, 155.4895864764049]
    50 189.592768834 49.0828094896 0.258885451125 [158.29102264631186, 127.4129835389735, 250.84155600535408, 221.82551314590697]
    51 217.58366095 35.7583135476 0.164342825152 [158.29102264631186, 239.37655200397103, 250.84155600535408, 221.82551314590697]
    52 334.304641242 141.250282718 0.422519658098 [158.29102264631186, 239.37655200397103, 509.20726466273004, 430.3437256559525]
    53 480.881721605 42.6821392524 0.0887580819455 [449.06978121731265, 534.9061148856636, 509.20726466273004, 430.3437256559525]
    54 480.881721605 42.6821392524 0.0887580819455 [449.06978121731265, 534.9061148856636, 509.20726466273004, 430.3437256559525]
    55 902.943651105 247.841727995 0.274481943244 [1068.483204504064, 1153.4852893146603, 509.20726466273004, 880.5988459394769]
    56 1611.30560458 47.4531043018 0.0294500957279 [1610.5342325593276, 1679.2761620385727, 1545.0813932908316, 1610.3306304247576]
    57 1972.13435814 363.336152087 0.184234989157 [1610.5342325593276, 1679.2761620385727, 2078.7119651608605, 2520.0150727966598]
    58 2947.53652674 666.793257545 0.226220523986 [3578.8901278508374, 3612.528941139381, 2078.7119651608605, 2520.0150727966598]
    59 4811.86719468 394.924422923 0.0820730096957 [5101.760516619482, 5169.0946698909365, 4169.850418336399, 4806.763173881624]
    60 5629.5813699 1054.49622066 0.187313434405 [5101.760516619482, 5169.0946698909365, 7440.707119206568, 4806.763173881624]
    61 5629.5813699 1054.49622066 0.187313434405 [5101.760516619482, 5169.0946698909365, 7440.707119206568, 4806.763173881624]
    62 7264.88757364 2538.40934807 0.349407932654 [5101.760516619482, 5169.0946698909365, 7440.707119206568, 11347.987988838993]
    63 13889.602916 380.737364512 0.0274116810116 [13573.197752243357, 13656.471632807468, 13793.975279096128, 14534.766999894846]
    """
    
    
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
            p.sadd(k, obj.getId())
            p.zadd(self.getKeysKey(r), **{k: cell})
            
        p.execute()
        
    def getKeysKey(self, resolution):
        return 'box:%s:%s:keys' % (self.className, resolution)
        
        
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
            print closest
            
            if not store:
                return redisConn.sunion(closest)
            else:
                tmpKey = 'box:%s:%s,%s' % (self.className, lat,lon)
                    
                redisConn.sunionstore(tmpKey, closest)
                return tmpKey
             
            
            
        return [] if not store else None
#        else:
#            closest = []
        
        return (x[0] for x in closest)
        
            
    
class IndexableObject(object):
    
    _keys_ = {}
    
    def save(self, redisConn):
        
        for k in self._keys_.values():
            k.save(self, redisConn)
    