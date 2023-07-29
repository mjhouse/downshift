import pprint
from downshift import sources
from downshift.greyhound.source import Greyhound

def fetch():
    source = Greyhound()
    pp = pprint.PrettyPrinter(indent=4)
    for station in source.data():
        pp.pprint(station)
    # print(sources.ALL)