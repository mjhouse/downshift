# from typing import Self
from peewee import *

from downshift.models.city import City

db = SqliteDatabase('data.db')

class Route(Model):
    start = ForeignKeyField(model=City)
    end = ForeignKeyField(model=City)

    class Meta:
        database = db
        constraints = [SQL('UNIQUE (start_id, end_id)')]

    def build(a: City, b: City):
        return Route(
            start=a,
            end=b
        )