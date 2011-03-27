#performance benchmarks

import sys
import os
import redis
from iprange import IPRange
from city import City
import time

def benchResolveIPs(num):

    ips = ['166.205.138.92', '62.0.18.221',  '69.147.125.65', '188.127.241.156', '79.178.26.33']
    r = redis.Redis()
    nips = len(ips)
    for i in xrange(num):
        ip = ips[i % nips]
        loc = IPRange.getCity(ip, r)
        
    return num

def benchResolveCoords(num):

    coords = [(-3.03333,53.47778), (40.7226,-74.66544), (31.78199,35.2196), (0,0),(45,45)]
    r = redis.Redis()
    ncoords = len(coords)
    for i in xrange(num):
        lat,lon = coords[i % ncoords]
        loc = City.getByLatLon(lat,lon, r)
        

    return num

def benchSingleProc(func, num):

    print "Running benchmark %s for %d times..." % (func.__name__, num)
    st = time.time()
    num = func(num)
    et = time.time()

    print "time: %.03fsec, rate: %.03fq/s" % (et - st, (float(num) / (et-st)))
    
if __name__ == "__main__":


   benchSingleProc(benchResolveCoords, 10000)
   benchSingleProc(benchResolveIPs, 10000)