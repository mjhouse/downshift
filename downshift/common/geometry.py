from downshift import constants

parser = constants.Amtrak

class Geometry:

    @staticmethod
    def parse(data: dict):
        if parser.geo(data) == 'Point':
            return Point.parse(data)
        if parser.geo(data) == 'LineString':
            return Line.parse(data)
        raise RuntimeError("unsupported geometry type")

class Point:

    def __init__(self, lon: float, lat: float):
        self.lon = lon
        self.lat = lat

    def parse(data: dict):
        return Point(
            parser.lon(data),
            parser.lat(data))

    def __str__(self):
        return f'<Point {self.lat},{self.lon}>'

class Line:

    def __init__(self, points: list[Point]):
        self.points = points

    def parse(data: dict):
        points = []
        raw = parser.coord(data)

        if raw:
            for pair in raw:
                points.append(Point(pair[0],pair[1]))

        return Line(points)
    
    def __str__(self):
        return f'<Line {len(self.points)}>'