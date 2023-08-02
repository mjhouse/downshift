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
from downshift.greyhound.crawler import Crawler
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
        self.__crawler = Crawler()
        self.__flixbus_key = self.__crawler.version()

    @sleep_and_retry
    @limits(calls=1, period=1)
    def __fetch_cities(self, url: str) -> dict:
        page = requests.get(url)
        result = {}

        if page.status_code != 200:
            return result

        return json.loads(page.text)

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

    def fetch(self):
        if not self.__flixbus_key:
            print("no flixbus key")
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
            data = self.__crawler.stations(item['slug'])

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
