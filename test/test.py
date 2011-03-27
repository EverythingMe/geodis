
import unittest
import redis
from provider.geonames import GeonamesImporter
from provider.ip2location import IP2LocationImporter
from provider.zipcodes import ZIPImporter


from city import City
from iprange import IPRange
from zipcode import ZIPCode

class  TestProvidersTestCase(unittest.TestCase):
    def setUp(self):
        self.redisHost = 'localhost'
        self.redisPort = 6379
        self.redisDB = 0
    
    def test1_ImportGeonames(self):

        importer = GeonamesImporter('./data/locations.csv', self.redisHost, self.redisPort, self.redisDB)
        self.assertTrue(importer.runImport() > 0, 'Could not import cities csv')

        

    def test2_ImportIP2Location(self):

        importer = IP2LocationImporter('./data/ip2location.csv', self.redisHost, self.redisPort, self.redisDB)
        self.assertTrue(importer.runImport() > 0, 'Could not import ip ranges csv')


    def test3_ImportZIP(self):

        importer = ZIPImporter('./data/zipcodes.csv', self.redisHost, self.redisPort, self.redisDB)
        self.assertTrue(importer.runImport() > 0, 'Could not import zipcodes csv')

    def test4_resolve(self):
        r = redis.Redis(self.redisHost, self.redisPort, self.redisDB)
        #resolve by coords
        
        loc = City.getByLatLon(34.05223, -118.24368, r)
        
        self.assertTrue(loc is not None)
        self.assertTrue(loc.country == 'United States')
        self.assertTrue(loc.state == 'CA' or loc.state == 'California')

        #resolve by ip
        ip = '4.3.68.1'

        loc = IPRange.getCity(ip, r)
        
        self.assertTrue(loc is not None)
        self.assertTrue(loc.country == 'United States')
        self.assertTrue(loc.state == 'CA' or loc.state == 'California')

        #resolve zip by lat,lon
        loc = ZIPCode.getByLatLon(34.0452, -118.284, r)
        
        self.assertTrue(loc is not None)
        self.assertTrue(loc.name == '90006')
        self.assertTrue(loc.country == 'United States')
        self.assertTrue(loc.state == 'CA' or loc.state == 'California')

        #resolve zip bu ip
        loc = IPRange.getZIP(ip, r)
        self.assertTrue(loc is not None)
        self.assertTrue(loc.name == '90001')
        self.assertTrue(loc.country == 'United States')
        self.assertTrue(loc.state == 'CA' or loc.state == 'California')
        

        
if __name__ == '__main__':
    unittest.main()

