import pprint
from peewee import *
from downshift import sources
from downshift.greyhound.source import Greyhound
from downshift.models.address import Address

db = SqliteDatabase('data.db')

def fetch():
    db.create_tables([Address])
    
    source = Greyhound()
    source.fetch()