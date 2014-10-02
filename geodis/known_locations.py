__author__ = 'dvirsky'

import math
import logging
import time


def distance(x, y):


    R = 6371000
    dLat = math.radians(y[0]-x[0])
    dLon = math.radians(y[1]-x[1])
    a = math.sin(dLat/2) * math.sin(dLat/2) + \
        math.cos( math.radians(x[0])) * math.cos( math.radians(y[0])) * \
        math.sin(dLon/2) * math.sin(dLon/2);

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c


#This is the "epoch" we're starting to count from. right now - 180 days ago
BASE_TS = 1388534400

class KnownLocation(object):

    def timestamp_to_score(self, timestamp):
        """
        Convert a hit timestamp to score
        """
        t = float(timestamp - BASE_TS)/(30*86400)
        return math.exp(t)/t

    def __init__(self, lat, lon, timestamp):
        self.lat = lat
        self.lon = lon
        self.score = self.timestamp_to_score(timestamp)
        self.numHits = 1
        self.lastHit = timestamp

    def distance(self, lat,lon):

        return distance((self.lat, self.lon), (lat,lon))


    def addHit(self, lat,lon, timestamp):
        """
        Add a hit to a known location - moving its center and updating its score
        """
        newLat = (self.lat*self.numHits + lat)/float(self.numHits+1)
        newLon = (self.lon*self.numHits + lon)/float(self.numHits+1)

        self.lat, self.lon = newLat, newLon
        self.numHits+=1
        self.score += self.timestamp_to_score(timestamp)

        self.lastHit = timestamp


    def __eq__(self, other):
        return id(self) == id(other)



"""
0 => 32.0804114505 34.8073404525 Hits: 3275 Score: 118001.20496 Last visited: 1.67048128896 days ago
1 => 32.0793257678 34.7956057502 Hits: 3267 Score: 84767.0812153 Last visited: 1.88272666043 days ago
2 => 32.0822170918 34.805609142 Hits: 293 Score: 9127.44901531 Last visited: 2.29248360591 days ago
3 => 32.0784376697 34.8086620127 Hits: 142 Score: 3961.80047383 Last visited: 5.86808545881 days ago
4 => 32.0859034074 34.779212775 Hits: 136 Score: 2469.45442039 Last visited: 32.1822521265 days ago
5 => 32.0913286933 34.78261102 Hits: 15 Score: 1112.4155664 Last visited: 11.2593817575 days ago
6 => 32.0823270225 34.7955078275 Hits: 40 Score: 771.439601612 Last visited: 5.1520090734 days ago
7 => 32.0830055846 34.7925382308 Hits: 13 Score: 287.216455065 Last visited: 4.88524981517 days ago
8 => 32.06109444 34.78727392 Hits: 5 Score: 214.089458005 Last visited: 6.91795814955 days ago
9 => 32.0514053 34.76908465 Hits: 2 Score: 10.0928654386 Last visited: 132.656627132 days ago"""

class KnowLocationDetector(object):


    MAX_RADIUS = 250 #meters
    MAX_CANDIDATES = 5
    MAX_TOP = 20

    def __init__(self):

        self.top_locations = []
        self.candidates = []

    def find_closest(self, location_list, lat,lon):

        candidate = None
        for loc in location_list:
            dist = loc.distance(lat,lon)
            if dist <= self.MAX_RADIUS :

                if candidate is None or loc.score > candidate[2]:
                    candidate = (loc, dist, loc.score)

        return candidate[0] if candidate else None


    def add_location(self, lat, lon, timestamp):
        """
        Add a location to the detector, updating scores and all
        """

        #find out if we're in a known location
        closest = self.find_closest(self.top_locations, lat, lon)
        if closest:
            logging.info("Found a known location, adding to it")
            closest.addHit(lat,lon, timestamp)
            return


        #find out if we're in a candidate
        closest = self.find_closest(self.candidates, lat, lon)
        if closest:
            logging.info("Found a candidate, adding to it")
            closest.addHit(lat,lon, timestamp)
        else:
            #we're dealing with a new location, we'll add it as a candidate
            logging.info("Creating a new candidate %f,%f", lat,lon)
            closest = KnownLocation(lat,lon,timestamp)

            #we're still filling the top locations, so no need to add as candidate
            if len(self.top_locations) < self.MAX_TOP:
                self.top_locations.append(closest)
            else:
                self.candidates.append(closest)

        #see if we can promote a candidate to the top locations
        if len(self.candidates) > 0:
            self.check_candidates()

    def check_candidates(self):
        """
        see if we need to promote a candidate and pop it from the top queue
        """
        topCandidate = max(self.candidates, key = lambda  loc: loc.score)
        bottomKnown = min(self.top_locations, key = lambda loc: loc.score)

        if topCandidate.score > bottomKnown.score:
            logging.info("Promoting candidate to known!")
            self.candidates.remove(topCandidate)
            self.top_locations.remove(bottomKnown)
            self.top_locations.append(topCandidate)
            self.candidates.append(bottomKnown)


        while len(self.candidates) > self.MAX_CANDIDATES:
            self.candidates.remove(min(self.candidates, key=lambda loc: loc.lastHit))





if __name__ == '__main__':
    #logging.basicConfig(level=0)
    import csv
    import datetime, time
    detector = KnowLocationDetector()

    seen = set()

    for i, row in enumerate(csv.reader(open('/home/dvirsky/Downloads/danjadevice.csv'), delimiter='\t')):
        if i == 0:
            continue

        date, latlon = row

        date = date.partition('.')[0]
        ts = time.mktime(time.strptime(date, '%Y-%m-%d %H:%M:%S'))

        if ts//10 in seen:
            continue
        seen.add(ts//10)

        lat,lon = map(float, latlon.split(","))

        detector.add_location(lat,lon, ts)

        print "tsi.setValue(%d000L); ctx.onEvent(new LocationEvent(new GeoLocation(%ff,%ff,1f)));" % (ts, lat,lon)



    aggScroe = 1#sum((x.score for x in detector.top_locations))
    for i, loc in enumerate(sorted(detector.top_locations[:10], key=lambda loc:loc.score, reverse=True)):
        print i, "=>", loc.lat, loc.lon, "Hits:", loc.numHits, "Score:", loc.score/aggScroe, "Last visited:", (time.time()-loc.lastHit)/86400, "days ago"

