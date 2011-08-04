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
from index import TextIndex
import re

class City(Location):
    """
    Wrapper for a city location object
    """

    #what we want to save for a city
    __spec__ = Location.__spec__ + ['continent', 'country', 'state', 'continentId', 'countryId', 'stateId', 'cityId', 'aliases']
    __keyspec__ = Location.__spec__ + ['country', 'state' ]

    _keys = {'name': TextIndex(('name', 'aliases'), ',') }
    
    def __init__(self, **kwargs):

        super(City, self).__init__(**kwargs)
        
        self.continent = kwargs.get('continent', '').strip()
        self.country = countries.get( kwargs.get('country', None), kwargs.get('country', '')).strip()        
        self.state = kwargs.get('state', '').strip()
        
        self.continentId = kwargs.get('continentId', 0)
        self.countryId = kwargs.get('countryId', 0)
        self.stateId = kwargs.get('stateId', 0)
        self.cityId = kwargs.get('cityId', 0)
        self.aliases = ",".join(filter(lambda x: re.match('^[a-zA-Z0-9,\\-\'": ]+$', x), kwargs.get('aliases', '').split(',')))
        
        
    @classmethod
    def getByName(cls, name, redisConn, referenceLat = None, referenceLon = None, countryLimit = None):
        """
        Load a citiy or a list of city by name or alias to the city. for example, name can be New York or NYC
        @return a list of City objects that can be empty
        """
        
        cities = cls.loadByNamedKey('name', name, redisConn)
        
        #if no need to sort - just return what we get
        if len(cities) > 1 and referenceLat and referenceLon:
            
            #sort by distance to the user
            cities.sort(lambda x,y: cmp(cls.getLatLonDistance((x.lat, x.lon), (referenceLat, referenceLon)), 
                                        cls.getLatLonDistance((y.lat, y.lon), (referenceLat, referenceLon))
                                    ))
        
        if countryLimit:
            cities = filter(lambda x: x.country.lower() == countryLimit.lower(), cities)
        return cities
        

        