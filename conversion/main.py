import os
from shutil import rmtree
from module import unzip, parse_items, parse_regions, parse_locations, generate_item_lua, generate_location_lua, convert_items, convert_locations


def main():
    # unzip_folder = "./unzipped/"
    output_folder = "./out/"
    
    # if os.path.exists(unzip_folder):
    #     rmtree(unzip_folder)
    
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)
    
    # unzip("Manual_SuperPaperMario_Redriel.apworld", unzip_folder)
    # data_folder = unzip_folder + "manual_superpapermario_redriel/data/"
    
    data_folder = "../../apworld/manual_superpapermario_redriel/data/"
    items = parse_items(data_folder)
    regions = parse_regions(data_folder)
    locations = parse_locations(data_folder, regions)
    
    generate_item_lua(items)
    generate_location_lua(locations)
    
    convert_items(items)
    convert_locations(locations)
    

if __name__ == "__main__":
    main()
