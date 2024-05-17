from collections import defaultdict
import re
from sympy import Symbol, symbols, to_dnf
from sympy.logic.boolalg import And, Or

from .constants import MAP_X_COORDS
from .files import export_json
from .utils import snake_case


def parse_logic_expression(expression: str) -> tuple[str, dict[str, Symbol]]:
    clauses = set(re.findall(r"\|([^|]+)\|", expression))

    clause_map = {}
    for clause in clauses:
        clause_parts = clause.split(":")
        if len(clause_parts) == 2:
            clause_name, count = clause_parts
            clause_name = snake_case(clause_name) + "|" + count
        else:
            clause_name = snake_case(clause_parts[0])
        
        clause_name = re.sub(r'[()#-]', '', clause_name)

        base_name = clause_name.split("|")[0]
        clause_map[clause] = symbols(base_name)

    expression = expression.replace("AND", "&").replace("OR", "|")
    
    if expression == "() & ()":
        return None, None
    elif '() & ' in expression:
        expression = expression[len("() & "):]
    elif ' & ()' in expression:
        expression = expression[:-len(" & ()")]
    
    for original, symbol in clause_map.items():
        expression = expression.replace(f"|{original}|", str(symbol))

    return expression, clause_map


def expression_to_dnf(input_string: str) -> list[str]:
    expression, clause_map = parse_logic_expression(input_string)
    if expression == None:
        return ""

    dnf_expression = to_dnf(expression, simplify=True, force=True)

    formatted_output = []
    for disjunct in Or.make_args(dnf_expression):
        clause_strings = []
        for conjunct in And.make_args(disjunct):
            clause_string = str(conjunct)

            for original, symbol in clause_map.items():
                if symbol.name != clause_string:
                    continue
                formatted_original = snake_case(original)
                if ":" in original:
                    formatted_original = "$has|" + formatted_original.replace(":", "|")

                clause_strings.append(formatted_original)
                break
            else:
                clause_strings.append(clause_string)
        formatted_output.append(", ".join(clause_strings))

    return formatted_output


def parse_area_name(name):
    name = name.split(" - ")[0]
    if any(name.startswith(v) for v in ["Flipside", "Flopside"] and not "Pit" in name):
        return name.split(" ")[0]
    return name


