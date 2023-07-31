import json
from bs4 import BeautifulSoup
from ratelimit import sleep_and_retry, limits
import requests
from jsonschema import validate

from pathlib import Path
from downshift.common.source import Source

from selenium.webdriver.common.by import By
# from selenium.webdriver import Chrome
from seleniumwire.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from downshift.constants import GREYHOUND_CITY_SEARCH
from downshift.models.address import Address
from downshift.models.route import Route
from downshift.models.station import Station
from downshift.models.city import City
from peewee import *
from selenium.webdriver.firefox.service import Service

db = SqliteDatabase('data.db')

REQUEST_DATA = {
    "from": 0,
    "size": 100,
    "_source": [
        "name",
        "id",
        "location"
    ],
    "sort": [
        {
            "search_volume": {
                "order": "desc"
            }
        }
    ],
    "query": {
        "bool": {
            "must": [
                {
                    "term": {
                        "field_site.keyword": {
                            "value": "flixbus"
                        }
                    }
                },
                {
                    "term": {
                        "_language.keyword": {
                            "value": "en-us"
                        }
                    }
                }
            ],
            "filter": [
                {
                    "geo_bounding_box": {
                        "location": {
                            "top_left": {
                                "lat": 64.595919,
                                "lon": -179.770047
                            },
                            "bottom_right": {
                                "lat": 16.440924,
                                "lon": -67.938804
                            }
                        }
                    }
                },
                {
                    "term": {
                        "reachable.id": 0
                    }
                },
                {
                    "terms": {
                        "transportation_category": [
                            "bus",
                            "flixtrain",
                            "train"
                        ]
                    }
                }
            ]
        }
    }
}

ADDRESSES_SCHEMA = {
    "type": "array",
    "properties": {
        "country": {"type": "string"},
        "id": {"type": "number"},
        "language": {"type": "string"},
        "location": {"type": "object"},
        "name": {"type": "string"},
        "search_volume": {"type": "number"},
        "slug": {"type": "string"},
        "stations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "@context": {"type": "string"},
                    "@type": {"type": "string"},
                    "address": {"type": "object"},
                    "latitude": {"type": "number"},
                    "longitude": {"type": "number"},
                    "name": {"type": "string"},
                    "openingHours": {"type": "string"},
                },
                "required": ["@type","address"],
            },
        },
        "transportation_category": {"type": "array"},
        "uuid": {"type": "string"},
    },
    "required": ["slug","uuid"], 
}

class Greyhound(Source):

    def __init__(self):
        super(Source).__init__()
        self.__flixbus_key = None

    @sleep_and_retry
    @limits(calls=1, period=1)
    def __fetch_cities(self, url: str) -> dict:
        page = requests.get(url)
        result = {}

        if page.status_code != 200:
            return result

        return json.loads(page.text)

    @sleep_and_retry
    @limits(calls=1, period=1)
    def __fetch_stations(self, slug: str) -> list[dict]:
        # fetch the city page of the given slug from flixbus
        page = requests.get(f"https://www.flixbus.com/bus/{slug}")

        # check that the page was found
        if page.status_code != 200:
            return []

        # parse the html and find a section with the 'stops-location' id
        soup = BeautifulSoup(page.text, features="html.parser")
        block = soup.find(id="stops-location")

        # check that the section was found
        if not block:
            return []
        
        # get the first script block from the section
        script = block.script

        # check that the script block was found
        if not script:
            return []

        # try to parse the script contents as json
        data = None
        
        try:
            data = json.loads(script.text)
        except:
            return []

        # verify that the data has the expected shape
        validate(data,ADDRESSES_SCHEMA)

        # return the parsed addresses
        return data

    def __fetch_reachable(self, city: int) -> list[dict]:
        # get list of destinations from flixbux
        REQUEST_DATA['query']['bool']['filter'][1]['term']['reachable.id'] = int(city)
        result = requests.post(
            f"https://{self.__flixbus_key}.cloudfront.net/cities_v2/_search",
            data=json.dumps(REQUEST_DATA),
            headers={
                "Host": f"{self.__flixbus_key}.cloudfront.net",
                "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://www.flixbus.com/",
                "Content-Type": "application/json",
                "Content-Length": "503",
                "Origin": "https://www.flixbus.com",
                "DNT": "1",
                "Connection": "keep-alive",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "cross-site",
                "TE": "trailers"
            })
        return result.json()['hits']['hits']

    def __fetch_version(self) -> bool:
        options = Options()
        options.headless = True

        driver = Chrome(options=options)
        driver.implicitly_wait(30)

        # go to the flixbus route map webapp
        driver.get('https://www.flixbus.com/bus-routes')

        # filter the results so that autocomplete gives us a station
        field = driver.find_element(By.ID,'searchInput-from')
        field.send_keys("New York, NY")

        # this is a path from the search input to the first 
        # autocomplete result
        xpath = '../../following-sibling::div/ul/li[2]/div'

        # click the first auto complete result
        container = field.find_element(By.XPATH,xpath)
        container.click()

        # search the network traffic for a route api request
        for request in driver.requests:

            # the request we're looking for has this path
            if request.path != '/cities_v2/_search':
                continue

            # split the host domain
            pieces = request.host.split('.')

            # should be [<KEY>, "cloudfront", "net"]
            if len(pieces) != 3:
                continue

            # check second element is 'cloudfront'
            if pieces[1] != 'cloudfront':
                continue

            # check third element is 'net'
            if pieces[2] != 'net':
                continue

            # host has correct shape, so assume first
            # element is the version key
            self.__flixbus_key = pieces[0]

            # the version key was found
            return True

        return False

    def fetch(self):
        has_key = bool(self.__flixbus_key)

        # check to see if we have a version key for 
        # the flixbus api
        if not has_key:
            has_key = self.__fetch_version()

        if not has_key:
            return

        # get all of the cities serviced by greyhound
        cities = self.__fetch_cities(GREYHOUND_CITY_SEARCH)

        # check that nothing went horribly wrong
        if not cities or not 'result' in cities.keys():
            return
        
        # for each city, get all of the stations
        for item in cities['result']:
            city = City.build(item)

            try:
                city.save()
            except:
                city = City.get(City.identifier == city.identifier)

            print(f"fetching stations for {item['name']}:")
            data = self.__fetch_stations(item['slug'])

            # check that stations where found
            if not data:
                print(f"    stations NOT found")
                continue

            print(f"    stations found")
            for record in data:
                address = Address.build(record['address'])

                if not address:
                    continue

                try:
                    address.save()
                except:
                    address = Address.get(Address.street == address.street)

                station = Station.build(record,city,address)

                try:
                    station.save()
                except:
                    station = Station.get(Station.address == address)

        routes = []

        print("fetching routes for each city:")
        for city in City.select():
            result = self.__fetch_reachable(city.identifier)
            ids = [ h['_source']['id'] for h in result ]
            
            print(f"  fetching reachable cities:")
            cities = list(City.select().where(City.identifier.in_(ids)))

            print(f"  found {len(cities)} hits:")
            routes.extend(Route.build(city,other) for other in cities)

        print(f"  creating {len(routes)} routes")
        Route.bulk_create(routes)
