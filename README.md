# Geospatial Data Processing
A comprehensive repository, that contains all necesary information/instructures/code for preprocessing orthophotos based on geospatial queries, including stitching, resizing, and performance optimization.

This `README.md` is strict format documenatation.  
More documentation/all my thoughts in informal way I wrote [here](./docs/INFORMAL-README.md).
## General information
- Official started date: 10.01.2024 (14:00 CET)
- Real started date: 11.01.2024
- Deadline: 14.01.2024 (14:00 CET, when I received an email)

## Prequistitions

- [X] Proficiency in Python programming.
- [X] Knowledge of Geospatial data handling, GIS, and Coordinate Reference Systems (CRS).
- [X] Experience with image processing libraries in Python, such as PIL or OpenCV.

## Task

### 🚀 Main Goal: 
Retrieve and return `latitude`, `longitude` and `image` from data.

### 📜 Goal's Technical Details/Restrictions/Challenges:

#### Input data
- Sample of [provided dataset](https://drive.usercontent.google.com/download?id=140PpLsdnVOQVIp5ia9jT_yvqtcWtF8Gj&export=download&confirm=t&uuid=483b1776-4e25-4976-9837-b498c823754a) was given. 
- One image has 1x1 km area.
- Real dataset could be much bigger than provided one.
- There is information, that one filename `...X_Y...` has latitude, longtitude range from `X/Y` till `X/Y+1000` and I need to extract It.
- `radius` param could be from `1` till `100` meters.

## Name Conventions in the Project.

Prefer `Projcted CRS` to `Geographic CRS`
- `Latitude`/`X`/ `Easting` are always come first in coordinates pair
- `Longitude`/`Y`/ `Northing` are always come second in coordinates pair 

In case of boxes there is next order convention (Latitude comes first, Longitude second here as well):
- Latitude Left (Min X), Longitude Bottom (Min Y), Latitude Right (Max X), Latitude Top (Max Y) (⬅️, ⬇️, ➡️, ⬆️)