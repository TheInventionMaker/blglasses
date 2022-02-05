import numpy as np
import os

from tflite_model_maker.config import ExportFormat
from tflite_model_maker import model_spec
from tflite_model_maker import object_detector

import tensorflow as tf
assert tf.__version__.startswith('2')

tf.get_logger().setLevel('ERROR')
from absl import logging
logging.set_verbosity(logging.ERROR)

spec = model_spec.get('efficientdet_lite2')

train_data = object_detector.DataLoader.from_pascal_voc("/Users/jamesnagler/Downloads/TestCustomGlassesModel/train", "/Users/jamesnagler/Downloads/TestCustomGlassesModel/train", label_map={
1: "person",
2: "door",
3: "dresser",
4: "bed",
5: "obstacle",
6: "chair",
7: "desk",
8: "table",
9: "couch",
10: "fridge",
11: "cabinets",
12: "dishwasher",
13: "sink",
14: "oven",
15: "computer",
16: "staircase",
17: "tv",
18: "garbage"
})
#Do 5fps for the rest
valid_data = object_detector.DataLoader.from_pascal_voc("/Users/jamesnagler/Downloads/TestCustomGlassesModel/valid", "/Users/jamesnagler/Downloads/TestCustomGlassesModel/valid", label_map={
1: "person",
2: "door",
3: "dresser",
4: "bed",
5: "obstacle",
6: "chair",
7: "desk",
8: "table",
9: "couch",
10: "fridge",
11: "cabinets",
12: "dishwasher",
13: "sink",
14: "oven",
15: "computer",
16: "staircase",
17: "tv",
18: "garbage"
})
model = object_detector.create(train_data, model_spec=spec, epochs=100, batch_size=8, train_whole_model=True, validation_data=valid_data)
model.export(export_dir='/Users/jamesnagler/Downloads/TestCustomGlassesModel/results')
