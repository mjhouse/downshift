
ADDRESSES_SCHEMA = {
    "type": "array",
    "properties": {
        "country": {"type": "string"},
        "id": {"type": "number"},
        "language": {"type": "string"},
        "location": {"type": "object"},
        "name": {"type": "string"},
        "search_volume": {"type": "number"},
        "slug": {"type": "string"},
        "stations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "@context": {"type": "string"},
                    "@type": {"type": "string"},
                    "address": {"type": "object"},
                    "latitude": {"type": "number"},
                    "longitude": {"type": "number"},
                    "name": {"type": "string"},
                    "openingHours": {"type": "string"},
                },
                "required": ["@type","address"],
            },
        },
        "transportation_category": {"type": "array"},
        "uuid": {"type": "string"},
    },
    "required": ["slug","uuid"], 
}