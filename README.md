[![Build Status](https://travis-ci.org/EverythingMe/geodis.svg?branch=master)](https://travis-ci.org/EverythingMe/geodis)

# Geodis - a Redis based geo resolving library


* * * * * *

Geodis is a simple and fast python module that allows you to convert IP addresses and latitude/longitude
coordinates into geographical locations such as cities, zipcodes and countries.

It currently supports cities worldwide, and zipcode areas in the US (of course each of these includes higher level data such as country).
But it is written in an extensible way, so that adding a new layer of objects and indexing them is very simple.

Geodis is fast, since it uses redis, which is a very fast in memory database, and geohashing to index coordinates.

A single thread, single process python program can resolve about 2000 ips and 3000 lat/lon pairs per second on
a regular desktop machine, when the database is fully loaded with IP ranges, zipcodes and all major cities in the world.

# Geodis - Getting started

Before you jump into python shell to test geodis , you must first ensure that redis server is running and on which port.
If you do not have a clue how to get started with redis-server [here is a link](https://redis.io/topics/quickstart) to get started, download install.

once redis-server is up and running you can test in python shell as shown below:

    >>> import redis
    >>> rs = redis.Redis("localhost")
    >>> rs
    Redis<ConnectionPool<Connection<host=localhost,port=6379,db=0>>>

The above line showing host and port ensures that redis server is running and accepting incoming connections at port `6379`.


USAGE
------------------------
    >>> import redis
    >>> import geodis.city
    >>> conn = redis.Redis()

    #getting a city by lat,lon
    >>> print geodis.city.City.getByLatLon(31.78,35.21, conn)
    Location: {'name': 'West Jerusalem', 'country': 'Israel', 'lon': '35.21961', 'zipcode': '', 'state': 'Jerusalem District', 'lat': '31.78199'}

    #getting a location by ip
    >>> print geodis.iprange.IPRange.getCity('62.219.0.221', '62.219.0.221', 31.78, 35.21, conn)
    Location: {'name': 'West Jerusalem', 'country': 'Israel', 'lon': '35.21961', 'zipcode': '', 'state': 'Jerusalem District', 'lat': '31.78199'}


Geodis can also be used as a command line utility
------------------------
    $ geodis -P  188.127.241.156 -p 6379
    Location: {'name': 'Crosby', 'country': 'United Kingdom', 'lon': '-3.03333', 'zipcode': '', 'state': 'England', 'key': 'loc:crosby:united kingdom:england:', 'lat': '53.47778'}

    $ geodis -L  40.90732,-74.07514 -p 6379
    Location: {'name': 'Rochelle Park', 'country': 'United States', 'lon': '-74.07514', 'zipcode': '', 'state': 'New Jersey', 'key': 'loc:rochelle park:united states:new jersey:', 'lat': '40.90732'}

IMPORTING DATA
------------------------
Geodis needs to import its data into redis. In the data folder you will find a list of all cities in the world, and a zipcode database.

The data files should be where the geodis files are installed if you've installed from pip (e.g `/usr/local/lib/python2.7/site-packages/geodis/data/cities1000.json`), or in the source tree if you've cloned this repo.

data is imported using a utility called geodis.py. run ./geodis.py --help for more details on importing it.

Examples:

* Cities are imported by running
      
        geodis -g -f <data directory>/cities1000.json -p 6379
    
* Zipcodes are imported by running
     
        geodis -z -f <data directory>/zipcode.csv -p 6379


** *IMPORTANT*: IP to location data is not provided, you need to buy an ip resolving database that can resolve ip ranges to lat,lon pairs **

Refreshing countries mapping:
------------------------
The data is already generated but if you ever need to update, use:

        python external/geonames/update.py > geodis/countries.py


INSTALLING:
------------------------

* `pip install geodis`


RUNNING:
------------------------
1. Install geodis

2. Install redis

3. Import data as described above.

