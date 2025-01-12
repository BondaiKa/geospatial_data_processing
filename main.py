import logging
import pathlib
from pathlib import Path
from typing import List

from utils import convert_epsg_4326_to_epsg_25832, convert_epsg_25832_to_epsg_4326, get_bounding_box, is_bbox_intersects

logging.basicConfig(format="[%(asctime)s] [%(levelname)s] %(message)s", level=logging.DEBUG)
log = logging.getLogger(__name__)

# Typing
Latitude = float
Longitude = float

LatitudeLeft = float
LongitudeBottom = float
LatitudeRight = float
LatitudeTop = float


def validate_input(latitude: float, longitude: float, radius: float = 100, projected_crs=False) -> None:
    log.info(f"Incoming latitude '{latitude}' and longitude '{longitude}' with set radius '{radius}'.")

    if not projected_crs and (not -90 < latitude < 90 and not -180 < longitude < 180):
        warning_message = (
            "Expected to have Geographic CRS `EPSG:4326` input format (in degress). Looks "
            "like provided input data is in `EPSG:25832`. In case of using directly EPSG:25832, "
            "set 'epsg_25832=True'!"
        )
        log.warning(warning_message)

    if radius < 0 or radius > 100:
        log.warning(f"Radius expected to be from 0 meters till 100 meters. Received {radius} meters.")


def get_paths_of_required_images(
    latitude_left: float,
    longitude_bottom: float,
    latitude_right: float,
    latitude_top: float,
    dataset_directory_full_path: pathlib.Path,
) -> List[pathlib.Path]:
    final_image_bounded_box = (latitude_left, longitude_bottom, latitude_right, latitude_top)

    relevant_tiles = []

    for image_file in dataset_directory_full_path.glob("*.jp2"):
        tile_bounded_box = get_bounding_box(image_file)
        if not tile_bounded_box:
            error_message = "Something goes wrong with parsing image"
            log.error(error_message)
            raise Exception(error_message)

        if is_bbox_intersects(tile_bounded_box, final_image_bounded_box):
            relevant_tiles.append(image_file)

    logging.info(f"Found {len(relevant_tiles)} tile(s) intersecting the required area.")
    return relevant_tiles


def get_image(
    latitude: float,
    longitude: float,
    dataset_directory_path: str,
    radius: float = 100,
    projected_crs=False,
) -> None:
    """Generate a 256x256 pixels image for the input (latitude, longitude) in
    EPSG:4326/EPSG:25832 format with a given radius in meters.

    - 'latitude' and 'longitude' must be in 'EPSG:4326' or 'EPSG:25832' format.
    - 'radius' value expected to be '0' till '100' meters.
    - 'dataset_directory_path' - orthophotos directory full path
        (E.g. '/Users/ksafiullin/src/geospatial-data-processing/data/orthophotos/nw')

    Steps:
    1) Verify incoming data is on EPSG:4326 format.
    2) Compute bounding box: (left, bottom, right, top).
    3) Find all relevant tiles that intersect with this bounding box.
    4) Partially read from each tile.
    5) Concatenate the partial reads into one final image.
    6) Crop/resize to 256x256.
    """
    log.debug(f"Reading set input data: lat {latitude}, long: {longitude}, and radius {radius}.")
    validate_input(latitude=latitude, longitude=longitude, radius=radius, projected_crs=False)

    # If it's EPSG:4326 and not EPSG:25832 format, transforms degrees to meters
    if not projected_crs:
        latitude, longitude = convert_epsg_4326_to_epsg_25832(latitude=latitude, longitude=longitude)

    latitude_left = latitude - radius
    longitude_bottom = longitude - radius
    latitude_right = latitude + radius
    latitude_top = longitude + radius

    tile_image_paths = get_paths_of_required_images(
        latitude_left, longitude_bottom, latitude_right, latitude_top, Path(dataset_directory_path)
    )

    log.info(tile_image_paths)


if __name__ == "__main__":
    logging.basicConfig(format="[%(asctime)s] [%(levelname)s] %(message)s", level=logging.DEBUG)

    # In the middle coordinates of 'dop10rgbi_32_468_5772_1_nw_2022' image file.
    # Expected to provide 1 tile  (cutted  in the middle 'dop10rgbi_32_468_5772_1_nw_2022' image)
    get_image(
        latitude=8.54010563577907,
        longitude=52.10215462837978,
        dataset_directory_path="/Users/ksafiullin/src/geospatial-data-processing/data/orthophotos/nw",
        radius=100,
    )

    # Test on the corner of 'dop10rgbi_32_468_5772_1_nw_2022' how many tiles will provide.
    get_image(
        *convert_epsg_25832_to_epsg_4326(468002, 5772002),
        dataset_directory_path="/Users/ksafiullin/src/geospatial-data-processing/data/orthophotos/nw",
    )
