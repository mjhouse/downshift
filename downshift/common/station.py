from downshift.common.address import Address
from downshift.common.geometry import Geometry, Point
from downshift import constants

parser = constants.Amtrak

class Station:
    
    def __init__(self, id: str, code: str, name: str, type: str, location: Point, address: Address):
        self.id = id
        self.code = code
        self.name = name
        self.type = type
        self.location = location
        self.address = address

    def parse(data: dict):
        return Station(
            parser.id(data).strip(),
            parser.code(data).strip(),
            parser.name(data).strip(),
            parser.geo(data).strip(),
            Point.parse(data),
            Address.parse(data))

    def description(self):
        return self.name or self.address.string()

    def __desc__(self):
        return self.__str__()

    def __str__(self):
        return f'<Station {self.description()}>'