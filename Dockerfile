FROM tensorflow/tensorflow
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y gdal-bin python-gdal python-pillow python-opencv python-geopandas python-psutil
CMD python2.7 /app/src/detectBuilding.py
