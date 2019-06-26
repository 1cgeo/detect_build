from PIL import Image
import os
import numpy as np

#Set limit max size image
Image.MAX_IMAGE_PIXELS = 933120000

#Set temporary folder path
PATH_TO_TMP = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), 
    'tmp'
)

class Preprocessing:
     """Set of functions that are performed before prediction."""

    def create_tiles(self, image_path, SIZE=(300, 300)):
        """Predict buildings in a batch of images.

        Parameters
        ----------
        image_path : string
            image path.
        SIZE : tuple
            default image size. default is (300, 300).
        """
        images_path = []
        img = Image.open(image_path)
        x, y = img.size
        if (x, y) == SIZE:
            images_path.append(image_path)
        else:
            for idx_x in range(0, x, SIZE[0]):
                for idx_y in range(0, y, SIZE[1]):
                    bbox=(idx_x, idx_y, min(idx_x+SIZE[0], x), min(idx_y+SIZE[1], y))
                    slice_bit=img.crop(bbox)
                    if SIZE != slice_bit.size:
                        xi, yi = slice_bit.size
                        cur = np.zeros((SIZE[0], SIZE[1], 3))
                        slice_bit = np.array(slice_bit)
                        cur[:yi, :xi, :] = slice_bit
                        slice_bit = Image.fromarray(cur.astype('uint8'))
                    img_path = os.path.join(
                        PATH_TO_TMP,
                        "{0}_{1}_{2}_{3}.tiff".format(
                            idx_x, 
                            min(idx_x+SIZE[0], x), 
                            idx_y, 
                            min(idx_y+SIZE[1], y)
                        )
                    ) 
                    slice_bit.save(img_path, plugin='gdal')
                    images_path.append(img_path)
        return images_path

    def run(self, image_path, ):
        """Performs all pre-processing."""
        return self.create_tiles(image_path)

    
                