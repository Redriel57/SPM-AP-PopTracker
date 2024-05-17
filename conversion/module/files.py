from json import load, dump
import zipfile

from .utils import snake_case


def unzip(file: str, to: str):
    with zipfile.ZipFile(file, 'r') as zip_ref:
        zip_ref.extractall(to)


def import_json(file: str):
    with open(file, 'r') as infile:
        json_data = load(infile)

    return json_data


def export_json(file: str, data) -> None:
    with open(file, 'w') as outfile:
        dump(data, outfile, indent=4)


def generate_item_lua(items):
    pref = "ITEM_MAPPING = {\n"
    suff = "}"
    
    middle = ""
    for name, item in items.items():
        middle += f"\t[{item["ap_id"]}] = {{\"{snake_case(name)}\", \"{'toggle' if item["count"] == 1 else 'consumable'}\"}},\n"
        
    file = "./out/item_mapping.lua"
    
    full = pref + middle + suff
    
    with open(file, 'w') as f:
        f.write(full)


def generate_location_lua(locations):
    pref = "LOCATION_MAPPING = {\n"
    suff = "}"
    
    middle = ""
    for name, loc in locations.items():
        if name.startswith("Completed"):
            middle += f"\t[{loc["ap_id"]}] = {{\"@Chapters/{loc["region"]}/Chapter Completed\"}},\n"
            continue
        
        if "Pit" not in name and (name.startswith("Flipside") or name.startswith("Flopside")):
            area = name.split(" ")[0]
            rest = name[len("fl_pside "):]
            middle += f"\t[{loc["ap_id"]}] = {{\"@Chapters/{area}/{rest}\"}},\n"
            continue
        
        if name.startswith("Mirror Hall"):
            middle += f"\t[{loc["ap_id"]}] = {{\"@Chapters/Mirror Hall/{name.split(" - ")[1]}\"}},\n"
            continue

        middle += f"\t[{loc["ap_id"]}] = {{\"@Chapters/{loc["region"]}/{name.split(" - ")[1]}\"}},\n"
        
    file = "./out/location_mapping.lua"
    
    full = pref + middle + suff
    
    with open(file, 'w') as f:
        f.write(full)
