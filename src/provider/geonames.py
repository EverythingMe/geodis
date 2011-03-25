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

from location import Location
import csv
import logging
import redis
import re
from countries import countries


class GeonamesImporter(object):
    
    def __init__(self, fileName, redisHost, redisPort):
        """
        Init a geonames cities importer
        @param fileName path to the geonames datafile
        @param redisConn redis connection
        """
        fileNames = fileName.split(',')
        self.fileName = fileNames[0]
        self.adminCodesFileName = fileNames[1] if len(fileNames) > 1 else None
        self.redis = redis.Redis(host = redisHost, port = redisPort)
        self._adminCodes = {}
        
    def _readAdminCodes(self):
        """
        Read administrative codes for states and regions
        """

        if not self.adminCodesFileName:
            logging.warn("No admin codes file name. You won't have state names etc")
            return

        try:
            fp = open(self.adminCodesFileName)
        except Exception, e:
            logging.error("could not open file %s for reading: %s" % (self.adminCodesFileName, e))
            return

        reader = csv.reader(fp, delimiter='\t')
        for row in reader:
            
            self._adminCodes[row[0].strip()] = row[1].strip()
            

    def runImport(self):
        """
        File Format:
        5368361 Los Angeles     Los Angeles     Angelopolis,El Pueblo de Nu....     34.05223        -118.24368      P       PPL
        US              CA      037                     3694820 89      115     America/Los_Angeles     2009-11-02

        """

        self._readAdminCodes()

        try:
            fp = open(self.fileName)
        except Exception, e:
            logging.error("could not open file %s for reading: %s" % (self.fileName, e))
            return False

        reader = csv.reader(fp, delimiter='\t')
        pipe = self.redis.pipeline()

        i = 0
        for row in reader:

            try:
                name = row[2]
                
                country = row[8]
                adminCode = '.'.join((country, row[10]))
                region = re.sub('\\(.+\\)', '', self._adminCodes.get(adminCode, '')).strip()
                
                if country == 'US' and not region:
                    region = row[10]

                lat = float(row[4])
                lon = float(row[5])

                loc = Location(name = name,
                                country = country,
                                state = region,
                                lat = lat,
                                lon = lon)

                loc.save(pipe)

                
                
            except Exception, e:
                logging.error("Could not import line %s: %s" % (row, e))
            i += 1
            if i % 1000 == 0:
                pipe.execute()

        logging.info("Imported %d locations" % i)

        return True