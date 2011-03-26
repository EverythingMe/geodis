# Copyright 2010 (c) doit9.com
# Copying and/or distribution of this file is prohibited.

import unittest
import redis
from provider.geonames import GeonamesImporter
from provider.ip2location import IP2LocationImporter
from location import Location
from iprange import IPRange

class  TestProvidersTestCase(unittest.TestCase):
    def setUp(self):
        self.redisHost = 'localhost'
        self.redisPort = 6379
    
    def test1_ImportGeonames(self):

        importer = GeonamesImporter('./data/locations.csv', self.redisHost, self.redisPort)
        self.assertTrue(importer.runImport() > 0, 'Could not import locations csv')

        

    def test2_ImportIP2Location(self):

        importer = IP2LocationImporter('./data/ip2location.csv', self.redisHost, self.redisPort)
        self.assertTrue(importer.runImport() > 0, 'Could not import ip ranges csv')

    def test3_resolve(self):
        r = redis.Redis(self.redisHost, self.redisPort)
        #resolve by coords
        loc = Location.getByLatLon(34.61, -117.82, r)
        self.assertTrue(loc is not None)
        self.assertTrue(loc.country == 'United States')
        self.assertTrue(loc.state == 'CA')

        #resolve by ip
        ip = '4.3.32.1'

        loc = IPRange.getLocation(ip, r)
        self.assertTrue(loc is not None)
        self.assertTrue(loc.country == 'United States')
        self.assertTrue(loc.state == 'CA')
        
if __name__ == '__main__':
    unittest.main()

