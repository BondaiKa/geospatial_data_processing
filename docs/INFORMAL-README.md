## My current TODO list:
- [X] Read carefully task defintion (2 times or more to verify that this is exactly what company asks!) and write for yourself task definition.
    - [X] Verify that you don't need to read image to provide `Latitude` and `Longitude`.
    - [X] Find the way how to use the promt with constant `radious`.
- [X] Understand data first (at least read it and look with you own eyes!).
- [ ] Learn more about Geospatial data handling, GIS, and Coordinate Reference Systems (CRS).
- [ ] Write `dumb` pipeline (_time_ is more important than _optimization_) for now.
- [ ] Document the process.
- [ ] Write draft slides.
- [ ] Submit, If there is no time remain.
- [ ] Optimize the process.
    - [X] Check the ways of potential optimization of input images. Can I do preprocessing or it's not possible?
- [ ] Update Documentation.
- [ ] Submit.

## My Developing Journal


Once I read requirements, I have next thoughts in my mind:
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

After that I started to create my first version of the process. So I used `python`, `poetry`, and `.pre-commit` (i couldn't resist and spent time to install it. I am really lazy to fix code style for myself 😅) with `mypy`, `black`, `flake8`, `isort`. After that my main goal was to look on image ASAP. I need to have a look on data at least once, that's why I used `rasterio` and `matplotlib`