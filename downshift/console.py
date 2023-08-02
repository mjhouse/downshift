from urllib.request import urlretrieve
from os.path import isfile
import os

from peewee import *
from downshift.greyhound.crawler import Crawler
from downshift.greyhound.source import Greyhound
from downshift.models.city import City
from downshift.models.address import Address
from downshift.models.config import Config, ConfigKey
from downshift.models.route import Route
from downshift.models.station import Station

db = SqliteDatabase('data.db')

def fetch():
    # create the database if it 
    # doesn't exist
    db.create_tables([
        Config,
        Route,
        City,
        Address,
        Station
    ])

    # print(Config.read(ConfigKey.FLIXBUS))

    crawler = Crawler()
    print(crawler.version())

    # source = Greyhound()
    # source.fetch()