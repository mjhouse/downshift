from downshift import amtrak

def run():
    source = amtrak.Amtrak("cache/")
    for route in source.routes():
        print(route)