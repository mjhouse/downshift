from enum import Enum
from peewee import *

db = SqliteDatabase('data.db')

class ConfigKey(Enum):
    FLIXBUS = 0b0000

class Config(Model):
    key = IntegerField(unique=True)
    value = CharField()

    class Meta:
        database = db

    def read(key: ConfigKey)-> str:
        config = Config.get_or_none(Config.key == key.value)
        if config:
            return config.value
        else:
            return ""
    
    def write(key: ConfigKey, value: str) -> None:
        Config.replace(key=key.value,value=value).execute()

    def __str__(self):
        return f'<{ConfigKey(self.key)}=\"{self.value}\">'