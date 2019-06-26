import os
import cv2
from preprocessing import Preprocessing
from posprocessing import Posprocessing
import numpy as np
import tensorflow as tf
from psutil import virtual_memory

#Path to input.
PATH_TO_INPUT_IMAGES = os.path.join(
os.path.abspath(os.path.dirname(__file__)), 
    '..',
    'input_images'
)
#Path to output.
PATH_TO_CKPT = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), 
    'model',
    'frozen_inference_graph.pb'
)

class DetectBuilding:
    """Locates buildings in images using a trained deep learning faster r-cnn model

     Examples
    --------
    1 - put your set of images in the folder "input_images".
    2 - run the following command :
        $ python detectBuilding.py
    3 - when finished the process check the result in the folder "output_gpkg"
    """
    def __init__(self):
        """Constructor."""
        self.load_model()
        self.preprocessing = Preprocessing()
        self.posprocessing = Posprocessing()

    def load_model(self):
        """Load trained model."""
        detection_graph = tf.Graph()
        with detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')
            self.sess = tf.Session(graph=detection_graph)
        self.image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
        self.detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
        self.detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
        self.detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')
        self.num_detections = detection_graph.get_tensor_by_name('num_detections:0')

    def predict(self, images):
        """Predict buildings in a batch of images.

        Parameters
        ----------
        images : list of images
            set of images for location.
        Returns
        -------
        boxes : list of boxes  
            boxes found in prediction.
        scores : list of scores
            scores probability scores of each box to be a building.
        """
        image_expanded = np.array(images)
        (boxes, scores, classes, num) = self.sess.run(
            [
                self.detection_boxes, 
                self.detection_scores, 
                self.detection_classes, 
                self.num_detections
            ],
            feed_dict={self.image_tensor: image_expanded}
        )
        return boxes, scores
    
    def load_images(self, images_path):
        """Loads the batch of images.

        Parameters
        ----------
        images_path : list of str
            list with the paths of images.
        Returns
        -------
        batch_images : list of images 
            set of images for location.
        """
        batch_images = [cv2.imread(ip) for ip in images_path]
        return batch_images

    def get_batch_size(self):
        mem_total = virtual_memory().total/(1024*1024*1024)
        return (mem_total*28)/15

    def run(self):
        """Performs the entire localization process."""
        for img_name in os.listdir(PATH_TO_INPUT_IMAGES):
            batch_size = self.get_batch_size()
            img_path = os.path.join(PATH_TO_INPUT_IMAGES, img_name)
            images_path = self.preprocessing.run(img_path)
            self.posprocessing.set_image_config(img_path)
            for i in range(0, len(images_path), batch_size):
                batch_path = images_path[i:min(len(images_path), i+batch_size)]
                batch_images = self.load_images(
                    batch_path
                )
                boxes, scores = self.predict(batch_images)
                self.posprocessing.run(boxes, scores, batch_path)
                boxes = [] 
                scores = [] 
                batch_images = []
            self.posprocessing.clean_tmp_dir()
                        
if __name__ == '__main__':
    detectBuilding = DetectBuilding()
    detectBuilding.run()
