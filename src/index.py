'''
Created on Aug 1, 2011

@author: dvirsky
'''
import string
import re

class TextIndex(object):
    '''
    classdocs
    '''
    
    trantab = string.maketrans("-_", "  ")

    def __init__(self, fields, delimiter = ' '):
        '''
        Constructor
        '''
        self.fields = fields
        self.delimiter = delimiter
        
    def getKey(self, className, word):
        
        return 'ft:%s:%s' % (className, word)
    
        
    def normalizeString(self, str_):
        
        return str_.translate(self.trantab, "\"'\\`'[]{}(),./?:)(*&^%$#@!=")
    
    def save(self, obj, redisConn):
        
        indexKeys = set()
        for f in self.fields:
            [indexKeys.add(self.normalizeString(x.lower().strip())) for x in (getattr(obj, f, '').split(self.delimiter)) ]
            
        for x in indexKeys:
            redisConn.sadd(self.getKey(obj.__class__.__name__, x), obj.getId())
            
        
    def getIds(self, className, value, redisConn):
        
        values = re.split(self.delimiter, self.normalizeString(value.lower().strip()))
        
        if not values:
            return []
        keys = [self.getKey(className, value) for value in values]
        print keys
        return redisConn.sinter(keys)
    
    
class IndexableObject(object):
    
    _keys_ = {}
    
    def save(self, redisConn):
        
        for k in self._keys_.values():
            k.save(self, redisConn)
    