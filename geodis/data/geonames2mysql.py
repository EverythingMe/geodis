#!/usr/bin/python
'''
Created on May 30, 2011

@author: dor
'''

import MySQLdb
import logging
import time
from optparse import OptionParser
import re
import json

class Cols:
    geonameid =         0
    name =              1
    asciiname =         2 
    alternatenames =    3 
    latitude =          4
    longitude =         5
    feature_class =     6
    feature_code =      7
    country_code =      8
    cc2 =               9
    admin1_code =       10 
    admin2_code =       11
    admin3_code =       12
    admin4_code =       13
    population =        14
    elevation =         15
    gtopo3 =            16
    timezone =          17 
    modification_date = 18 
    
class FeatureType:
    world = 'World'
    continent = 'Continent'
    country = 'Country'
    region = state = 'Region'
    city = 'City'
    
    parents = {
        city: region,
        region: country,
        country: continent,
        continent: world
    }
    
featureCodes = {
                 'CONT':    FeatureType.continent,
                 
                 'PCL':     FeatureType.country,
                 'PCLI':    FeatureType.country,
                 'PCLD':    FeatureType.country,
                 'PCLF':    FeatureType.country,
                 'PCLIX':   FeatureType.country,
                 'PCLS':    FeatureType.country,
                 'TERR':    FeatureType.country,
                 
                 'ADM1':    FeatureType.region,
                 
                 'PPL':     FeatureType.city,
                 'PPLA':    FeatureType.city,
                 'PPLA2':   FeatureType.city,
                 'PPLC':    FeatureType.city,
                 'PPLS':    FeatureType.city
}

ids = {
       FeatureType.country: [Cols.country_code],
       FeatureType.region:  [Cols.country_code, Cols.admin1_code]
}

class GeonamesLoader:
    
    def __init__(self, **dbparams):
        
        self.names = {}
        self.links = {}
        
        self.db=MySQLdb.connect(**dbparams)
    
    def _loadAlternates(self, alternates):
        self.names = {}
        self.links = {}
        
        strengths = {}

        numeric = re.compile('^\d+$')

        for l in alternates.xreadlines():
            r = l.strip().split('\t')
            
            if r[2]=='en' and not numeric.match(r[3]):
                
                id = r[1]
                strength = 0
                l = len(r)

                if l>5 and r[5]=='1':
                    strength += 70
                    
                if l>4 and r[4]=='1':
                    strength += 30
                    
                if strength==100 or strength>strengths.get(id):
                    self.names[id] = r[3]
                    strengths[id] = strength
            
            elif r[2]=='link' and 'http://en.wikipedia.org' in r[3]:
                self.links[r[1]] = r[3]
                
    def _loadHierarchy(self, hierarchy):
        # reading hierarchy
        
        self.hierarchy = {}
        for l in hierarchy.xreadlines():
            r = l.strip().split('\t')
            if len(r)>2 and r[2]=='ADM':
                self.hierarchy[r[1]] = r[0]
            

    
    def load(self, allCountires, alternates, hierarchy):

        logging.info('Loading %s...' % alternates)
        self._loadAlternates(open(alternates))
        
        logging.info('Loading %s...' % hierarchy)
        self._loadHierarchy(open(hierarchy))
        
        ref = {}
        data = []
            
        logging.info('Loading %s...' % allCountires)
        for line in open(allCountires).xreadlines():
            r = line.split('\t')
            fc = r[Cols.feature_code] 
            #print r[Cols.name], fc
            
            if fc in featureCodes and \
                    (r[Cols.feature_class]!='P' or int(r[Cols.population])>=1000) and \
                    (r[Cols.feature_code]!='TERR' or int(r[Cols.gtopo3])>=0):
                
                if fc == 'TERR' and r[Cols.country_code] == 'AU':
                    print(r)
                    continue

                ft = featureCodes[fc]
                if ft in ids:
                    id = '_'.join([r[id] for id in ids[ft]])
                    ref[id] = r[Cols.geonameid]
                
                parentFT = FeatureType.parents.get(ft, None)
                tempParentId = '_'.join([r[id] for id in ids[parentFT]]) if parentFT in ids else None

                # skipping all entities inside Greater London except London itself
                if r[Cols.admin2_code]=='GLA' and r[Cols.geonameid]!='2643743':
                    continue
                
                gid = r[Cols.geonameid]
                data.append([
                             tempParentId, 
                             gid, 
                             self.names.get(gid, r[Cols.name]), 
                             r[Cols.longitude], 
                             r[Cols.latitude],
                             self.links.get(gid, None),
                             ft,
                             r[Cols.alternatenames],
                             r[Cols.population]
                            ])
                
        
        logging.info('Assigning parents...')
        for rec in data:
            if rec[0]:
                parentId = ref.get(rec[0], None)
                if not parentId and '_' in rec[0]:
                    parentId = ref.get(rec[0].split('_')[0], None)
                rec[0] = parentId
            
            if not rec[0]:
                rec[0] = self.hierarchy.get(rec[1], None)
                
                if not rec[0]:
                    logging.warn("Can't place '%s' (%s), skipping" % (rec[2], rec[1]))
                    continue
        
        logging.info('Commiting...')
        cur = self.db.cursor()
        cur.execute("SET FOREIGN_KEY_CHECKS=0")
        cur.execute('TRUNCATE locations')
        cur.execute("INSERT INTO locations (parentId, id, name, lon, lat, type) VALUES (%s, %s, %s, %s, %s, %s)", [None, '6295630', 'Worldwide', 0, 0, FeatureType.world])   
        cur.executemany("INSERT INTO locations (parentId, id, name, lon, lat, info, type, aliases, population) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", data)
        cur.execute('COMMIT')
        cur.execute("SET FOREIGN_KEY_CHECKS=1")
        return True

    def dump(self):
        logging.info('Dumping CSV')
        cur = self.db.cursor()
        cur.execute("""
            SELECT continent.id as continent_id, continent.name as continent_name, country.id as country_id, country.name as country_name, state.id as state_id,state.name as state_name,
            city.id as city_id, city.name as city_name, city.lat as lat, city.lon as lon, city.aliases as aliases, city.population as population,
            state.type as type2, country.type as type1, continent.type as type0 
            FROM locations city
	    JOIN locations state ON (city.parentId=state.id)
            JOIN locations country ON (state.parentId=country.id)
            JOIN locations continent ON (continent.id=country.parentId)
            WHERE city.type = 'City'
        """)
        
        for row in cur.fetchall():
            t = row[-3]
            record = map(str,row)[:-3]
            if t=='Country':
                record = record[2:]
                record.insert(4, '0')
                record.insert(5, '')
            
            print(json.dumps(record, ensure_ascii=False))
            
        return True

