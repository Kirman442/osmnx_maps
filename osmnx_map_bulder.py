# -*- coding: utf-8 -*-
"""
Created on Tue Apr 23 17:38:30 2024

@author: Kirill
"""

import os
import osmnx as ox
import geopandas as gpd
from geopy.geocoders import Nominatim
from PIL import Image, ImageDraw, ImageFont, ImageColor
from shapely.ops import unary_union
ox.settings.log_console = False
import time


# main settings
place = ['Delhi, India'] 
#'Barselona, España' 'Acapulco de Juárez, Mexico', 'Stockholm, Sweden', 'Tripoly, Libya', 'Prague, Czech Republic', 'Moscow, Russia', 'Ho Chi Minh, Vietnam', 'Tokio, Japan', 'Pekin, China', 'Mumbai, India', 'New Dehli, India' 'Delhi'
city,  country = place[0].split(', ')
geolocator = Nominatim(user_agent="degdms")
location = geolocator.geocode(place, language="en")
img_folder = "images"
extension = "png"
font_folder = "fonts"
font_city = "CaviarDreams.ttf"
font_notes = "BerlinSmallCaps.ttf"
# image res
dpi = 600
# distance in metres from the geopoint of place
dist = 2500
# size of the figure/image, the larger the values, the larger the size
figsize = (8, 8)

# files paths
if not os.path.exists(img_folder):
    os.makedirs(img_folder)
fp_water = os.path.join(img_folder, city + f"_water.{extension}")
fp_roads = os.path.join(img_folder, city + f"_roads.{extension}")
fp_railroads = os.path.join(img_folder, city + f"_railroads.{extension}")
fp_buildings = os.path.join(img_folder, city + f"_buildings.{extension}")
# fp_result = os.path.join(img_folder, city + f"_finalImage_{dist}.{extension}") 

# font paths
fsity = os.path.join(font_folder, font_city)
fnotes = os.path.join(font_folder, font_notes)
crs = ('EPSG:4326')

surface = ox.geocode_to_gdf(place)

# Define bboxes for our maps, i.e. 1 - Boundary, 2 - Distance
bbox_boundary = tuple(surface.total_bounds[[3,1,2,0]])
bbox_distance = ox.utils_geo.bbox_from_point(
    (location.latitude-0.02, location.longitude), dist=dist)

image_paths = [fp_roads]
# Roads Block
# ------------

# dict to make output file final image
responses = {'response': 0, 'add_water': 0, 'add_buildings': 0,
             'add_railways': 0, 'color_palette': 0, 'gradient_position': 0}

print('Which map will be built? 1 - Boundary, 2 - Distance')

# response = None
# while response not in {1, 2}:
#     response = int(input("Please enter 1 or 2: "))

# print('Choose color palette: 1 - Dark, 2 - Light blue, 3 - Navy, 4 - Salmon, 5 - Dark Orange')
# color_palette  = None
# while color_palette not in {1, 2, 3, 4, 5}:
#     color_palette = int(input("Please type the matching number: "))

# print('Add Roads?: 1 - Yes, 0 - No')
# add_roads = None
# while add_roads not in {0, 1}:
#     add_roads = int(input("Please type the matching number: "))

# print('Add Water?: 1 - Yes, 0 - No')
# add_water = None
# while add_water not in {0, 1}:
#     add_water = int(input("Please type the matching number: "))

# print('Add buildings?: 1 - Yes, 0 - No')
# add_buildings = None
# while add_buildings not in {0, 1}:
#     add_buildings = int(input("Please type the matching number: "))

# add_railways('Add railways?: 1 - Yes, 0 - No')
# add_buildings = None
# while add_railways not in {0, 1}:
#     add_railways = int(input("Please type the matching number: "))

# print('Choose gradient: 1 - From top, 2 - From bottom, 3 - None')
# gradient_position = None
# while gradient_position not in {1, 2, 3}:
#     gradient_position = int(input("Please type the matching gradient position's number: "))


# quickly make a selection for test, uncomment the lines above to make a manual selection and comment lines below
start_time = time.time()
response = 2
add_water = 1
add_buildings = 0
add_railways = 0
color_palette = 3
gradient_position = 2

#  Compose the path to the output file with the input data
for key in responses.keys():
    responses[key]=globals()[key]
if response == 2:
    responses['dist'] = dist

filename = city
for key, value in responses.items():
    filename += f"_{value}"
filename += f".{extension}"
fp_result = os.path.join(img_folder, filename)


# Determine text position based on gradient position
if gradient_position in {None, 2, 3}:
    text_position = 'bottom'
