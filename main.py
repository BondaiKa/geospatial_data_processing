import copy
import logging
import pathlib
from pathlib import Path
from typing import List, Tuple

from PIL import Image

from utils import (
    concat_two_tile_images,
    concat_vertically,
    convert_epsg_4326_to_epsg_25832,
    convert_epsg_25832_to_epsg_4326,
    generate_tile_image,
    get_bounding_box,
    is_bbox_intersects,
)

logging.basicConfig(format="[%(asctime)s] [%(levelname)s] %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)

# Typing
Latitude = float
Longitude = float

LatitudeLeft = float
LongitudeBottom = float
LatitudeRight = float
LatitudeTop = float


def validate_input(latitude: float, longitude: float, radius: float = 100, epsg_25832=False) -> None:
    log.info(f"Incoming latitude '{latitude}' and longitude '{longitude}' with set radius '{radius}'.")

    if not epsg_25832 and (not -90 < latitude < 90 and not -180 < longitude < 180):
        warning_message = (
            "Expected to have Geographic CRS `EPSG:4326` input format (in degress). Looks "
            "like provided input data is in `EPSG:25832`. In case of using directly EPSG:25832, "
            "set 'epsg_25832=True'!"
        )
        log.warning(warning_message)

    if radius < 0 or radius > 100:
        log.warning(f"Radius expected to be from 0 meters till 100 meters. Received {radius} meters.")


def get_paths_of_tile_images(
    image_bounded_box: Tuple[LatitudeLeft, LongitudeBottom, LatitudeRight, LatitudeTop],
    dataset_directory_full_path: pathlib.Path,
) -> List[pathlib.Path]:

    relevant_tiles = []

    for image_file in dataset_directory_full_path.glob("*.jp2"):
        tile_bounded_box = get_bounding_box(image_file)
        if not tile_bounded_box:
            error_message = "Something goes wrong with parsing image"
            log.error(error_message)
            # TODO @Karim: handle this error better later.
            raise Exception(error_message)

        if is_bbox_intersects(tile_bounded_box, image_bounded_box):
            relevant_tiles.append(image_file)

    logging.info(f"Found {len(relevant_tiles)} tile(s) intersecting the required area.")
    return relevant_tiles


def get_image(
    latitude: float,
    longitude: float,
    dataset_directory_path: str,
    radius: float = 100,
    epsg_25832=False,
    final_image_size: Tuple[int, int] = (256, 256),
) -> Image.Image:
    """Generate a 256x256 pixels image for the input (latitude, longitude) in
    EPSG:4326/EPSG:25832 format with a given radius in meters.

    - 'latitude' and 'longitude' must be in 'EPSG:4326' or 'EPSG:25832' format.
    - 'radius' value expected to be '0' till '100' meters.
    - 'dataset_directory_path' - orthophotos directory full path
        (E.g. '/Users/ksafiullin/src/geospatial-data-processing/data/orthophotos/nw').

    Steps:
    1) Verify incoming data is on EPSG:4326 format.
    2) Compute bounding box: (left, bottom, right, top).
    3) Find all relevant tiles that intersect with this bounding box.
    4) Partially read from each tile.
    5) Concatenate the partial reads into one final image.
    6) Crop/resize to 256x256.
    """
    log.debug(f"Reading set input data: lat {latitude}, long: {longitude}, and radius {radius}.")
    validate_input(latitude=latitude, longitude=longitude, radius=radius, epsg_25832=False)

    # If it's EPSG:4326 and not EPSG:25832 format, transforms degrees to meters
    if not epsg_25832:
        latitude, longitude = convert_epsg_4326_to_epsg_25832(latitude=latitude, longitude=longitude)

    latitude_left = latitude - radius
    longitude_bottom = longitude - radius
    latitude_right = latitude + radius
    longitude_top = longitude + radius

    final_image_bounding_box = (latitude_left, longitude_bottom, latitude_right, longitude_top)

    tile_image_paths = get_paths_of_tile_images(final_image_bounding_box, Path(dataset_directory_path))

    if not tile_image_paths:
        # TODO @Karim: I need to consider case when I selected last image in dataset (e.g no image below and right).
        # So I need to create partial black image and concat with exist tile.
        log.warning("No tiles intersecting the bounding box. Returning a blank 256x256 image.")
        return Image.new("RGB", final_image_size, color="black")

    if len(tile_image_paths) == 1:
        return generate_tile_image(final_image_bounding_box, tile_image_paths[0]).resize(
            (256, 256), Image.BILINEAR  # type: ignore
        )

    if len(tile_image_paths) == 2:
        return (
            concat_two_tile_images(final_image_bounding_box, tile_image_paths)
            .resize((256, 256), Image.BILINEAR)  # type: ignore
            .show()
        )

    if len(tile_image_paths) == 4:
        _tile_image_paths = copy.deepcopy(tile_image_paths)
        _tile_image_paths.sort()
        return concat_vertically(
            concat_two_tile_images(final_image_bounding_box, [_tile_image_paths[1], _tile_image_paths[3]]),
            concat_two_tile_images(final_image_bounding_box, [_tile_image_paths[0], _tile_image_paths[2]]),
        ).resize(
            (256, 256), Image.BILINEAR  # type: ignore
        )
    else:
        error_message = (
            "I didn't implement other cases with missing images in dataset, "
            "except when there is no found tile images at all."
        )
        log.error(error_message)
        raise NotImplementedError(error_message)


if __name__ == "__main__":
    logging.basicConfig(format="[%(asctime)s] [%(levelname)s] %(message)s", level=logging.INFO)

    ###############################################################################################
    # In the middle coordinates of 'dop10rgbi_32_468_5772_1_nw_2022' image file.
    # Expected to provide 1 tile  (cutted  in the middle 'dop10rgbi_32_468_5772_1_nw_2022' image)
    ###############################################################################################
    get_image(
        latitude=8.54010563577907,
        longitude=52.10215462837978,
        dataset_directory_path="/Users/ksafiullin/src/geospatial_data_processing/data/orthophotos/nw",
        radius=100,
    ).show()

    ###############################################################################################
    # Test on the corner of 'dop10rgbi_32_468_5772_1_nw_2022', will it provide 4 tiles or not.
    ###############################################################################################
    get_image(
        *convert_epsg_25832_to_epsg_4326(468002, 5772002),
        dataset_directory_path="/Users/ksafiullin/src/geospatial_data_processing/data/orthophotos/nw",
    ).show()
