# osmnx_maps

Project Description

Users can load and model urban networks suitable for pedestrians, cars, or cyclists with a single line of Python code, and then easily analyze and visualize them.

I returned to this project after completing the first version because I realized it would be beneficial to visualize water bodies. A map without them looks quite odd, especially since data on water bodies is available in OSM. When I started working on this, I decided to redo the entire project because the road visualization was done schematically. While this was acceptable for the first version, it had its flaws. The same road could have different line thickness and colors because these attributes were calculated based on the length of coordinate segments rather than the road's purpose or its entire section. For example, if a road from point A to point B is marked as a "pedestrian road" or "highway," it should have consistent line thickness and color in the visualization.

When working with water bodies, I discovered they mostly consist of numerous polygons rather than a single multipolygon. As a result, visualizing a water body would show the boundaries of each polygon, which I found aesthetically displeasing. While making them transparent was an option, it would obscure the outlines of the water bodies.

Thus, I decided to merge all water surfaces into a single multipolygon to eliminate these boundaries.

Additionally, I implemented a text menu allowing users to choose what to visualize on the map, such as buildings, roads, water bodies, or railways. Users can also select suitable color palettes through the menu. This enables the option to display only roads and water, just buildings, and so on.

As a result, almost the entire code was rewritten. The new version allows for the addition of water bodies, buildings, and railway infrastructure to the map, application of various palettes for visualization, adjustment of label placements, and overlaying gradients. I also added a frame to enhance the map's appearance.

Overall, these improvements make the tool more versatile and aesthetically pleasing.