if __name__ == '__main__':
    
    logging.basicConfig(level=logging.DEBUG)
    
    parser = OptionParser()#usage="\n\n%prog [--import_geonames | --import_ip2location] --file=FILE", version="%prog 0.1")

    parser.add_option("-i", "--import_geonames", dest="import_geonames",
                      action='store_true', default=False,
                      help='Import locations from Geonames data dump to mysql')

    parser.add_option("-x", "--export_csv", dest="export_csv",
                      action='store_true', default=False,
                      help='Export locations to csv')
    
    parser.add_option("-D", "--dir", dest="import_dir",
                  help="Location of the files we want to import", metavar="DIR")

    parser.add_option("-H", "--host", dest="host", default = 'localhost',
                      help="mysql host to use", metavar="HOST")

    parser.add_option("-P", "--port", dest="port", default = 3306,
                      type="int", help="mysql port to use", metavar="PORT")

    parser.add_option("-u", "--user", dest="user", default = 'root',
                      help="mysql user", metavar="USER")
    
    parser.add_option("-p", "--password", dest="passwd", default = '',
                      help="mysql password", metavar="PASSWD")
    
    parser.add_option("-d", "--database", dest="database", default = 'doat',
                      help="mysql database", metavar="DB")

    start = time.time()    
    try:
        (options, args) = parser.parse_args()
        loader = GeonamesLoader(host=options.host, port=options.port, user=options.user, passwd=options.passwd, db=options.database)
        if options.import_geonames:
            dir = options.import_dir
            loader.load('%s/allCountries.txt'%dir, '%s/alternateNames.txt'%dir, '%s/hierarchy.txt'%dir)
        elif options.export_csv:
            loader.dump()
        
        logging.info('Done')
    except Exception:
        logging.exception("Error")
    logging.info('Operation took %s seconds' % (time.time() - start))