else:
    text_position = 'top'
    
print('Retrieve data')

if response == 1:
    start_time = time.time()
    bbox = bbox_boundary
    Groads = ox.graph_from_place(place, truncate_by_edge = True, retain_all=True, simplify = True, network_type='drive')
else:
    start_time = time.time()
    bbox = bbox_distance
    Groads = ox.graph_from_bbox(
        bbox=bbox, truncate_by_edge=True, retain_all=True, simplify=True, network_type='drive')

def get_graph(G, bbox=None, edge_color=None, edge_linewidth=None, filepath=None):
    fig, ax = ox.plot_graph(G, node_size=0, figsize=figsize, bbox=bbox,
                            dpi=dpi, bgcolor='None',
                            save=True, edge_color=edge_color,
                            edge_linewidth=edge_linewidth, edge_alpha=None, filepath=filepath, close=True)
    return fig


def classify_roads (gdf_edges: 'gpd.GeoDataFrame') -> list:
    print('Add edges data')
    data = [dd for vv, kk, dd in Groads.edges(data=True, keys=False)]

    def roads_colors_info(response: 'int') -> dict:
        """
    Define roads colors and background Image color.

    Args:
        gdf_edges: gpd.GeoDataFrame containing edges from place.

    Returns:
        lists: Formatted contact information.
        Background colour of the image based on response
    """
        road_info = {
            "tertiary": {"linewidth": 0.1, "colour": "#fff"},
            "service": {"linewidth": 0.1, "colour": "#fff"},
            "living_street": {"linewidth": 0.1, "colour": "#fff"},
            "secondary": {"linewidth": 0.12, "colour": "#fff"},
            "residential": {"linewidth": 0.15, "colour": "#fff"},
            "primary": {"linewidth": 0.20, "colour": "#fff"},
            "motorway": {"linewidth": 0.25, "colour": "#fff"},
            "trunk": {"linewidth": 0.27, "colour": "#fff"},
            "secondary_link": {"linewidth": 0.27, "colour": "#fff"},
            "highway": {"linewidth": 0.30, "colour": "#fff"},
            "default": {"linewidth": 0.05, "colour": "#fff"}
        }
        
        # Define color mappings for each condition
        color_mappings = {
            1: "#778899",   # dark
            2: "#ffffff",   # light blue
            3: "#a3bac8",   # Navy
            4: '#df4546',   # Salmon
            5: '#FE9A2E'    # Dark Orange 
        }
        
        background_color_mapping = {
            1: '#061529',   # dark
            2: '#6aa0c2',   # light blue
            3: '#264353',   # Navy,
            4: '#f6e6d9',   # Salmon
            5: '#000000'    # Dark Orange
            }

        if color_palette:
            # Get the new color based on the condition
            new_color = color_mappings.get(color_palette, "#000000")
            new_bg_color = background_color_mapping.get(color_palette, "#ffffff")
            
            # Update color value in the dictionary
            for road_type, road_colors in road_info.items():
                road_colors["colour"] = new_color
        return road_info, new_bg_color
    
    road_info, bgcolor_roads = roads_colors_info(response)
    
    roadColors, roadWidths = [], []


    for item in data:
        if isinstance(item, dict) and "highway" in item and isinstance(item["highway"], str):
            road_type = item["highway"]
            if road_type in road_info:
                roadWidths.append(road_info[road_type]["linewidth"])
                roadColors.append(road_info[road_type]["colour"])
            else:
                roadWidths.append(road_info["default"]["linewidth"])
                roadColors.append(road_info["default"]["colour"])
        else:
            roadWidths.append(road_info["default"]["linewidth"])
            roadColors.append(road_info["default"]["colour"])
            
    return roadColors, roadWidths, bgcolor_roads

roadColors, roadWidths, bgcolor_roads = classify_roads(Groads.edges)


   
get_graph(Groads, bbox=bbox, edge_color=roadColors, edge_linewidth=roadWidths, filepath=fp_roads)
print(f"plot roads graph {(time.time() - start_time):.1f} seconds")

# ----------------
# End roads block


# Water Block
# ------------

# Function with dissolve and union all polygons into one so that there are no connections to each other, as it was visible on the map.
def get_footprint(gdf: 'gpd.GeoDataFrame', color: 'hex', bbox=None, edge_color='None', edge_linewidth=None, filepath=None) -> 'Image':
    fig, ax = ox.plot_footprints(gdf, color=color, bbox=bbox, figsize=figsize, edge_color=edge_color,
                                  edge_linewidth=edge_linewidth,  bgcolor='None', dpi=dpi, alpha=None,
                                  show=False, close=False, save=True, filepath=filepath)
    return fig, ax

