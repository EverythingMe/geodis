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

#Importer for locations from geonames

import csv, sys
csv.field_size_limit(sys.maxsize)
import logging
import redis
import re
import json

from ..city import City
from .importer import Importer

class GeonamesImporter(Importer):
    
    def runImport(self):
        """
        File Format:
        continentId    continentName    countryId    countryName    stateId    stateName    cityId    cityName    lat    lon
        """
        
        
        try:
            fp = open(self.fileName)
        except Exception, e:
            logging.error("could not open file %s for reading: %s" ,self.fileName, e)
            return False
        
        self.reset(City)
        
        pipe = self.redis.pipeline()
        #reader = csv.reader(fp, delimiter='\t', quotechar = '"')
        
        i = 0
        fails = 0
        for line in fp:

            try:
		row = [x.encode('utf-8') for x in json.loads(line)]
                loc = City (
                    continentId =   row[0],
                    continent =     row[1],
                    countryId =     row[2],
                    country =       row[3],
                    stateId =       row[4],
                    state =         row[5],
                    cityId =        row[6],
                    name =          row[7],
                    lat =           float(row[8]),
                    lon =           float(row[9]),
                    aliases =       row[10],
                    population =    int(row[11])
                )

                loc.save(pipe)
                
            except Exception, e:
                logging.exception("Could not import line %s: %s" ,line, e)
                fails+=1
                return
       	
	         
            i += 1
            if i % 1000 == 0:
                pipe.execute()
        pipe.execute()

        logging.info("Imported %d cities, failed %d times" , i, fails)
        print("Finished!")
        return True
