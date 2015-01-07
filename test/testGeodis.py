import sys,os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../src')
import unittest
import redis
import os
from geodis.provider.geonames import GeonamesImporter
from geodis.provider.ip2location import IP2LocationImporter
from geodis.provider.zipcodes import ZIPImporter


from geodis.city import City
from geodis.iprange import IPRange
from geodis.zipcode import ZIPCode
from geodis import countries


atdir = lambda *f: os.path.join(os.path.abspath(os.path.dirname(__file__)), *f)


class TestGeodis(unittest.TestCase):
    def setUp(self):
        self.redisHost = os.getenv('TEST_REDIS_HOST', 'localhost')
        self.redisPort = int(os.getenv('TEST_REDIS_PORT', '6375'))
        self.redisDB = int(os.getenv('TEST_REDIS_DBNUMBER', '8'))
        self.redis = redis.Redis(self.redisHost, self.redisPort, self.redisDB)
    
    def test1_ImportGeonames(self):

        importer = GeonamesImporter(atdir('data/cities.json'), self.redisHost, self.redisPort, self.redisDB)
        self.assertGreater(importer.runImport(), 0, 'Could not import cities json')

    def test2_ImportIP2Location(self):

        importer = IP2LocationImporter(atdir('data/ip2location.csv'), self.redisHost, self.redisPort, self.redisDB)
        self.assertGreater(importer.runImport(), 0, 'Could not import ip ranges csv')

    def test3_ImportZIP(self):
        importer = ZIPImporter(atdir('data/zipcodes.csv'), self.redisHost, self.redisPort, self.redisDB)
        self.assertGreater(importer.runImport(), 0, 'Could not import zipcodes csv')

    def test4_resolve_by_coords(self):
        loc = City.getByLatLon(34.05223, -118.24368, self.redis)

        self.assertIsNotNone(loc)

        self.assertEqual(loc.country, 'United States')
        self.assertIn(loc.state, ('CA', 'California'))

    def test5_resolve_by_textual_search(self):
        locs = City.getByName('springfield', self.redis, 44.0462, -123.022, 'united states')

        self.assertGreater(len(locs), 0)
        self.assertEqual(locs[0].country, 'United States')
        self.assertEqual(locs[0].name, 'Springfield')
        self.assertEqual(locs[0].state, 'Missouri')

    def test6_resolve_by_ip(self):
        loc = IPRange.getCity('4.3.68.1', self.redis)

        self.assertIsNotNone(loc)
        self.assertEqual(loc.country, 'United States')
        self.assertIn(loc.state, ('CA', 'California'))

    def test7_resolve_zip_by_lat_lon(self):
        loc = ZIPCode.getByLatLon(34.0452, -118.284, self.redis)

        self.assertIsNotNone(loc)
        self.assertEqual(loc.name, '90006')
        self.assertEqual(loc.country, 'United States')
        self.assertIn(loc.state, ('CA', 'California'))

    def test8_resolve_zip_by_ip(self):
        loc = IPRange.getZIP('4.3.68.1', self.redis)

        self.assertIsNotNone(loc)
        self.assertEqual(loc.name, '90001')
        self.assertEqual(loc.country, 'United States')
        self.assertIn(loc.state, ('CA', 'California'))

    def testCountryUtils(self):
        testData = [('Israel', 'IL', 294640), ( "Sweden", 'SE', '2661886'), ('United States', 'US', 6252001)]

        for name, code, cid in testData:

            self.assertEqual(countries.get2LetterCodeByName(name), code)
            self.assertEqual(countries.getNameBy2LetterCode(code), name)
            self.assertEqual(countries.getIdByName(name), int(cid))
            self.assertEqual(countries.getIdBy2LetterCode(code), int(cid))

            self.assertEqual(countries.getNameById(cid), name)
            self.assertEqual(countries.get2LetterCodeById(cid), code)

    def testNameCodeConversionReversable(self):
        countryNames = [c.name for c in countries.countries]
        countryCodes = [c.ISO for c in countries.countries]

        transformed = [countries.getNameBy2LetterCode(countries.get2LetterCodeByName(c)) for c in countryNames]
        self.assertEqual(countryNames, transformed)

        transformed = [countries.get2LetterCodeByName(countries.getNameBy2LetterCode(c)) for c in countryCodes]
        self.assertEqual(countryCodes, transformed)


if __name__ == '__main__':
    import sys
    sys.argv = ['', 'TestGeodis']

    unittest.main()
