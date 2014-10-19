Geodis - a Redis based geo resolving library
------------------------------------------------------------------------

Geodis is a simple and fast python module that allows you to convert IP addresses and latitude/longitude
coordinates into geographical locations such as cities, zipcodes and countries.

It currently supports cities worldwide, and zipcode areas in the US (of course each of these includes higher level data such as country).
But it is written in an extensible way, so that adding a new layer of objects and indexing them is very simple.

Geodis is fast, since it uses redis, which is a very fast in memory database, and geohashing to index coordinates.

a single thread, signle process python program can resolve about 2000 ips and 3000 lat/lon pairs per second on
a regular desktop machine, when the database is fully loaded with IP ranges, zipcodes and all major cities in the world.


USAGE
------------------------
    >>> import redis
    >>> import geodis
    >>> conn = redis.Redis()

    #getting a city by lat,lon
    >>> print geodis.City.getByLatLon(31.78,35.21, conn)
    Location: {'name': 'West Jerusalem', 'country': 'Israel', 'lon': '35.21961', 'zipcode': '', 'state': 'Jerusalem District', 'lat': '31.78199'}

    #getting a location by ip
    >>> print geodis.IPRange.getCity('62.219.0.221', conn)
    Location: {'name': 'West Jerusalem', 'country': 'Israel', 'lon': '35.21961', 'zipcode': '', 'state': 'Jerusalem District', 'lat': '31.78199'}


Geodis can also be used as a command line utility
------------------------
    $ ./geodis.py -p  188.127.241.156
    Location: {'name': 'Crosby', 'country': 'United Kingdom', 'lon': '-3.03333', 'zipcode': '', 'state': 'England', 'key': 'loc:crosby:united kingdom:england:', 'lat': '53.47778'}

    $ ./geodis.py -l  40.90732,-74.07514
    Location: {'name': 'Rochelle Park', 'country': 'United States', 'lon': '-74.07514', 'zipcode': '', 'state': 'New Jersey', 'key': 'loc:rochelle park:united states:new jersey:', 'lat': '40.90732'}

IMPORTING DATA
------------------------
Geodis needs to import its data into redis.
In the data folder you will find a list of all cities in the world, and a zipcode database.

    *IMPORTANT*: IP to location data is not provided, you need to buy an ip resolving database that can resolve ip ranges to lat,lon pairs

data is imported using a utility called geodis.py. run ./geodis.py --help for more details on importing it.


REUIREMENTS:
------------------------

* redis-server

    get it at http://redis.io


* redis-py

    http://github.com/andymccurdy/redis-py

    install it with *easy_install redis*

    optionally: run easy_install hiredis (binary module that accelerates stuff if it exists)

* geohasher

    A geohashing python module.

    can be installed with *easy_install geohasher*
