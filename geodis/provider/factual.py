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
import re

from ..business import Business
from .importer import Importer

class BusinessImporter(Importer):
    
    def runImport(self):
        """
        File Format:
        47f2642f-a337-42e4-9a88-edc2f0709d89    Dominos Pizza North Park        1925 El Cajon Blvd      San Diego       CA      92104   (619) 294-4570          Food & Beverage > Restaurants > Pizza           32.755249
       -117.144707

        """
        
        
        try:
            fp = open(self.fileName)
        except Exception, e:
            logging.error("could not open file %s for reading: %s" ,self.fileName, e)
            return False
        
        self.reset(Business)
        
        pipe = self.redis.pipeline()
        reader = csv.reader(fp, delimiter='\t', quotechar = '"')
        
        
        
        i = 0
        fails = 0
        for row in reader:
            try:
                cat = row[8]
                if not re.match('^(%s)\s' % "|".join([re.escape(x) for x in (
                                                                           'Arts, Entertainment', 
                                                                           'Shopping', 
                                                                           'Food & Beverage'
                                                                          )]), 
                                cat):
                    
                    continue
                
                if row[10] and row[11]:
                    loc = Business (
                        name =  row[1],
                        address = row[2],
                        continent =     'North America',
                        country =       'United States',
                        city = row[3],
                        state = row[4],
                        zip = row[5],
                        category = row[9],
                        lat = row[10],
                        lon = row[11],
                        type = row[8]
                        
                    )
                    #print loc
                loc.save(pipe)
                
            except Exception, e:
                logging.exception("Could not import line %s: %s" ,row, e)
                fails+=1
                
            
            i += 1
            if i % 1000 == 0:
                print i
                pipe.execute()
        pipe.execute()

        logging.info("Imported %d businesses, failed %d times" , i, fails)
        print "Finished!"
        return True