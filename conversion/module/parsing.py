from .files import import_json
from .constants import STARTING_ITEM_ID, STARTING_LOCATION_ID

def parse_items(data_folder: str):
    data = import_json(data_folder + "items.json")
    d = dict()
    for i, item in enumerate(data):
        d[item["name"]] = {"ap_id": STARTING_ITEM_ID + i} | item
    
    return d

def parse_regions(data_folder: str):
    data = import_json(data_folder + "regions.json")
    d = dict()
    for reg, val in data.items():
        d[reg] = val
    
    return d


def parse_locations(data_folder: str, regions):
    data = import_json(data_folder + "locations.json")
    d = dict()
    
    for i, loc in enumerate(data):
        req_region = regions[loc["region"]]["requires"]
        if req_region == []:
            req_region = ""
        
        req_loc = loc["requires"]
        if req_loc == []:
            req_loc = ""
         
        region = loc["region"]
        category = getattr(loc, 'category', [])
        place_item = getattr(loc, 'place_item', [])
        victory = getattr(loc, 'victory', False)

        d[loc["name"]] = {
            "name": loc["name"],
            "region": region, 
            "category": category,
            "place_item": place_item,
            "victory": victory,
            "ap_id": STARTING_LOCATION_ID + i,
            "req": f"({req_region}) AND ({req_loc})"
        }
    
    return d