if add_water == 1:
    print('Start Water block')
    image_paths.insert(0,fp_water)

    def union_polygons(geopandas_gdf):
        
        water_polys_gdf = geopandas_gdf[geopandas_gdf['geometry'].geom_type.isin(
            ['Polygon', 'MultiPolygon'])]
        water_zone_gdf = water_polys_gdf[['name', 'geometry', 'type']]
        water_polys_gdf = water_zone_gdf.dissolve(by='type',  dropna=False)
        geometry_list = water_polys_gdf['geometry'].tolist()
        polys_gseries = gpd.GeoSeries(geometry_list, crs=crs)
        boundary_gseries = gpd.GeoSeries(unary_union(polys_gseries))
        data_dict = {'name': 'water', 'geometry': boundary_gseries}
        gdf_polygons = gpd.GeoDataFrame(data_dict, crs=crs)
        
        return gdf_polygons
    
        
    water_tags = {'natural': ['water', 'bay', 'stream'],
            'waterway': ['river', 'canal', 'lake', 'weir', 'waterfall'],
            'water': ['river', 'reflecting_pool', 'basin', 'pond'],
            'place': 'sea', 
            'landuse': 'reservoir', 
            'type': 'waterway', 
            'name:en': 'Bosphorus',
            'leisure': 'marina'}
    
    watercolor_mapping = {
                1: '#293560', # dark blue
                2: '#ffffff', # light blue
                3: '#081e2b', # navy
                4: '#77cad0', # Salmon
                5: '#0a1d40'  # Dark Orange
                }
        
    if color_palette:
        water_color = watercolor_mapping.get(color_palette, "#524439")
        
    if response == 1:
        water = ox.features_from_place(place, tags = water_tags)
    else:
        water = ox.features_from_bbox(bbox = bbox, tags = water_tags)
    
    extract_gdf = union_polygons(water)
    
    # Visualize a GeoDataFrame of geospatial features footprints.
    
    get_footprint(extract_gdf, water_color, bbox=bbox, edge_color='w', edge_linewidth=0.08, filepath=fp_water)

    print(f"plot water graph {(time.time() - start_time):.1f} seconds")
# # ----------------
# # End Water Block


# # # # Buildings block
# # # # ---------------------
# get buildings

if add_buildings == 1:
    print('Start Buildings block')
    image_paths.append(fp_buildings)
    buildings_tags = {'building': True}
    buildings_color_map = {
                1: '#3A485680', # dark blue
                2: '#B1BDC580', # light blue
                3: '#a3bac880', # navy
                4: '#df454680', # salmon
                5: '#FE9A2E80'  # Dark Orange
                }
    if color_palette:
        building_color = buildings_color_map.get(color_palette, "#524439")
    
    if response == 1:
        buildings_gdf = ox.features_from_place(place, tags=buildings_tags)
    else:
        buildings_gdf = ox.features_from_bbox(bbox=bbox, tags=buildings_tags)

    get_footprint(buildings_gdf, building_color, bbox=bbox, edge_color='None', edge_linewidth=None, filepath=fp_buildings)

    print(f"plot buildings graph {(time.time() - start_time):.1f} seconds")

# ----------------
# End Buildings Block


if add_railways == 1:
    print('Start Railroads block')
    image_paths.append(fp_railroads)
    cf = '["railway"~"rail|subway|tram|light_rail|railway|light_rail"]'
    railway_color_map = {
                1: '#6C6A8560', # dark blue 
                2: '#9ACFD960', # light blue
                3: '#8BCDD960', # navy 
                4: '#9E001860', # salmon 
                5: '#ff932660'  # Dark Orange
                }
    if color_palette:
        railway_color = railway_color_map.get(color_palette, "#ffffff80")
        
    if response == 1:
        Grail = ox.graph_from_place(place, truncate_by_edge = True, retain_all=True, simplify = True, custom_filter = cf)
    else:
        Grail = ox.graph_from_bbox(
            bbox=bbox, truncate_by_edge=True, retain_all=True, simplify=True, custom_filter = cf)

    get_graph(Grail, bbox=bbox, edge_color=railway_color, edge_linewidth=0.5, filepath=fp_railroads)
    print(f"plot railways graph {(time.time() - start_time):.1f} seconds")



