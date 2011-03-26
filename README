Geodis - a Redis based geo resolving library
------------------------------------------------------------------------

Geodis is a simple python module that allows you to import locations
(currently only cities) and geographical IP ranges into Redis, a fast in-memory NoSQL database.

It is able to resolve either lat,lon coordinates into city, region and country (based on the closest match),
and/or resolve IP addresses into the same location objects.

Geodis is fast - a single thread, signle process python program can resolve about 1500 locations per second on
a desktop machine, when the database is fully loaded with IP ranges and all major cities in the world.


USAGE
------------------------
    >>> import redis
    >>> import geodis
    >>> conn = redis.Redis()

    #getting a location by lat,lon
    >>> print geodis.Location.getByLatLon(31.78,35.21, conn)
    Location: {'name': 'West Jerusalem', 'country': 'Israel', 'lon': '35.21961', 'zipcode': '', 'state': 'Jerusalem District', 'lat': '31.78199'}

    #getting a location by ip
    >>> print geodis.IPRange.getLocation('62.219.0.221', conn)
    Location: {'name': 'West Jerusalem', 'country': 'Israel', 'lon': '35.21961', 'zipcode': '', 'state': 'Jerusalem District', 'lat': '31.78199'}


Geodis can also be used as a command line utility
------------------------
    $ ./geodis.py -p  188.127.241.156
    Location: {'name': 'Crosby', 'country': 'United Kingdom', 'lon': '-3.03333', 'zipcode': '', 'state': 'England', 'key': 'loc:crosby:united kingdom:england:', 'lat': '53.47778'}

    $ ./geodis.py -l  40.90732,-74.07514
    Location: {'name': 'Rochelle Park', 'country': 'United States', 'lon': '-74.07514', 'zipcode': '', 'state': 'New Jersey', 'key': 'loc:rochelle park:united states:new jersey:', 'lat': '40.90732'}

IMPORTING DATA
------------------------
Geodis needs to import its data into redis. In the data folder you will find a list of all cities in the world.
*IMPORTANT*: IP to location data is not provided, you need to buy an ip resolving database that can resolve ip ranges to lat,lon pairs
run geodis.py --help for more details


REUIREMENTS:
------------------------

* redis-server
    get it at http://redis.io


* redis-py
    http://github.com/andymccurdy/redis-py
    install it with easy_install redis
    optionally: run easy_install hiredis (binary module that accelerates stuff if it exists)

* python-geohash
    http://code.google.com/p/python-geohash/
    can be installed with easy_install python-geohash
