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

__author__="dvirsky"
__date__ ="$Mar 25, 2011 4:44:22 PM$"

redis_host = 'localhost'
redis_port = 6379

def importGeonames(fileName):
    
    global redis_host, redis_port
    importer = GeonamesImporter(fileName, redis_host, redis_port)
    if not importer.runImport():
        print "Could not import geonames database..."
        sys.exit(1)

    sys.exit(0)





if __name__ == "__main__":

    #build options parser
    parser = OptionParser(usage="\n\n%prog [--import_geonames | --import_ip2location] --file=FILE", version="%prog 0.1")

    parser.add_option("-g", "--import_geonames", dest="import_geonames",
                      action='store_true', default=False,
                      help='Import locations from Geonames data dump')

    parser.add_option("-f", "--file", dest="import_file",
                  help="Location of the file we want to import", metavar="FILE")
    
    (options, args) = parser.parse_args()

    if options.import_geonames:
        importGeonames(options.import_file)