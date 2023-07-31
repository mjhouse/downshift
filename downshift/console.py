from urllib.request import urlretrieve
from os.path import isfile
import os

from peewee import *
from downshift.greyhound.source import Greyhound
from downshift.models.city import City
from downshift.models.address import Address
from downshift.models.route import Route
from downshift.models.station import Station

db = SqliteDatabase('data.db')

def fetch():
    # create the database if it 
    # doesn't exist
    db.create_tables([
        Route,
        City,
        Address,
        Station
    ])

    source = Greyhound()
    source.fetch()