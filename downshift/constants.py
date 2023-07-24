from enum import Enum

# endpoints used to fetch station and transport data
AMTRAK_STATIONS_URL: str = "https://maps.amtrak.com/services/MapDataService/stations/allStations"
AMTRAK_ROUTES_URL: str = "https://maps.amtrak.com/services/MapDataService/stations/nationalRoute"

# POST to this url with something like: `{ "RouteOptions": [{"Name": "Crescent","Origin": "BHM","Destination": "ATL" }]}`
AMTRAK_ROUTE_FIND_URL: str = "https://maps.amtrak.com/services/MapDataService/RoutePointSearch/getRoutePointListCollections"

# GET  to this url with the following headers set:
#   origin
#       BHM
#   destination
#       ATL
#   startDate
#       2023-07-23T01:01:00
AMTRAK_SCHEDULES_FIND_URL: str = "https://www.amtrak.com/v3/travel-service/schedules"


# dictionary paths used to parse fetched data
AMTRAK_ID_PATH: str = "properties/gx_id"
AMTRAK_SEGID_PATH: str = "properties/segmentid"
AMTRAK_CODE_PATH: str = "properties/Code"
AMTRAK_NAME_PATH: str = "properties/Name"

AMTRAK_ADDR1_PATH: str = "properties/Address1"
AMTRAK_ADDR2_PATH: str = "properties/Address2"
AMTRAK_CITY_PATH: str = "properties/City"
AMTRAK_STATE_PATH: str = "properties/State"
AMTRAK_ZIP_PATH: str = "properties/ZipCode"

AMTRAK_COORD_PATH: str = "geometry/coordinates"
AMTRAK_LAT_PATH: str = "geometry/coordinates/1"
AMTRAK_LON_PATH: str = "geometry/coordinates/0"
AMTRAK_GEO_PATH: str = "geometry/type"

AMTRAK_STATIONS_PATH: str = "StationsDataResponse/features"
AMTRAK_ROUTES_PATH: str = "features"
AMTRAK_TYPE_PATH: str = "properties/StnType"

def extract(data: dict, path: str):
    while data and path:
        step, _, path = path.partition('/')
        try:
            data = data[step]
        except KeyError:
            data = data[step.lower()]
        except TypeError:
            data = data[int(step)]
    return data

class StationType(Enum):
    Bus   = 0b0000
    Train = 0b0001

class Amtrak:

    @staticmethod
    def code(data: dict):
        return extract(data,AMTRAK_CODE_PATH)
    
    @staticmethod
    def id(data: dict):
        return extract(data,AMTRAK_ID_PATH)
    
    @staticmethod
    def segid(data: dict):
        return extract(data,AMTRAK_SEGID_PATH)
    
    @staticmethod
    def name(data: dict):
        return extract(data,AMTRAK_NAME_PATH)
    
    @staticmethod
    def addr1(data: dict):
        return extract(data,AMTRAK_ADDR1_PATH)
    
    @staticmethod
    def addr2(data: dict):
        return extract(data,AMTRAK_ADDR2_PATH)
    
    @staticmethod
    def city(data: dict):
        return extract(data,AMTRAK_CITY_PATH)
    
    @staticmethod
    def state(data: dict):
        return extract(data,AMTRAK_STATE_PATH)

    @staticmethod
    def zip(data: dict):
        return extract(data,AMTRAK_ZIP_PATH)

    @staticmethod
    def coord(data: dict):
        return extract(data,AMTRAK_COORD_PATH)

    @staticmethod
    def lat(data: dict):
        return extract(data,AMTRAK_LAT_PATH)
    
    @staticmethod
    def lon(data: dict):
        return extract(data,AMTRAK_LON_PATH)
    
    @staticmethod
    def geo(data: dict):
        return extract(data,AMTRAK_GEO_PATH)
    
    @staticmethod
    def stations(data: dict):
        return extract(data,AMTRAK_STATIONS_PATH)
    
    @staticmethod
    def routes(data: dict):
        return extract(data,AMTRAK_ROUTES_PATH)

    @staticmethod
    def type(data: dict):
        return extract(data,AMTRAK_TYPE_PATH)
