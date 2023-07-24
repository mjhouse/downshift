

GREYHOUND_CITY_DETAIL_SEARCH: str = "https://global.api.flixbus.com/search/service/cities/details?locale=en_US&from_city_id=37261"

# lon/lat returned are for city centers, not for bus stop locations
GREYHOUND_CITY_SEARCH: str = "https://global.api.flixbus.com/cms/cities?language=en-gl&country=US&limit=9999"

# scheme
# 	https
# host
# 	global.api.flixbus.com
# filename
# 	/search/service/v4/search
# from_city_id
# 	2ff0f50f-381d-4b87-b2c9-9b8fa7795f1c
# to_city_id
# 	12de2012-89ac-40a3-a908-2308ecf3a4ed
# departure_date
# 	23.07.2023
# products
# 	{"adult":1}
# currency
# 	USD
# locale
# 	en_US
# search_by
# 	cities
# include_after_midnight_rides
# 	1
GREYHOUND_PRICE_SEARCH: str = "https://global.api.flixbus.com/search/service/v4/search?from_city_id=2ff0f50f-381d-4b87-b2c9-9b8fa7795f1c&to_city_id=12de2012-89ac-40a3-a908-2308ecf3a4ed&departure_date=23.07.2023&products=%7B%22adult%22%3A1%7D&currency=USD&locale=en_US&search_by=cities&include_after_midnight_rides=1"