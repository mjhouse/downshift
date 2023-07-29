import json
import os
from bs4 import BeautifulSoup
from ratelimit import sleep_and_retry, limits
import requests
from jsonschema import validate

from pathlib import Path
from downshift.common.source import Source
from downshift.constants import GREYHOUND_CITY_SEARCH

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


    def data(self) -> list[dict]:
        # get all of the cities serviced by greyhound
        cities = self.__fetch_cities(GREYHOUND_CITY_SEARCH)
        result = []

        # check that nothing went horribly wrong
        if not cities or not 'result' in cities.keys():
            return result
        
        # for each city, get all of the stations
        for city in cities['result']:
            stations = self.__fetch_stations(city['slug'])

            # check that stations where found
            if not stations:
                continue

            # add the station data to the city data
            result.append({
                **city,
                'stations': stations,
            })

            break

        # return each city with all stations
        return result