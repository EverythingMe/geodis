"""
Generate geodis/countries.py from a TSV dump at geonames.org

The generated code is part of the repository, if you ever wish to update it, run this again.
"""

import urllib
import csv
import itertools
import collections

url = 'http://download.geonames.org/export/dump/countryInfo.txt'
fields = 'ISO', 'ISO3', 'ISOnumeric', 'fips', 'name', 'capital', 'area', 'population', 'continent', 'tld', 'currencyCode', 'currencyName', 'phone', 'postalCodeFormat', 'postalCodeRegex', 'languages', 'id', 'neighbours', 'equivalentFipsCode'
split_to_set = lambda s: set(s.split(','))
types = {
    'area': float,
    'id': int,
    'population': int,
    'ISOnumeric': int,
    'languages': split_to_set,
    'neighbours': split_to_set
}

f = urllib.urlopen(url)
Country = collections.namedtuple('Country', fields)
source = itertools.dropwhile(lambda l: l.startswith('#'), f)
reader = csv.DictReader(source, fields, delimiter='\t')

print('import collections')
print('Country = collections.namedtuple(\'Country\', {})'.format(fields))
print('countries = [')

for line in reader:
    for field in fields:
        t = types.get(field, str)
        attr = line[field].strip()
        line[field] = t(attr) if attr else None
    print ('    {},'.format(Country(**line)))

print (']')

# Generate getters (i.e: getIdByName, get2LetterCodeById)
_attrs = ('Id', 'id'), ('Name', 'name'), ('2LetterCode', 'ISO'), ('3LetterCode', 'ISO3')
for attr in _attrs:
    print
    print
    lookup = 'countriesBy{}'.format(attr[0])
    print ('{} = {{c.{}: c for c in countries}}'.format(lookup, attr[1]))

    others = set(_attrs) - {attr}
    for other in others:
        print
        print
        print ('''def get{other[0]}By{attr[0]}({attr[1]}):
    """Get country {other[0]} by {attr[0]}"""
    return {lookup}[{attr[1]}].{other[1]}'''.format(other=other, attr=attr, lookup=lookup))
