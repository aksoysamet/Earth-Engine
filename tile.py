from tilematrix import TilePyramid
from shapely.geometry import Polygon
import math
# initialize TilePyramid
tile_pyramid = TilePyramid("geodetic")

# some_polygon = Polygon([(28.18114792845247, 40.536185527959724), (28.18114792845247, 41.545593768518934), (29.514538390583656, 41.545593768518934), (29.514538390583656, 40.536185527959724)])
some_polygon = Polygon([(26.19, 36.18), (26.19, 39.96), (31.725000000000005, 39.96), (31.725000000000005, 36.18)])
zoom = 7
total_row = tile_pyramid.matrix_height(zoom)
for tile in tile_pyramid.tiles_from_geom(some_polygon, zoom):
    meta_tile = math.ceil(zoom/2.0)-1
    # print(next(tile_pyramid.tiles_from_geom(tile.bbox(), meta_tile)).id)
    mt = next(tile_pyramid.tiles_from_geom(tile.bbox(), meta_tile))
    total_meta_row = tile_pyramid.matrix_height(meta_tile)
    zero_padding = math.floor(zoom/6)+1
    print("EPSG_4326_" + str(tile.id.zoom).zfill(2) + 
    f"/{str(mt.id.col).zfill(zero_padding)}_{str(total_meta_row-mt.id.row-1).zfill(zero_padding)}/{str(tile.id.col).zfill(zero_padding*2)}_{str(total_row-tile.id.row-1).zfill(zero_padding*2)}.png")
    # print(tile.bbox())
