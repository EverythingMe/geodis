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


import csv
import logging
import redis

from iprange import IPRange

class IP2LocationImporter(object):

    def __init__(self, fileName, redisHost, redisPort):
        """
        Init a geonames cities importer
        @param fileName path to the geonames datafile
        @param redisConn redis connection
        """
        self.fileName = fileName
        self.redis = redis.Redis(host = redisHost, port = redisPort)

    def runImport(self):
        """
        File Format:
        "50331648","50331903","US","UNITED STATES","MASSACHUSETTS","BEVERLY","42.5685","-70.8619"

        """

        try:
            fp = open(self.fileName)
        except Exception, e:
            logging.error("could not open file %s for reading: %s" % (self.fileName, e))
            return False

        reader = csv.reader(fp, delimiter=',', quotechar='"')
        pipe = self.redis.pipeline()

        i = 0
        for row in reader:

            try:
                rangeMin = row[0]
                rangeMax = row[1]
                lat = float(row[7])
                lon = float(row[8])
                logging.info("Indexing range %s-%s, %s,%s" % (rangeMin, rangeMax, lat,lon))

                range = IPRange(rangeMin, rangeMin, lat, lon)
                range.save(pipe)
            except Exception, e:
                logging.error("Could not save record: %s" % e)

            i += 1
            if i % 1000 == 0:
                pipe.execute()

        logging.info("Imported %d locations" % i)

        return i

            