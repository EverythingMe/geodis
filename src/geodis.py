#!/usr/bin/python

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

import redis
import logging
import sys
from optparse import OptionParser

from provider.geonames import GeonamesImporter
from provider.ip2location import IP2LocationImporter
from provider.zipcodes import ZIPImporter
from iprange import IPRange
from city import City
from zipcode import ZIPCode

import us_states

__author__="dvirsky"
__date__ ="$Mar 25, 2011 4:44:22 PM$"

redis_host = 'localhost'
redis_port = 6379
redis_db = 8

def importGeonames(fileName):
    
    global redis_host, redis_port, redis_db
    importer = GeonamesImporter(fileName, redis_host, redis_port, redis_db)
    if not importer.runImport():
        print "Could not import geonames database..."
        sys.exit(1)

    


def importIP2Location(fileName):

    global redis_host, redis_port, redis_db
    importer = IP2LocationImporter(fileName, redis_host, redis_port, redis_db)
    if not importer.runImport(True):
        print "Could not import geonames database..."
        sys.exit(1)


def importZIPCode(fileName):

    global redis_host, redis_port, redis_db
    importer = ZIPImporter(fileName, redis_host, redis_port, redis_db)
    if not importer.runImport():
        print "Could not import geonames database..."
        sys.exit(1)

    
def resolveIP(ip):
    global redis_host, redis_port, redis_db
    r = redis.Redis(host = redis_host, port = redis_port, db = redis_db)

    loc = IPRange.getZIP(ip, r)
    print loc
    

def resolveCoords(lat, lon):
    global redis_host, redis_port, redis_db
    r = redis.Redis(host = redis_host, port = redis_port, db = redis_db)
    loc = City.getByLatLon(lat, lon, r)
    print loc


if __name__ == "__main__":
    
    
    
    logging.basicConfig(
                level = logging.INFO,
                format='%(asctime)s %(levelname)s in %(module)s.%(funcName)s (%(filename)s:%(lineno)s): %(message)s',
                )
    #build options parser
    parser = OptionParser(usage="\n\n%prog [--import_geonames | --import_ip2location] --file=FILE", version="%prog 0.1")

    parser.add_option("-g", "--import_geonames", dest="import_geonames",
                      action='store_true', default=False,
                      help='Import locations from Geonames data dump')

    parser.add_option("-i", "--import_ip2coutnry", dest="import_ip2location",
                      action='store_true', default=False,
                      help='Import ip ranges from ip2country.com dumps')
    
    parser.add_option("-z", "--import_zipcodes", dest="import_zipcodes",
                      action='store_true', default=False,
                      help='Import zipcodes')

    parser.add_option("-f", "--file", dest="import_file",
                  help="Location of the file we want to import", metavar="FILE")
    
    parser.add_option("-d", "--dir", dest="import_dir",
                  help="Location of the files we want to import", metavar="DIR")

    parser.add_option("-P", "--resolve_ip", dest="resolve_ip", default = None,
                      help="resolve an ip address to location", metavar="IP_ADDR")


    parser.add_option("-L", "--resolve_latlon", dest="resolve_latlon", default = None,
                      help="resolve an lat,lon pair into location", metavar="LAT,LON")


    parser.add_option("-H", "--redis_host", dest="redis_host", default = 'localhost',
                      help="redis host to use", metavar="HOST")

    parser.add_option("-p", "--redis_port", dest="redis_port", default = 6379,
                      type="int", help="redis port to use", metavar="PORT")

    parser.add_option("-n", "--redis_database", dest="redis_db", default = 8,
                      type="int", help="redis database to use (default 8)", metavar="DB_NUM")
    
    (options, args) = parser.parse_args()
    redis_host = options.redis_host
    redis_port = options.redis_port
    redis_db = options.redis_db
    
    if options.import_geonames:
        importGeonames(options.import_file)
        
    elif options.import_ip2location:
        importIP2Location(options.import_file)

    elif options.import_zipcodes:
        importZIPCode(options.import_file)
        
    elif options.resolve_ip:
        resolveIP(options.resolve_ip)
        
    elif options.resolve_latlon:
        coords = [float(p) for p in options.resolve_latlon.split(',')]
        resolveCoords(*coords)

    print "Success!"
    sys.exit(0)
