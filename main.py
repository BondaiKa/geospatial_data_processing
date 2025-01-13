import logging
import pathlib
from pathlib import Path
from typing import List, Tuple

import numpy as np
import rasterio
from PIL import Image
from rasterio.windows import from_bounds

from utils import convert_epsg_4326_to_epsg_25832, convert_epsg_25832_to_epsg_4326, get_bounding_box, is_bbox_intersects

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

    final_image_bounded_box = (latitude_left, longitude_bottom, latitude_right, longitude_top)

    tile_image_paths = get_paths_of_tile_images(final_image_bounded_box, Path(dataset_directory_path))

    if not tile_image_paths:
        # TODO @Karim: I need to consider case when I selected last image in dataset (e.g no image below and right).
        # So I need to create partial black image and concat with exist tile.
        log.warning("No tiles intersecting the bounding box. Returning a blank 256x256 image.")
        blank_img = Image.new("RGB", (256, 256), color="black")
        return blank_img

    # 1) Create a "mosaic" NumPy array for the bounding box
    #    We'll define a resolution of 1 pixel per meter (naive) => 2*radius wide/high
    #    Then we can resize to 256x256 in the end.

    mosaic_width = int(latitude_right - latitude_left + 1)
    mosaic_height = int(longitude_top - longitude_bottom + 1)

    # If radius=100, mosaic_width ~ 200 px, mosaic_height ~ 200 px
    if mosaic_width <= 0 or mosaic_height <= 0:
        error_message = "Bounding box dimensions invalid. Returning."
        log.error(error_message)
        raise Exception(error_message)

    log.debug(f"Creating mosaic array of size {mosaic_width}x{mosaic_height}")
    mosaic = np.zeros((mosaic_height, mosaic_width, 3), dtype=np.uint8)

    # 2) Read partial data from each tile and paste into mosaic
    for jp2_file in tile_image_paths:
        try:
            with rasterio.open(jp2_file) as src:
                # Build a Window from our bounding box in EPSG:25832
                window = from_bounds(
                    left=latitude_left,  # x_min
                    bottom=longitude_bottom,  # y_min
                    right=latitude_right,  # x_max
                    top=longitude_top,  # y_max
                    transform=src.transform,
                )

                # Read the first 3 bands (assuming RGB; adjust if your .jp2 has more/different bands)
                partial_data = src.read([1, 2, 3], window=window)
                # partial_data shape: (3, h, w)

                partial_data = np.transpose(partial_data, (1, 2, 0))  # shape: (h, w, 3)
                partial_data = np.clip(partial_data, 0, 255).astype(np.uint8)

                # 3) Figure out where to place partial_data in the mosaic
                #    We'll define top-left of mosaic as (latitude_left, longitude_top)
                #    so pixel (0,0) in mosaic corresponds to (x=latitude_left, y=longitude_top).

                # RasterIO has origin top-left, but in EPSG coords top > bottom.
                # We'll invert row index: row = top - pixel_y, col = pixel_x - left

                # Let's find out the actual bounding box of the partial read
                actual_bounds = rasterio.windows.bounds(window, transform=src.transform)
                read_left, read_bottom, read_right, read_top = actual_bounds

                # Convert bounding box to mosaic indices
                # col = x - latitude_left; row = longitude_top - y
                start_col = int(read_left - latitude_left)
                end_col = start_col + partial_data.shape[1]
                start_row = int(longitude_top - read_top)
                end_row = start_row + partial_data.shape[0]

                # Clip if out of mosaic array bounds
                # E.g. partial read can exceed the mosaic range
                mosaic_slice_y0 = max(0, start_row)
                mosaic_slice_y1 = min(mosaic_height, end_row)
                mosaic_slice_x0 = max(0, start_col)
                mosaic_slice_x1 = min(mosaic_width, end_col)

                # partial_data slice offsets
                data_slice_y0 = max(0, -start_row)  # how many rows to skip if start_row < 0
                data_slice_y1 = data_slice_y0 + (mosaic_slice_y1 - mosaic_slice_y0)
                data_slice_x0 = max(0, -start_col)
                data_slice_x1 = data_slice_x0 + (mosaic_slice_x1 - mosaic_slice_x0)

                if mosaic_slice_y1 > mosaic_slice_y0 and mosaic_slice_x1 > mosaic_slice_x0:
                    mosaic[mosaic_slice_y0:mosaic_slice_y1, mosaic_slice_x0:mosaic_slice_x1, :] = partial_data[
                        data_slice_y0:data_slice_y1, data_slice_x0:data_slice_x1, :
                    ]

        except Exception as e:
            log.error(f"Error reading tile {jp2_file}: {e}")
            continue

    # 4) Convert the mosaic to a PIL image and resize to 256x256
    mosaic_img = Image.fromarray(mosaic, mode="RGB")
    final_img_256 = mosaic_img.resize((256, 256), resample=Image.BILINEAR)  # type: ignore

    # 5) Show or return the final imag
    # If you prefer to return it instead of showing:
    return final_img_256


if __name__ == "__main__":
    logging.basicConfig(format="[%(asctime)s] [%(levelname)s] %(message)s", level=logging.DEBUG)

    # In the middle coordinates of 'dop10rgbi_32_468_5772_1_nw_2022' image file.
    # Expected to provide 1 tile  (cutted  in the middle 'dop10rgbi_32_468_5772_1_nw_2022' image)
    # get_image(
    #     latitude=8.54010563577907,
    #     longitude=52.10215462837978,
    #     dataset_directory_path="/Users/ksafiullin/src/geospatial_data_processing/data/orthophotos/nw",
    #     radius=100,
    # ).show()

    # # Test on the corner of 'dop10rgbi_32_468_5772_1_nw_2022', will it provide 4 tiles or not.
    get_image(
        *convert_epsg_25832_to_epsg_4326(468002, 5772002),
        dataset_directory_path="/Users/ksafiullin/src/geospatial_data_processing/data/orthophotos/nw",
    ).show()
