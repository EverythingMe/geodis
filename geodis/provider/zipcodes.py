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
            logging.error("could not open file %s for reading: %s" % (self.fileName, e))
            return False

        reader = csv.reader(fp, delimiter=',', quotechar = '"')
        pipe = self.redis.pipeline()

        i = 0
        for row in reader:

            try:
                name = row[0]
                city = row[1]
                stateCode = row[2]
                lat = float(row[3])
                lon = float(row[4])
                state = stateCode#code_to_state.get(stateCode, '').title()
                country = 'US'

                loc = ZIPCode(name = name,
                              city = city,
                                country = country,
                                state = state,
                                lat = lat,
                                lon = lon)

                loc.save(pipe)

                
                
            except Exception, e:
                logging.error("Could not import line %s: %s" % (row, e))
            i += 1
            if i % 1000 == 0:
                pipe.execute()

        pipe.execute()

        logging.info("Imported %d locations" % i)

        return i
