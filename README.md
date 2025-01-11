# Geospatial Data Processing
A comprehensive repository featuring code for preprocessing orthophotos based on geospatial queries, including stitching, resizing, and performance optimization.

## General information
- Official started date: 10.01.2024
- Real started date: 11.01.2024
- Deadline: 13.01.2024

## My current TODO list:
- [ ] Read carefully task defintion (2 times or more to verify that this is exactly what company asks!) and write for yourself task definition.
    - [ ] Verify that you don't need to read image to provide `Latitude` and `Longitude`.
    - [ ] Check the ways of potential optimization of input images. Can I do preprocessing or it's not possible?
    - [ ] Find the way how to use the promt with constant `radious`.
- [ ] Understand data first.
- [ ] Learn more about Geospatial data handling, GIS, and Coordinate Reference Systems (CRS).
- [ ] Write dumb pipeline (_time_ is more important than _optimization_).
- [ ] Document the process.
- [ ] Write draft slides.
- [ ] Submit, If there is no time remain.
- [ ] Optimize the process.
- [ ] Update Documentation.
- [ ] Submit.

## Prequistitions

- [X] Proficiency in Python programming.
- [] Knowledge of Geospatial data handling, GIS, and Coordinate Reference Systems (CRS).
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

##### 👀 Observation №1
> ⚠️ It was mentioned that the dataset's size could be even bigger, so candidate (I) should consider the case that whole data can't fit in memory.  **Restriction №1**: Don't put whole dataset into memory use iterator, batch, micro-batch processing whatever.

##### 👀 Observation №2
> `Latitude` and `Longitude` are written in filename already - so for that you don't even need to read image for that. (#TODO @Karim: you need to check this assumption) 

##### 👀 Observation №3
>  _Imagine that the images were being retrieved over network on the fly. We encourage you to come up with ways to preprocess the data to optimize the retrieval process._ So they ask you to think about the way to optimize incomming images (maybe it's not needed, but I need to check).

##### 👀 Observation №4
>  _Consider that while the radius parameter remains generally fixed, the latitude and longitude parameters will vary randomly across requests._ For I don't understand their promt about constant `radious`. For now (11.01.2024) I don't have any idea how to use it in optimization...

#### ❗️ Challenge that I need to solve (it's not optional)
- Users will type `latitude` and `longitude` and `radious`. One image has `1x1 km` area. It's possible, that user set almost the edge of one image. In that case, I need to retrieve nearest required images (in worst case scenario additional `3` images), that covers radious and return final 256x256 image.
- Handle all posssible errors.

#### ❗️ Challenge that I need to solve (optional)
- Optimize time execution of `get_image(lat, long, radius)` function with any possible way. 