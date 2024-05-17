from .files import export_json
from .utils import snake_case


def convert_entry(entry):
    count = int(entry['count'])
    name = entry['name']
    formatted_name = snake_case(name)
    new_entry = dict()

    if "Map" in name:
        new_entry = {
            "name": name,
            "type": "toggle",
            "img": f"images/items/map.png",
            "loop": True,
            "codes": formatted_name
        }
    elif "Completed" in name:
        new_entry = {
            "name": name,
            "type": "toggle",
            "img": f"images/checks/star_block.png",
            "loop": True,
            "codes": formatted_name
        }
    elif count == 1:
        new_entry = {
            "name": name,
            "type": "toggle",
            "img": f"images/items/{formatted_name}.png",
            "loop": True,
            "codes": formatted_name
        }
    else:
        new_entry = {
            "name": name,
            "type": "consumable",
            "img": f"images/items/{formatted_name}.png",
            "initial_quantity": 0,
            "max_quantity": count,
            "codes": formatted_name
        }

    return new_entry

def convert_items(items):
    output = [convert_entry(entry) for entry in items.values()]

    export_json("./out/items.json", output)
