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

#Importer for locations from ip2location.com databases


import csv
import logging
import redis

from .importer import Importer
from ..iprange import IPRange

class IP2LocationImporter(Importer):

    def runImport(self, reset = False):
        """
        File Format:
        "67134976","67135231","US","UNITED STATES","CALIFORNIA","LOS ANGELES","34.045200","-118.284000","90001"

        """
        
        try:
            fp = open(self.fileName)
        except Exception, e:
            logging.error("could not open file %s for reading: %s" ,self.fileName, e)
            return False
        
        if reset:
            print "Deleting old ip data..."
            self.redis.delete(IPRange._indexKey)

        print "Starting import..."
            
        reader = csv.reader(fp, delimiter=',', quotechar='"')
        pipe = self.redis.pipeline()

        i = 0
        for row in reader:
            
            try:
                #parse the row
                countryCode = row[3]
                rangeMin = int(row[0])
                rangeMax = int(row[1])
                lat = float(row[6])
                lon = float(row[7])

                #take the zipcode if possible
                try:
                    zipcode = row[8]
                except:
                    zipcode = ''


                #junk record
                if countryCode == '-' and (not lat and not lon):
                    continue
                    
                range = IPRange(rangeMin, rangeMax, lat, lon, zipcode)
                range.save(pipe)
                
            except Exception, e:
                logging.error("Could not save record: %s" , e)

            i += 1
            if i % 10000 == 0:
                logging.info("Dumping pipe. did %d ranges" , i)
                pipe.execute()

        pipe.execute()
        logging.info("Imported %d locations" , i)

        return i

            