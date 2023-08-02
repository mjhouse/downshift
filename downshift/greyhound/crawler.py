import json
from bs4 import BeautifulSoup
from ratelimit import sleep_and_retry, limits
import requests
from jsonschema import validate

from selenium.webdriver.common.by import By
from seleniumwire.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

from downshift.greyhound.schema import ADDRESSES_SCHEMA

from peewee import *
from downshift.greyhound.urls import FLIXBUS_CITY, FLIXBUS_ROUTES, FLIXBUS_SEARCH

from downshift.models.config import Config, ConfigKey

class Crawler:

    def __init__(self):
        self.__stations_cache = {}
        self.__version_cache = Config.read(ConfigKey.FLIXBUS)

    @sleep_and_retry
    @limits(calls=1, period=10)
    def stations(self, slug: str) -> list[dict]:
        """Get stations from the flixbus page for a city.

        This function crawls a page for a given city slug
        and extracts the station information embedded in 
        javascript code in the page body.
        """

        # return cached data if we have some
        if slug in self.__stations_cache:
            return self.__stations_cache[slug]

        # fetch the city page of the given slug from flixbus
        page = requests.get(FLIXBUS_CITY(slug))

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

        data = None

        # try to parse the script contents as json        
        try:
            data = json.loads(script.text)
        except:
            return []

        # verify that the data has the expected shape
        validate(data,ADDRESSES_SCHEMA)

        # cache the data for later calls
        self.__stations_cache[slug] = data

        # return the parsed addresses
        return data

    @sleep_and_retry
    @limits(calls=1, period=1)
    def verify(self) -> bool:
        """Verify that the flixbus version hash is still good.

        Calls a flixbus cloudfront endpoint with the version 
        hash. If the url isn't found or returns 404 (bad or 
        out-of-date hash) then this function returns false, 
        otherwise it returns true. 
        """
        try:
            result = requests.get(FLIXBUS_SEARCH(self.__version_cache))
            return result.status_code == 200
        except:
            return False

    @sleep_and_retry
    @limits(calls=1, period=30)
    def version(self) -> str | None:
        """Get the flixbus version hash for their api
        
        This function uses selenium to inspect network
        requests made by the flixbus interactive bus 
        route map to get a version hash to use for later
        requests.
        """

        if self.__version_cache and self.verify():
            return self.__version_cache

        result = None

        # set selenium options to headless (no gui)
        options = Options()
        options.headless = True

        driver = Chrome(options=options)
        driver.implicitly_wait(30)

        # go to the flixbus route map webapp
        driver.get(FLIXBUS_ROUTES)

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
            result = pieces[0]
            break

        # cache the result for later runs
        Config.write(ConfigKey.FLIXBUS,result)

        # cache the result for later calls
        self.__version_cache = result

        return result