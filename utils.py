import logging
import pathlib
import re
from functools import lru_cache
from typing import Tuple

from pyproj import Transformer

# Typing
Latitude = float
Longitude = float

LatitudeLeft = float
LongitudeBottom = float
LatitudeRight = float
LatitudeTop = float

logging.basicConfig(format="[%(asctime)s] [%(levelname)s] %(message)s", level=logging.DEBUG)
log = logging.getLogger(__name__)

TransformerFromCRS = lru_cache(Transformer.from_crs)


def get_bounding_box(
    image_filepath: pathlib.Path,
) -> Tuple[LatitudeLeft, LongitudeBottom, LatitudeRight, LatitudeTop]:
    """Return 1000x1000 meters bounding box"""
    pattern = r"dop10rgbi_32_(\d+)_(\d+)_1_nw_\d{4}\.jp2"
    match = re.match(pattern, image_filepath.name)
    if not match:
        raise ValueError(
            f"Incorrect filepath. Got {image_filepath}," "expected 'dop10rgbi_32_<easting>_<northing>_1_nw_<year>.jp2'"
        )

    latitude_left = int(match.group(1)) * 1000
    latitude_right = latitude_left + 999
    longitude_bottom = int(match.group(2)) * 1000
    latitude_top = longitude_bottom + 999

    return (latitude_left, longitude_bottom, latitude_right, latitude_top)


def is_bbox_intersects(tile_bbox, final_image_bbox) -> bool:
    """Return boolean if tile image and final generated image overlap or not."""
    (tile_bbox_left, tile_bbox_bottom, tile_bbox_right, tile_bbox_top) = tile_bbox
    (final_image_bbox_left, final_image_bbox_bottom, final_image_bbox_right, final_image_bbox_top) = final_image_bbox

    if tile_bbox_right < final_image_bbox_left or tile_bbox_left > final_image_bbox_right:
        return False
    if tile_bbox_top < final_image_bbox_bottom or tile_bbox_bottom > final_image_bbox_top:
        return False

    return True


def convert_epsg_4326_to_epsg_25832(latitude: Latitude, longitude: Longitude) -> Tuple[Latitude, Longitude]:
    log.debug(
        f"Converting from 'EPSG:4326' (latitude,longitude) ({latitude}^, {longitude}^) degrees to 'EPSG:25832' meters."
    )
    wgs84_to_utm32 = TransformerFromCRS("EPSG:4326", "EPSG:25832", always_xy=True)
    latitude, longitude = wgs84_to_utm32.transform(xx=latitude, yy=longitude)
    log.debug(f"Converted to (latitude, longitude) ({latitude},{longitude}) meters")
    return (latitude, longitude)


def convert_epsg_25832_to_epsg_4326(latitude: float, longitude: float) -> Tuple[Latitude, Longitude]:
    log.debug(f"Converting from 'EPSG:25832' (latitude, longitude) ({latitude}m, {longitude}m) to 'EPSG:4326' degrees.")
    utm32_to_wgs84 = TransformerFromCRS("EPSG:25832", "EPSG:4326", always_xy=True)
    latitude, longitude = utm32_to_wgs84.transform(xx=latitude, yy=longitude)
    log.debug(f"Converted to (latitude, longitude): ({latitude}, {longitude}) degrees")
    return (latitude, longitude)
