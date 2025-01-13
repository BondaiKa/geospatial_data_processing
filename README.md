# Geospatial Data Processing
A comprehensive repository, that contains all necesary information/instructures/code for preprocessing orthophotos based on geospatial queries, including stitching, resizing, and performance optimization.

## Project Structure

- `notebooks/` - contains analysis or attempt walkthrough how I solved some issues
- `main.py` - entrypoin of the repostory.
- `utils.py` - is used in `main.py` as well as in notebooks.
- `pyproject.toml` - list of packages to install (similar to `requirements.txt`)

## General information
- Official started date: 10.01.2024 (14:00 CET)
- Real started date: 11.01.2024
- Deadline: 14.01.2024 (14:00 CET, when I received an email)

## Prequistitions

- [X] Proficiency in Python programming.
- [X] Knowledge of Geospatial data handling, GIS, and Coordinate Reference Systems (CRS).
- [X] Experience with image processing libraries in Python, such as PIL or OpenCV.

## Task

### TODO List
- [X] Read carefully task defintion (2 times or more to verify that this is exactly what company asks!) and write for yourself task definition.
    - [X] Verify that you don't need to read image to provide `Latitude` and `Longitude`.
    - [X] Find the way how to use the promt with constant `radious`.
- [X] Understand data first (at least read it and look with you own eyes!).
- [X] Learn more about Geospatial data handling, GIS, and Coordinate Reference Systems (CRS).
- [X] Write `dumb` pipeline (_time_ is more important than _optimization_) for now.
- [ ] Add tests.
- [ ] Add `click` libarary to run main.py  more conveniet way and play with `latitude` and `longitudes` in terminal.
- [X] Document the process.
- [ ] Write draft slides.
- [X] Optimize the process.
    - [X] Check the ways of potential optimization of input images. Can I not read whole image?
- [X] Update Documentation.
- [X] Do performance analysis (Partially achieved).
- [X] Submit.

### 🚀 Main Goal: 
Retrieve and return `image` from data from provided `latitude` and `longitude`.

#### Input data
- Sample of [provided dataset](https://drive.usercontent.google.com/download?id=140PpLsdnVOQVIp5ia9jT_yvqtcWtF8Gj&export=download&confirm=t&uuid=483b1776-4e25-4976-9837-b498c823754a) was given. 
- One image has 1x1 km area.
- Real dataset could be much bigger than provided one.
- There is information, that one filename `...X_Y...` has latitude, longtitude range from `X/Y` till `X/Y+1000` and I need to extract It.
- `radius` param could be from `1` till `100` meters.

## Installation

To get started with this project, follow the steps below:

0. **Prequistitions**:
    - Install `python`, `poetry`.
1. **Clone the Repository**:
   ```bash
   git clone git@github.com:BondaiKa/geospatial_data_processing.git
   cd geospatial_data_processing
   ```
2. poetry install
    ```bash
    poetry install
    ```
3. Run main.py
    ```bash
    poetry run python main.py
    ```

## Developing / Technical documentation
### Name Conventions in the Project.

`Latitude`, `Longitude` are preferable to use as variables in this project. 

Prefer `Projcted CRS` to `Geographic CRS`.
- `Latitude`/`X`/ `Easting` are always come first in coordinates pair.
- `Longitude`/`Y`/ `Northing` are always come second in coordinates pair.

In case of boxes there is next order convention (Latitude comes first, Longitude second here as well):
- Latitude Left (Min X), Longitude Bottom (Min Y), Latitude Right (Max X), Latitude Top (Max Y)  
(⬅️, ⬇️, ➡️, ⬆️)

## My Developing Journal

Once I read requirements, I have next thoughts in my mind:
##### 👀 Observation №1
> ⚠️ It was mentioned that the dataset's size could be even bigger, so candidate (I) should consider the case that whole data can't fit in memory.  **Restriction №1**: Don't put whole dataset into memory use iterator, batch, micro-batch processing whatever.

##### 👀 Observation №2
> `Latitude` and `Longitude` are written in filename already - so for that you don't even need to read image for that.

##### 👀 Observation №3
>  _Imagine that the images were being retrieved over network on the fly. We encourage you to come up with ways to preprocess the data to optimize the retrieval process._ So they ask you to think about the way to optimize incomming images (maybe it's not needed, but I need to check).

##### 👀 Observation №4
>  _Consider that while the radius parameter remains generally fixed, the latitude and longitude parameters will vary randomly across requests._ For I don't understand their promt about constant `radious`. For now (11.01.2024) I don't have any idea how to use it in optimization... Caching? One degree left or right - and it's different image, you need to change input 1x1 km into super small images (e.g. 1x1 meter). Then yes,it's possible to cache and use old computation.

#### ❗️ Challenge that I need to solve (it's not optional)
- Users will type `latitude` and `longitude` and `radious`. One image has `1x1 km` area. It's possible, that user set almost the edge of one image. In that case, I need to retrieve nearest required images (in worst case scenario additional `3` images), that covers radious and return final 256x256 image.
- Handle all posssible errors.

#### ❗️ Challenge that I need to solve (optional)
- Optimize time execution of `get_image(lat, long, radius)` function with any possible way. 