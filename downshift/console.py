from downshift.amtrak.source import Amtrak

def run():
    source = Amtrak("cache/")
    for route in source.routes():
        print(route)