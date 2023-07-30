# from typing import Self
from peewee import *
from jsonschema import validate

db = SqliteDatabase('data.db')

GREYHOUND_CITY_SCHEMA = {
    "type": "object",
    "properties": {
        "country":{"type": "string"},
        "id": {"type": "number"},
        "language": {"type": "string"},
        "location": {"type": "object"},
        "name": {"type": "string"},
        "search_volume": {"type": "number"},
        "slug": {"type": "string"},
        "transportation_category": {"type": "array"},
        "uuid": {"type": "string"}
    },
    "required": [
        "country",
        "id",
        "language",
        "location",
        "name",
        "search_volume",
        "slug",
        "transportation_category",
        "uuid"
    ], 
}

class City(Model):
    country = CharField()
    identifier = IntegerField()
    language = CharField()
    name = CharField()
    slug = CharField()
    uuid = CharField()

    class Meta:
        database = db

    def build(data: dict):
        validate(data,GREYHOUND_CITY_SCHEMA)

        country = data['country']
        identifier = data['id']
        language = data['language']
        name = data['name']
        slug = data['slug']
        uuid = data['uuid']

        return City(
            country=country,
            identifier=identifier,
            language=language,
            name=name,
            slug=slug,
            uuid=uuid
        )