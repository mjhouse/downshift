from peewee import *
from jsonschema import validate
from downshift.constants import StationType

from downshift.models.address import Address
from downshift.models.city import City

db = SqliteDatabase('data.db')

GREYHOUND_STATION_SCHEMA = {
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
    "required": [
        "@context",
        "@type",
        "address",
        "latitude",
        "longitude",
        "name",
        "openingHours",
    ],
}

class Station(Model):
    name = CharField()
    type = IntegerField()
    city = ForeignKeyField(model=City)
    address = ForeignKeyField(model=Address,unique=True)
    latitude = FloatField()
    longitude = FloatField()

    class Meta:
        database = db

    def build(data: dict, city: City, address: Address):
        validate(data,GREYHOUND_STATION_SCHEMA)

        name = data['name']
        type = StationType.Bus.value
        latitude = data['latitude']
        longitude = data['longitude']

        return Station(
            city=city,
            name=name,
            type=type,
            address=address,
            latitude=latitude,
            longitude=longitude,
        )