# from typing import Self
from peewee import *
from jsonschema import validate

db = SqliteDatabase('data.db')

GREYHOUND_ADDRESS_SCHEMA = {
    "type": "object",
    "properties": {
        "@type": {"type": "string"},
        "addressCountry": {"type": "string"},
        "addressLocality": {"type": "string"},
        "postalCode": {"type": "string"},
        "streetAddress": {"type": "string"},
    },
    "required": [
        "@type",
        "addressCountry",
        "addressLocality",
        "postalCode",
        "streetAddress",
    ], 
}

class Address(Model):
    street = CharField(unique=True)
    city = CharField()
    state = CharField()
    country = CharField()
    postal = CharField()

    class Meta:
        database = db

    def build(data: dict):
        validate(data,GREYHOUND_ADDRESS_SCHEMA)

        street = data['streetAddress']
        city = data['addressLocality'].split(',')[0].strip()
        state = data['addressLocality'].split(',')[1].strip()
        country = data['addressCountry']
        postal = data['postalCode']

        return Address(
            street=street,
            city=city,
            state=state,
            country=country,
            postal=postal,
        )