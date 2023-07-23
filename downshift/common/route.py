from downshift.common.address import Address
from downshift.common.geometry import Geometry, Line, Point
from downshift import constants

parser = constants.Amtrak

class Route:
    
    def __init__(self, id: str, name: str, line: Line):
        self.id = id
        self.name = name
        self.line = line

    def parse(data: dict):
        return Route(
            parser.segid(data),
            parser.name(data),
            Line.parse(data))

    def __desc__(self):
        return self.__str__()

    def __str__(self):
        return f'<Route {self.name} ({self.id})>'