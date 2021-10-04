#US State codes taken from http://www.cmmichael.com/blog/2006/12/29/state-code-mappings-for-python

from .location import Location

import math

state_to_code = {'VERMONT': 'VT', 'GEORGIA': 'GA', 'IOWA': 'IA', 'Armed Forces Pacific': 'AP', 'GUAM': 'GU', 'KANSAS': 'KS', 'FLORIDA': 'FL', 'AMERICAN SAMOA': 'AS', 'NORTH CAROLINA': 'NC', 'HAWAII': 'HI', 'NEW YORK': 'NY', 'CALIFORNIA': 'CA', 'ALABAMA': 'AL', 'IDAHO': 'ID', 'FEDERATED STATES OF MICRONESIA': 'FM', 'Armed Forces Americas': 'AA', 'DELAWARE': 'DE', 'ALASKA': 'AK', 'ILLINOIS': 'IL', 'Armed Forces Africa': 'AE', 'SOUTH DAKOTA': 'SD', 'CONNECTICUT': 'CT', 'MONTANA': 'MT', 'MASSACHUSETTS': 'MA', 'PUERTO RICO': 'PR', 'Armed Forces Canada': 'AE', 'NEW HAMPSHIRE': 'NH', 'MARYLAND': 'MD', 'NEW MEXICO': 'NM', 'MISSISSIPPI': 'MS', 'TENNESSEE': 'TN', 'PALAU': 'PW', 'COLORADO': 'CO', 'Armed Forces Middle East': 'AE', 'NEW JERSEY': 'NJ', 'UTAH': 'UT', 'MICHIGAN': 'MI', 'WEST VIRGINIA': 'WV', 'WASHINGTON': 'WA', 'MINNESOTA': 'MN', 'OREGON': 'OR', 'VIRGINIA': 'VA', 'VIRGIN ISLANDS': 'VI', 'MARSHALL ISLANDS': 'MH', 'WYOMING': 'WY', 'OHIO': 'OH', 'SOUTH CAROLINA': 'SC', 'INDIANA': 'IN', 'NEVADA': 'NV', 'LOUISIANA': 'LA', 'NORTHERN MARIANA ISLANDS': 'MP', 'NEBRASKA': 'NE', 'ARIZONA': 'AZ', 'WISCONSIN': 'WI', 'NORTH DAKOTA': 'ND', 'Armed Forces Europe': 'AE', 'PENNSYLVANIA': 'PA', 'OKLAHOMA': 'OK', 'KENTUCKY': 'KY', 'RHODE ISLAND': 'RI', 'WASHINGTON, DC': 'DC', 'ARKANSAS': 'AR', 'MISSOURI': 'MO', 'TEXAS': 'TX', 'MAINE': 'ME'}

code_to_state = {'WA': 'WASHINGTON', 'VA': 'VIRGINIA', 'DE': 'DELAWARE', 'DC': 'WASHINGTON, D.C.', 'WI': 'WISCONSIN', 'WV': 'WEST VIRGINIA', 'HI': 'HAWAII', 'AE': 'Armed Forces Middle East', 'FL': 'FLORIDA', 'FM': 'FEDERATED STATES OF MICRONESIA', 'WY': 'WYOMING', 'NH': 'NEW HAMPSHIRE', 'NJ': 'NEW JERSEY', 'NM': 'NEW MEXICO', 'TX': 'TEXAS', 'LA': 'LOUISIANA', 'NC': 'NORTH CAROLINA', 'ND': 'NORTH DAKOTA', 'NE': 'NEBRASKA', 'TN': 'TENNESSEE', 'NY': 'NEW YORK', 'PA': 'PENNSYLVANIA', 'CA': 'CALIFORNIA', 'NV': 'NEVADA', 'AA': 'Armed Forces Americas', 'PW': 'PALAU', 'GU': 'GUAM', 'CO': 'COLORADO', 'VI': 'VIRGIN ISLANDS', 'AK': 'ALASKA', 'AL': 'ALABAMA', 'AP': 'Armed Forces Pacific', 'AS': 'AMERICAN SAMOA', 'AR': 'ARKANSAS', 'VT': 'VERMONT', 'IL': 'ILLINOIS', 'GA': 'GEORGIA', 'IN': 'INDIANA', 'IA': 'IOWA', 'OK': 'OKLAHOMA', 'AZ': 'ARIZONA', 'ID': 'IDAHO', 'CT': 'CONNECTICUT', 'ME': 'MAINE', 'MD': 'MARYLAND', 'MA': 'MASSACHUSETTS', 'OH': 'OHIO', 'UT': 'UTAH', 'MO': 'MISSOURI', 'MN': 'MINNESOTA', 'MI': 'MICHIGAN', 'MH': 'MARSHALL ISLANDS', 'RI': 'RHODE ISLAND', 'KS': 'KANSAS', 'MT': 'MONTANA', 'MP': 'NORTHERN MARIANA ISLANDS', 'MS': 'MISSISSIPPI', 'PR': 'PUERTO RICO', 'SC': 'SOUTH CAROLINA', 'KY': 'KENTUCKY', 'OR': 'OREGON', 'SD': 'SOUTH DAKOTA'}

