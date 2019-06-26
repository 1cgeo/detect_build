FROM tensorflow/tensorflow
RUN apt-get update && apt-get install -y gdal-bin python-gdal python-pillow python-opencv python-geopandas python-psutil
CMD python2.7 /app/src/detectBuilding.py
#docker run -v $PWD:/app -it teste/app2
