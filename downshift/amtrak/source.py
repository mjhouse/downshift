from pathlib import Path
import requests
import json
import os

from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util import Padding

from downshift import constants
from downshift.common import Source, Route, Station
from downshift.common.address import Address
from downshift.common.geometry import Geometry, Line, Point

parser = constants.Amtrak

class Amtrak(Source):

    def __init__(self, cache: str = None):
        super(Source).__init__()

        if cache != None:
            self.__cache = Path(os.getcwd()) / cache

    def __data(self, key: str, url: str):
        if not self.__cache.exists():
            os.mkdir(self.__cache)

        name = key + '.json'
        path = self.__cache / name

        data = None

        if not path.exists():
            page = requests.get(url)

            with open(path,'w') as f:
                f.write(page.text)

            data = json.loads(page.text)
        else:
            with open(path,'r') as f:
                data = json.loads(f.read())

        return data

    def route(self, id: str) -> Route:
        for route in self.routes():
            if route.id == id:
                return route

    def routes(self) -> list[Route]:
        data = self.__data('routes',constants.AMTRAK_ROUTES_URL)
        return [ Route.parse(d) for d in parser.routes(data) ]

    def station(self, id: str) -> Station:
        for station in self.stations():
            if station.id == id:
                return station

    def stations(self) -> list[Station]:
        data = self.__data('stations',constants.AMTRAK_STATIONS_URL)
        return [ Station.parse(d) for d in parser.stations(data) ]
