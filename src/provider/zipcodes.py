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

#Importer for zipcodes.csv file found in /data

from zipcode import ZIPCode
from us_states import code_to_state
import csv
import logging
from city import City

from importer import Importer

class ZIPImporter(Importer):
    
    def runImport(self):
        """
        File Format:
        "00210","Portsmouth","NH","43.005895","-71.013202","-5","1"
        """

        try:
            fp = open(self.fileName)
        except Exception, e:
            logging.error("could not open file %s for reading: %s" ,self.fileName, e)
            return False

        self.reset(ZIPCode)

        reader = csv.reader(fp, delimiter=',', quotechar = '"')
        
        features = {}
        countryId = None
        continentId = None
        for key in self.redis.keys("City:*"):
            try:
                city = self.redis.hgetall(key)#dict(zip(City.__spec__, key.split(':')[1:]))
            except Exception, e:
                logging.error(e)
                continue
            
            if city.get('country')=='United States':
                
                if not continentId:
                    continentId = city['continentId']
                
                if not countryId:
                    countryId = city['countryId']
                    
                state = features.get(city['state'], None)
                if not state:
                    state = {'id': city['stateId'], 'cities':{}}
                    features[city['state']] = state
                state['cities'][city['name']] = city['cityId']
            
        pipe = self.redis.pipeline()
        i = 0
        fails = 0
        for row in reader:
            if len(row)==0:
                continue
            try:
                name = row[0]
                city = row[1]
                stateCode = row[2]
                lat = float(row[3])
                lon = float(row[4])
                state = stateCode#code_to_state.get(stateCode, '').title()
                country = 'US'
                continent = 'Norh America'
                
                stateName = code_to_state.get(stateCode, '').title()
                stateId = features[stateName]['id']
                cityId = features[stateName]['cities'].get(city)

                loc = ZIPCode(name = name,
                              city = city,
                              cityId = cityId,
                              state = state,
                              stateId = stateId,
                              country = country,
                              countryId = countryId,
                              continent = continent,
                              continentId = continentId,
                              lat = lat,
                              lon = lon)

                loc.save(pipe)

                
                
            except Exception, e:
                logging.error("Could not import line #%d: %s, %s: %s" % (i+1, city, state, e))
                fails += 1
                
            i += 1
            if i % 1000 == 0:
                pipe.execute()

        pipe.execute()

        logging.info("Imported %d locations, failed %d times" , i, fails)

        return True