def get_coordinates_chapter(area: str, as_dict: bool = False) -> tuple[int, int]:
    X = [150 + i*300 for i in range(8)]
    Y = [340 + i*500 for i in range(4)]
    x, y = 0, 0
    
    if area == "Flipside Pit":
        x, y = (1108, 1054)
        
    elif area == "Flopside Pit":
        x, y = (1292, 1054)
        
    elif area.startswith("Flipside"):
        x, y = (1155, 1000)
    
    elif area.startswith("Flopside"):
        x, y = (1245, 1000)
    
    elif area.startswith("Mirror"):
        x, y = (1200, 1054)

    else:
        a, b = map(lambda x: int(x) - 1, area.split(" - ")[0].split("-"))
        
        x, y = (X[b + (a // 4) * 4], Y[a % 4])
    
    if as_dict:
        return { "x": x, "y": y }
    
    return ( x, y )


def get_coordinates_maps(n: int) -> tuple[int, int]:
    return MAP_X_COORDS[n - 1]
    

def convert_locations(locations):
    chapters = defaultdict(list)
    chapters_no_mapsanity = defaultdict(list)
    maps = [None]*48
    
    def convert_entry(entry):
        name: str = entry["name"]
        area = ""

        if name.startswith("Completed"):
            area = name.split(" ")[-1]
            name = "Chapter Completed"
        else:
            area = name.split(" - ")[0]
            if area.startswith("Flipside") and "Pit" not in name:
                name = name[len("flipside "):]
                area = "Flipside"
            elif area.startswith("Flopside") and "Pit" not in name:
                name = name[len("flopside "):]
                area = "Flopside"
            elif " - " not in name:
                return None
            else:
                name = name.split(" - ")[1]

        logic = expression_to_dnf(entry["req"])

        d = {
            "name": name,
            "access_rules": logic
        }
            
        if "Completed" in name:
            d |= {
                "hosted_item": f"completed_chapter_{area}",
                "item_count": 0
            }
        else:
            d |= {
                "item_count": 1
            }
        
        if "Map #" in name:
            d |= {
                "chest_unopened_img": "images/checks/map.png",
                "chest_opened_img": "images/checks/map_checked.png"
            }
            
            map_id = int(name.split("#")[1])
            tab = ((map_id - 1) // 16) + 1
            
            x, y = get_coordinates_maps(map_id)
            
            maps[map_id - 1] = {
                "name": f"Map #{map_id:02}",
                "visibility_rules": [],
                "sections": [
                    {
                        "name": "Found the map",
                        "chest_unopened_img": "images/checks/map_404.png",
                        "chest_opened_img": "images/checks/map.png",
                        "hosted_item": f"map_#{map_id:02}",
                        "access_rules": [f"map_#{map_id:02}"],
                        "item_count": 0
                    },
                    {
                        "name": "Fleep here!",
                        "item_count": 1,
                        "ref": f"Chapters/{area}/{name}"
                    }
                ],
                "map_locations": [
                    {
                        "map": f"maps{tab}",
                        "x": x,
                        "y": y
                    }
                ]
            }

        else:
            d |= {
                "chest_unopened_img": "images/checks/chest.png",
                "chest_opened_img": "images/checks/chest_opened.png"
            }
            chapters_no_mapsanity[area].append(d)

        chapters[area].append(d)
    
    
    for data in locations.values():
        convert_entry(data)
    
    other = ["Flipside", "Mirror Hall", "Flopside", "Flipside Pit", "Flopside Pit"]
    chapters_data = [
        {
            "name": n,
            "sections": chapters[n],
            "size": 28,
            "border_thickness": 2,
            "map_locations": [{
                "map": "chapters",
                **get_coordinates_chapter(n, True)
            }]
        }
        for n in other
    ]
    
    for c in range(1, 9):
        for s in range(1, 5):
            ch = f"{c}-{s}"
            chapters_data.append({
                "name": ch,
                "sections": chapters[ch],
                "map_locations": [{
                    "map": "chapters",
                    **get_coordinates_chapter(ch, True)
                }]
            })
            
    
    maps1_data = maps[:16]
    maps2_data = maps[16:32]
    maps3_data = maps[32:]
        
    final_json = [
        {
            "name": "Chapters",
            "chest_unopened_img": "images/checks/chest.png",
            "chest_opened_img": "images/checks/chest_open.png",
            "children": chapters_data
        },
        {
            "name": "Maps 1",
            "chest_unopened_img": "images/checks/map.png",
            "chest_opened_img": "images/checks/checked_map.png",
            "children": maps1_data
        },
        {
            "name": "Maps 2",
            "chest_unopened_img": "images/checks/map.png",
            "chest_opened_img": "images/checks/checked_map.png",
            "children": maps2_data
        },
        {
            "name": "Maps 3",
            "chest_unopened_img": "images/checks/map.png",
            "chest_opened_img": "images/checks/checked_map.png",
            "children": maps3_data
        }
    ]
    export_json("./out/locations.json", final_json)
    
    other = ["Flipside", "Flopside"]
    chapters_data_no_mapsanity = [
        {
            "name": n,
            "sections": chapters_no_mapsanity[n],
            "size": 28,
            "border_thickness": 2,
            "map_locations": [{
                "map": "chapters",
                **get_coordinates_chapter(n, True)
            }]
        }
        for n in other
    ]
    
    for c in range(1, 9):
        for s in range(1, 5):
            ch = f"{c}-{s}"
            chapters_data_no_mapsanity.append({
                "name": ch,
                "sections": chapters_no_mapsanity[ch],
                "map_locations": [{
                    "map": "chapters",
                    **get_coordinates_chapter(ch, True)
                }]
            })

    final_json_no_mapsanity = [
        {
            "name": "Chapters",
            "chest_unopened_img": "images/checks/chest.png",
            "chest_opened_img": "images/checks/chest_open.png",
            "children": chapters_data_no_mapsanity
        }
    ]
    export_json("./out/locations_no_mapsanity.json", final_json_no_mapsanity)