# # Image and text block
# # ---------------------
# Convert from decimal degrees to degrees, minutes, seconds.
def deg_to_dms(deg, pretty_print=None):
    """
    Convert degrees to dms.
    """
    m, s = divmod(abs(deg)*3600, 60)
    d, m = divmod(m, 60)
    if deg < 0:
        d = -d
    d, m = int(d), int(m)

    if pretty_print:
        if pretty_print == 'latitude':
            hemi = 'N' if d >= 0 else 'S'
        elif pretty_print == 'longitude':
            hemi = 'E' if d >= 0 else 'W'
        else:
            hemi = '?'
        return '{d:d}°{m:d}′{hemi:1s}'.format(
            d=abs(d), m=m, hemi=hemi)
    return d, m, s

# Convert lat/lon to dms coordinates
lat = deg_to_dms(location.latitude, pretty_print='latitude')
lon = deg_to_dms(location.longitude, pretty_print='longitude')
coords = f"{lat} / {lon}"


gradient_mapping = {
            1: [(86,115,132),120, 25], # dark blue
            2: [(255, 255, 255),120, 20], # light blue
            3: [(202, 247, 255),120, 20], # navy
            4: [(255, 255, 255),180, 20], # salmon
            5: [(254, 154, 46),120, 20]   # Dark Orange
            }
if color_palette:
    gradient_color_dict = gradient_mapping.get(color_palette, [(255, 255, 255),180, 20])
startcolor, startalpha, gradientpercentage = gradient_color_dict


def create_gradient_mask(width, height, start_color = None, start_alpha = None, gradient_percentage = None, end_alpha=0):
    """
    Create a gradient mask image with a white-to-transparent gradient.
    """
    # Create a new blank image with an alpha channel
    mask = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(mask)

    # Calculate the height of the gradient mask
    gradient_height = int(gradient_percentage / 100 * height)
    
    if gradient_position == 1:
        # Draw a gradient from white to transparent starting from the top
        for y in range(gradient_height):
            # Calculate alpha value based on y-coordinate
            alpha = int((end_alpha - start_alpha) * (y / gradient_height) + start_alpha)
            color = start_color + (alpha,)
            draw.line([(0, y), (width, y)], fill=color)
    else:
        # Draw a gradient from white to transparent starting from the bottom
        for y in range(height - gradient_height, height):
            # Calculate alpha value based on y-coordinate
            alpha = int((end_alpha - start_alpha) * ((height - y) / gradient_height) + start_alpha)
            color = start_color + (alpha,)
            draw.line([(0, y), (width, y)], fill=color)

    return mask

def apply_mask(image, mask):
    """
    Apply the mask to the image.
    """
    # Create a new image by blending the original image and the mask
    masked_image = Image.alpha_composite(image.convert("RGBA"), mask)

    return masked_image

def add_inscription(image, city_name, coordinates, text_position):
    """
    Add inscriptions to the image.
    """
    # Make image with the same size as original to compose them later together
    text_image = Image.new("RGBA", image.size, (255, 255, 255, 0))
    draw_text = ImageDraw.Draw(text_image)
    # draw_text.convert("RGBA")
    picWidth, picHeight = image.size
    # make font adjustable depending on the image size.
    fontsize = int(picHeight * 240 / 3624)
    font = ImageFont.truetype(fsity, size=fontsize)
    font_countryName = ImageFont.truetype(fsity, size=int(fontsize/3))
    ## change to *.ttf filename wenn using system fonts
    # font = ImageFont.truetype("arial.ttf", size=fontsize) 
    # font_dms = ImageFont.truetype(fnotes, size=int(fontsize/3))
    # font_countryName = ImageFont.truetype("arial.ttf", size=int(fontsize/3))
    
    
    textcolor_mapping = {
                1: ['#ABBFC899','#96A5B7', '#ffffff'], # dark blue
                2: ['#ffffff99', '#6F8799', '#00000099'],   # light blue
                3: ['#F2B5D199', '#d8d1d1', '#00000080'],   # Navy
                4: ['#6f2f4299', '#8E6431', '#ffffff'],  # Salmon 
                5: ['#DFE0DF99', '#DFE0DF', '#ffffff']   # Dark Orange
                }
    if color_palette:
        # Get the new color based on the condition
        text_color = textcolor_mapping.get(color_palette, "#000000")
        
    if text_position == 'top':
        city_name_coord = (picWidth/2, picHeight / 8)
        text_coord = (city_name_coord[0], (city_name_coord[1] - fontsize))
        country_coord = (city_name_coord[0], (city_name_coord[1] - fontsize - int(fontsize/3)))
       
    else:
        city_name_coord = (picWidth/2, picHeight * 0.9)
        text_coord = (city_name_coord[0], (city_name_coord[1]+ fontsize/2))
        country_coord = (city_name_coord[0], (city_name_coord[1]+ fontsize/2 + int(fontsize/3)))
    
    # Calculate the size of the inscription relative to the image for correct positioning
    # Writing the inscriptions
    # Draw city name
    draw_text.text(city_name_coord, city.upper(), font=font, fill=text_color[0],
                    anchor="ms",  spacing=8, stroke_width=3, stroke_fill=text_color[2])
    # Draw coordinates
    draw_text.text(text_coord,
    coords, fill = text_color[1], anchor = "ms", font = font_countryName,  stroke_width = 2,
    stroke_fill = text_color[2])
    # Draw country
    draw_text.text(country_coord, country, fill=text_color[1],
                    anchor="ms", font=font_countryName, stroke_width=2, stroke_fill=text_color[2])
    final_image = Image.alpha_composite(image.convert("RGBA"), text_image.convert("RGBA"))

    return final_image.convert('RGBA') # return text with gradient and base image

