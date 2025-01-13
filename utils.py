import logging
import pathlib
import re
from functools import lru_cache
from typing import List, Tuple

import numpy as np
import rasterio
from PIL import Image
from pyproj import Transformer

# Typing
Latitude = float
Longitude = float

LatitudeLeft = float
LongitudeBottom = float
LatitudeRight = float
LatitudeTop = float

logging.basicConfig(format="[%(asctime)s] [%(levelname)s] %(message)s", level=logging.INFO)
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


def concat_hortizontally(left_image, right_image):
    dst = Image.new("RGB", (left_image.width + right_image.width, left_image.height))
    dst.paste(left_image, (0, 0))
    dst.paste(right_image, (left_image.width, 0))
    return dst


def concat_vertically(top_image, bottom_image):
    dst = Image.new("RGB", (top_image.width, top_image.height + bottom_image.height))
    dst.paste(top_image, (0, 0))
    dst.paste(bottom_image, (0, top_image.height))
    return dst


def get_file_latitude_longitude(
    tile_image_path: pathlib.Path,
) -> Tuple[Latitude, Longitude]:
    pattern = r"dop10rgbi_32_(\d+)_(\d+)_1_nw_\d{4}\.jp2"
    match = re.match(pattern, tile_image_path.name)
    if match is None:
        # TODO @Karim: Need to handle the case when it's different file name convention
        raise ValueError(f"Invalid file name format: {tile_image_path.name}")
    return (float(match.group(1)), float(match.group(2)))


def generate_tile_image(
    tile_bounding_box: Tuple[LatitudeLeft, LongitudeBottom, LatitudeRight, LatitudeTop],
    tile_image_path: pathlib.Path,
):
    log.info(f"Generating {tile_image_path.stem} tile image")
    with rasterio.open(tile_image_path) as src:
        window = rasterio.windows.from_bounds(
            *tile_bounding_box,
            transform=src.transform,
        )
        log.info(window)
        partial_rgb = src.read([1, 2, 3], window=window)
        log.info(partial_rgb.shape)

        partial_rgb = np.transpose(partial_rgb, (1, 2, 0))
        return Image.fromarray(partial_rgb, mode="RGB")


def concat_two_tile_images(
    final_image_bounding_box: Tuple[LatitudeLeft, LongitudeBottom, LatitudeRight, LatitudeTop],
    tile_image_paths: List[pathlib.Path],
):
    first_tile_langitude, first_tile_longitude = get_file_latitude_longitude(tile_image_paths[0])
    second_tile_langitude, second_tile_longitude = get_file_latitude_longitude(tile_image_paths[1])

    if first_tile_langitude == second_tile_langitude:
        if first_tile_longitude < second_tile_longitude:
            return concat_vertically(
                generate_tile_image(final_image_bounding_box, tile_image_paths[0]),
                generate_tile_image(final_image_bounding_box, tile_image_paths[1]),
            )
        else:
            return concat_vertically(
                generate_tile_image(final_image_bounding_box, tile_image_paths[1]),
                generate_tile_image(final_image_bounding_box, tile_image_paths[0]),
            )
    elif first_tile_longitude == second_tile_longitude:
        if second_tile_langitude > first_tile_langitude:
            return concat_hortizontally(
                generate_tile_image(final_image_bounding_box, tile_image_paths[0]),
                generate_tile_image(final_image_bounding_box, tile_image_paths[1]),
            )
        else:
            return concat_hortizontally(
                generate_tile_image(final_image_bounding_box, tile_image_paths[1]),
                generate_tile_image(final_image_bounding_box, tile_image_paths[0]),
            )