state_geocodes = { 'AK': (61.3850,-152.2683),
        'AL': (32.7990,-86.8073),
        'AR': (34.9513,-92.3809),
        'AS': (14.2417,-170.7197),
        'AZ': (33.7712,-111.3877),
        'CA': (36.1700,-119.7462),
        'CO': (39.0646,-105.3272),
        'CT': (41.5834,-72.7622),
        'DC': (38.8964,-77.0262),
        'DE': (39.3498,-75.5148),
        'FL': (27.8333,-81.7170),
        'GA': (32.9866,-83.6487),
        'HI': (21.1098,-157.5311),
        'IA': (42.0046,-93.2140),
        'ID': (44.2394,-114.5103),
        'IL': (40.3363,-89.0022),
        'IN': (39.8647,-86.2604),
        'KS': (38.5111,-96.8005),
        'KY': (37.6690,-84.6514),
        'LA': (31.1801,-91.8749),
        'MA': (42.2373,-71.5314),
        'MD': (39.0724,-76.7902),
        'ME': (44.6074,-69.3977),
        'MI': (43.3504,-84.5603),
        'MN': (45.7326,-93.9196),
        'MO': (38.4623,-92.3020),
        'MP': (14.8058,145.5505),
        'MS': (32.7673,-89.6812),
        'MT': (46.9048,-110.3261),
        'NC': (35.6411,-79.8431),
        'ND': (47.5362,-99.7930),
        'NE': (41.1289,-98.2883),
        'NH': (43.4108,-71.5653),
        'NJ': (40.3140,-74.5089),
        'NM': (34.8375,-106.2371),
        'NV': (38.4199,-117.1219),
        'NY': (42.1497,-74.9384),
        'OH': (40.3736,-82.7755),
        'OK': (35.5376,-96.9247),
        'OR': (44.5672,-122.1269),
        'PA': (40.5773,-77.2640),
        'PR': (18.2766,-66.3350),
        'RI': (41.6772,-71.5101),
        'SC': (33.8191,-80.9066),
        'SD': (44.2853,-99.4632),
        'TN': (35.7449,-86.7489),
        'TX': (31.1060,-97.6475),
        'UT': (40.1135,-111.8535),
        'VA': (37.7680,-78.2057),
        'VI': (18.0001,-64.8199),
        'VT': (44.0407,-72.7093),
        'WA': (47.3917,-121.5708),
        'WI': (44.2563,-89.6385),
        'WV': (38.4680,-80.9696),
        'WY': (42.7475,-107.2085)
    }




class State(object):
    
    
    _index_ = {}
    def __init__(self, name, code, lat = None, lon = None):
        self.name = name
        self.code = code
        self.lat = lat
        self.lon = lon
        
        
    def __repr__(self):
        
        return "%s" % self.__dict__
        
        
    @staticmethod
    def buildIndex():
        """
        Init the state index
        we index both by name and by code.
        This gets called automatically when this module is imprted for the first time
        """
        
        if not State._index_:
            for code, geocode in state_geocodes.iteritems():
                name = code_to_state.get(code, '').capitalize()
                State._index_[code] = State(name, code, geocode[0], geocode[1])
                State._index_[name.upper()] = State._index_[code]
    
    @staticmethod    
    def get(stateOrCode):
        
        """
        Get state object by code or name, case insensitive
        @return the state if found, or None otherwise
        """
        
        s = stateOrCode.upper().strip()
        
        return State._index_.get(s)

    def score(self, refLat, refLon):

        if refLat is None or refLon is None:
            return 0.2
        d = Location.getLatLonDistance((self.lat, self.lon), (refLat, refLon))
        dScore =  max(0.2, 1 - 1/(1+math.exp(-0.012*d+2*math.e) ))


        return dScore

State.buildIndex()


if __name__ == '__main__':
    print(State.get('CA'))
    
    
