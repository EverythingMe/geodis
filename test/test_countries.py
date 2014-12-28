from unittest import TestCase
from geodis.countries import *


class CountriesTestCase(TestCase):
    def testIds(self):
        for country in countries:
            if country.ISO3 in ('SCG', 'ANT'):
                continue
            self.assertTrue(country.id, 'Country {} has invalid id'.format(country))
            self.assertEqual(getNameById(country.id), country.name)
            self.assertEqual(get2LetterCodeById(country.id), country.ISO)
            self.assertEqual(get3LetterCodeById(country.id), country.ISO3)
        ids = [country.id for country in countries]
        assert len(set(ids)) == len(ids) - 1  # SCG, ANT have id = None

    def testNames(self):
        for country in countries:
            self.assertTrue(country.name, 'Country {} has invalid name'.format(country))
            self.assertEqual(getIdByName(country.name), country.id)
            self.assertEqual(get2LetterCodeByName(country.name), country.ISO)
            self.assertEqual(get3LetterCodeByName(country.name), country.ISO3)
        names = [country.name for country in countries]
        assert len(set(names)) == len(names)

    def test2LetterCodes(self):
        for country in countries:
            self.assertTrue(country.ISO, 'Country {} has invalid ISO'.format(country))
            self.assertEqual(getIdBy2LetterCode(country.ISO), country.id)
            self.assertEqual(getNameBy2LetterCode(country.ISO), country.name)
            self.assertEqual(get3LetterCodeBy2LetterCode(country.ISO), country.ISO3)
        ISOs = [country.ISO for country in countries]
        assert len(set(ISOs)) == len(ISOs)

    def test3LetterCodes(self):
        for country in countries:
            self.assertTrue(country.ISO3, 'Country {} has invalid ISO3'.format(country))
            self.assertEqual(getIdBy3LetterCode(country.ISO3), country.id)
            self.assertEqual(getNameBy3LetterCode(country.ISO3), country.name)
            self.assertEqual(get2LetterCodeBy3LetterCode(country.ISO3), country.ISO)
        ISO3s = [country.ISO3 for country in countries]
        assert len(set(ISO3s)) == len(ISO3s)
