import sys,os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../src')
import unittest
import redis
from geodis.provider.geonames import GeonamesImporter
from geodis.provider.ip2location import IP2LocationImporter
from geodis.provider.zipcodes import ZIPImporter


from geodis.city import City
from geodis.iprange import IPRange
from geodis.zipcode import ZIPCode
from geodis import countries

class  TestGeodis(unittest.TestCase):
    def setUp(self):
        self.redisHost = 'localhost'
        self.redisPort = 6379
        self.redisDB = 8
    
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

        #resolve by textual search

        locs = City.getByName('springfield', r, 44.0462, -123.022, 'united states')

        self.assertTrue(len(locs)>0)
        self.assertTrue(locs[0].country == 'United States')
        self.assertTrue(locs[0].name == 'Springfield')
        self.assertTrue(locs[0].state == 'Oregon')


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

    def testCountryUtils(self):

        testData = [('Israel', 'IL', 294640), ( "Sweden", 'SE', '2661886'), ('United States', 'US', 6252001)]

        for name, code, cid in testData:

            self.assertEqual(countries.getCountryCodeByName(name), code)
            self.assertEqual(countries.getCountryNameByCode(code), name)
            self.assertEqual(countries.getCountryIdByName(name), int(cid))
            self.assertEqual(countries.getCountryIdByCode(code), int(cid))

            self.assertEqual(countries.getCountryNameById(cid), name)
            self.assertEqual(countries.getCountryCodeById(cid), code)

    def testNameCodeConversionReversable(self):
        transformed = [countries.getCountryNameByCode(countries.getCountryCodeByName(c)) for c in countries.countries.itervalues()]
        self.assertEqual(countries.countries.values(), transformed)
        transformed = [countries.getCountryCodeByName(countries.getCountryNameByCode(c)) for c in countries.countries.iterkeys()]
        self.assertEqual(countries.countries.keys(), transformed)


if __name__ == '__main__':
    
    import sys;sys.argv = ['', 'TestGeodis']
    unittest.main()
