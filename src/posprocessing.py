import time
import os
import datetime
import gdal
import numpy as np
import geopandas as gp
from shapely.geometry import Point, Polygon

#Path to output folder.
PATH_TO_OUTPUT_GPKG = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), 
    '..',
    'output_gpkg'
)

#Path to temporary data folder.
PATH_TO_TMP = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), 
    'tmp'
)

class Posprocessing:
    """Set of functions that are performed after each prediction.

    """
    def __init__(self):
        """Constructor."""
        self.file_path = os.path.join(
            PATH_TO_OUTPUT_GPKG,
            "{0}.gpkg".format(
                datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d_%H%M%S')
            )
        )
        self.open_gpkg()

    def open_gpkg(self):
        """Create a DataFrame or open an existing gpkg to save results."""
        if os.path.exists(self.file_path):
            self.geometry_data = gp.read_file(self.file_path, layer='boxes')
        else:
            self.geometry_data = gp.GeoDataFrame()
            self.geometry_data['geometry'] = None

    def clean_tmp_dir(self):
        """Clean temporary folder."""
        for fn in os.listdir(PATH_TO_TMP):
            os.remove(
                os.path.join(PATH_TO_TMP,fn)
            )

    def set_image_config(self, image_path):
        """Defines height, width, and image source coordinates."""
        g = gdal.Open(image_path) 
        geoTransform = g.GetGeoTransform()
        self.dimension_x = g.RasterXSize
        self.dimension_y = g.RasterYSize
        minx = geoTransform[0]
        maxy = geoTransform[3]
        maxx = minx + geoTransform[1] * self.dimension_x
        miny = maxy + geoTransform[5] * self.dimension_y
        self.pixelWidth = abs(geoTransform[1])
        self.pixelHeight = abs(geoTransform[5])
        self.originx = minx
        self.originy = maxy

    def pixel2coord(self, originx, originy, box):
        """Converts the coordinates of the pixels to the georeferenced coordinates.

        Parameters
        ----------
        originx : float
            image source x coordinate.
        originy : float
           image source y coordinate.
        
        Returns
        -------
        coordinates : list of float 
            list of georeferenced coordinates.
        """
        ymin, xmin, ymax, xmax  = box
        p1 = [
            originx + (self.pixelWidth*xmin*300 + self.pixelWidth/2) , 
            originy - (self.pixelHeight*ymax*300 + self.pixelHeight/2) 
        ]
        p2 = [
            originx + (self.pixelWidth*xmin*300 + self.pixelWidth/2) , 
            originy - (self.pixelHeight*ymin*300 + self.pixelHeight/2) 
        ]
        p3 = [
            originx + (self.pixelWidth*xmax*300 + self.pixelWidth/2) , 
            originy - (self.pixelHeight*ymin*300 + self.pixelHeight/2) 
        ]
        p4 = [
            originx + (self.pixelWidth*xmax*300 + self.pixelWidth/2) , 
            originy - (self.pixelHeight*ymax*300 + self.pixelHeight/2) 
        ]
        coordinates =  [ p1, p2, p3, p4 ]
        for point in coordinates:
            if abs(point[0]) > self.dimension_x:
                point[0] = self.dimension_x if point[0] > 0 else -self.dimension_x
            if abs(point[1]) > self.dimension_y:
                point[1] = self.dimension_y if point[1] > 0 else -self.dimension_y
        return coordinates

    def get_xy_origin(self, name):
        """extracts the source coordinates of a name with a format containing the coordinates.

        Parameters
        ----------
        name : string
            name with the source coordinates.
        
        """
        x1 = int(name.split('.')[0].split('_')[0])
        y1 = int(name.split('.')[0].split('_')[2])
        originx = self.originx + x1*self.pixelWidth
        originy = self.originy - y1*self.pixelHeight
        return originx, originy

    def run(self, boxes, scores, batch_path):
        """Performs all pos-processing.

        Parameters
        ----------
        boxes : list
            list of the coordinates of the boxes.
        scores : list
            score list for each boxing.
        batch_path : list
            list with the paths of the batch images.
        
        """
        fid = len(self.geometry_data['geometry'])
        size_gpkg = fid
        count = len(scores)
        for i in range(count):
            for idx in range(scores[i].shape[0]):
                score = scores[i][idx] 
                if score > 0.74:
                    if count == 1:
                        originx = self.originx 
                        originy = self.originy
                    else:
                        name = batch_path[i].split('/')[-1]
                        originx, originy = self.get_xy_origin(name)
                    coordinates = self.pixel2coord(
                        originx, 
                        originy, 
                        tuple(boxes[i][idx].tolist())
                    )
                    poly = Polygon(coordinates)
                    self.geometry_data.loc[fid, 'geometry'] = poly
                    self.geometry_data.loc[fid, 'score'] = score
                    fid += 1
        if len(self.geometry_data['geometry']) > size_gpkg: 
            self.geometry_data.to_file(self.file_path, layer='boxes', driver="GPKG")

                    
        