def draw_frame(image, outer_white_width=50, black_width=4, inner_white_width=4):
    """
    Draw a frame around the image with the inscription.
    """
    # Create a drawing object
    draw = ImageDraw.Draw(image)

    # Get image dimensions
    width, height = image.size

    # Calculate frame coordinates
    top_left = (0, 0)
    bottom_right = (width - 1, height - 1)

    # Calculate inner rectangle coordinates
    inner_left = outer_white_width
    inner_top = outer_white_width
    inner_right = width - outer_white_width
    inner_bottom = height - outer_white_width

    # Draw outer white frame
    draw.rectangle([top_left, bottom_right], outline="white", width=outer_white_width)

    # Draw black frame
    draw.rectangle([(inner_left, inner_top), (inner_right, inner_bottom)], outline="black", width=black_width)

    # Draw inner white frame
    inner_left += black_width
    inner_top += black_width
    inner_right -= black_width
    inner_bottom -= black_width
    draw.rectangle([(inner_left, inner_top), (inner_right, inner_bottom)], outline="white", width=inner_white_width)

    # Draw second black frame
    inner_left += inner_white_width
    inner_top += inner_white_width
    inner_right -= inner_white_width
    inner_bottom -= inner_white_width
    draw.rectangle([(inner_left, inner_top), (inner_right, inner_bottom)], outline="black", width=black_width)

    return image

def composite_images(base_image, image_with_inscription_path, save_path):
    """
    Combine all images to get the final image.
    """
    try:
        # Check if image_with_inscription is a PIL Image object
        if not isinstance(image_with_inscription_path, Image.Image):
            raise ValueError("image_with_inscription is not a PIL Image object")
        
        # Composite images
        final_image = Image.alpha_composite(base_image, image_with_inscription_path.convert("RGBA"))
        
        # Save the result
        final_image.save(save_path)
        print("Image saved successfully")
    
    except FileNotFoundError as e:
        print("Error: File not found:", e.filename)
    
    except Exception as e:
        print("An error occurred:", e)

def merge_images(image_paths: 'list', base_image: 'Image') -> 'Image':
    for path in image_paths:
        image = Image.open(path).convert("RGBA")
        base_image = Image.alpha_composite(base_image, image)
    return base_image

def delete_temp_images(image_paths: 'list'):
    for path in image_paths:
        image_path_to_delete = os.path.join(path)
        os.remove(image_path_to_delete)

def get_image_size(image_path):
    
    with Image.open(image_path) as img:
        return img.size
    
image_size = get_image_size(fp_roads)

background_color = ImageColor.getcolor(bgcolor_roads, "RGB")
background_image = Image.new("RGBA", image_size, background_color)


base_image = merge_images(image_paths, background_image)


text_position = text_position
if gradient_position in {1, 2}:
    # Create a gradient mask
    mask = create_gradient_mask(base_image.width, base_image.height, start_color = startcolor, start_alpha = startalpha, gradient_percentage = gradientpercentage)
    
    # Apply the mask to the original image
    masked_image = apply_mask(base_image, mask)
    # Apply inscription to the masked image
    image_with_inscription = add_inscription(masked_image, city, coords, text_position)
    # output_image = draw_frame(image_with_inscription)
else:
    image_with_inscription = add_inscription(base_image, city, coords, text_position)

output_image = draw_frame(image_with_inscription)

# compose and display the final image
composite_images(base_image, output_image, fp_result)

# delete temp images
delete_temp_images(image_paths)

print(f"all jobs done {(time.time() - start_time):.1f} seconds")

