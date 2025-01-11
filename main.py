import logging

import matplotlib.pyplot as plt
import rasterio

log = logging.getLogger(__name__)


def get_image(lat: float, long: float, radius: float = 100) -> None:
    logging.info(f"Reading set input data: lat {lat}, long: {long}, and radius {radius}.")
    image_path = "data/orthophotos/nw/dop10rgbi_32_462_5766_1_nw_2022.jp2"

    with rasterio.open(image_path) as src:
        # Read the first band (geospatial rasters can have multiple bands)
        data = src.read(1)  # Band 1 is often the main data

        # Display metadata about the file
        print("File metadata:")
        print(src.meta)

        # Plot the data
        plt.imshow(data, cmap="viridis")
        plt.colorbar(label="Values")
        plt.title("Geospatial Data Visualization")
        plt.xlabel("X Coordinate")
        plt.ylabel("Y Coordinate")
        plt.show()


if __name__ == "__main__":
    logging.basicConfig(format="[%(asctime)s] [%(levelname)s] %(message)s", level=logging.INFO)
    get_image(1, 1)
