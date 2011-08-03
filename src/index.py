'''
Created on Aug 1, 2011

@author: dvirsky
'''
import string

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
        
        k = self.getKey(className, self.normalizeString(value.lower().strip()))
        
        return redisConn.smembers(k)
    