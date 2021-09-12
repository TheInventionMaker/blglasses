# python3
#
# Copyright 2019 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Example using TF Lite to classify objects with the Raspberry Pi camera."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import pyttsx3
import argparse
import io
import time
import numpy as np
import picamera

from PIL import Image
from tflite_runtime.interpreter import Interpreter
import cv2
import multiprocessing
import time
import VL53L1X
import time
import numpy
#!/usr/bin/python
import asyncio
import TCA9548A
import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.OUT)
GPIO.setup(22, GPIO.OUT)
# set specific multiplexer to a specific channel
# TCA9548A.I2C_setup( multiplexer_addr , multiplexer_channel )
TCA9548A.I2C_setup(0x70,0)
tof = VL53L1X.VL53L1X(i2c_bus=1, i2c_address=0x29)
tof.open()
tof.set_timing(66000, 70)
tof.start_ranging(3)  # Start ranging
distance_in_mm = tof.get_distance()

TCA9548A.I2C_setup(0x70,1)
tof2 = VL53L1X.VL53L1X(i2c_bus=1, i2c_address=0x29)
tof2.open()
tof2.set_timing(66000, 70)
tof2.start_ranging(3)  # Start ranging
distance_in_mm = tof2.get_distance()
TCA9548A.I2C_setup(0x70,2)
tof3 = VL53L1X.VL53L1X(i2c_bus=1, i2c_address=0x29)
tof3.open()
tof3.set_timing(66000, 70)
tof3.start_ranging(3)  # Start ranging
tof3.get_distance()

engine = pyttsx3.init() # object creation
rate = engine.getProperty('rate')   # getting details of current speaking rate
engine.setProperty('rate',170)
engine.setProperty('volume',1.0)

def load_labels(path):
  with open(path, 'r') as f:
    return {i: line.strip() for i, line in enumerate(f.readlines())}


def set_input_tensor(interpreter, image):
  tensor_index = interpreter.get_input_details()[0]['index']
  input_tensor = interpreter.tensor(tensor_index)()[0]
  input_tensor[:, :] = image


def classify_image(interpreter, image, top_k=1):
  """Returns a sorted array of classification results."""
  set_input_tensor(interpreter, image)
  interpreter.invoke()
  output_details = interpreter.get_output_details()[0]
  output = np.squeeze(interpreter.get_tensor(output_details['index']))

  # If the model is quantized (uint8 data), then dequantize the results
  if output_details['dtype'] == np.uint8:
    scale, zero_point = output_details['quantization']
    output = scale * (output - zero_point)

  ordered = np.argpartition(-output, top_k)
  return [(i, output[i]) for i in ordered[:top_k]]

def detect_edges(frame, dir):
    # filter for blue lane lines
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(hsv, cv2.COLOR_BGR2GRAY)
    #show_image("hsv", hsv)
    ret, thresh = cv2.threshold(gray,100,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
    lower_blue = np.array([0, 0, 40])
    upper_blue = np.array([150, 255, 255])
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    #show_image("blue mask", mask)

    # detect edges
    #edges = cv2.Canny(mask, 200, 400)
    adjW = int(thresh.shape[0] * 0.2)
    cropped_image = thresh[adjW:thresh.shape[0], 0:thresh.shape[1]]
    
    height = cropped_image.shape[0]
    width = cropped_image.shape[1]
    # Cut the image in half
    width_cutoff = width // 2
    left = cropped_image[:, :width_cutoff]
    right = cropped_image[:, width_cutoff:]
    leftPx = cv2.countNonZero(left) / 1000
    rightPx = cv2.countNonZero(right) / 1000
    
    mid = 0
    if leftPx > rightPx:
      mid = leftPx * 0.2
      if leftPx - mid > rightPx:
        print("Left", rightPx / (leftPx - mid) * 100)
        if dir:
          return "left"
      else:
        print("Straight")
        if dir:
          return "straight"
    else:
      mid = rightPx * 0.2
      if rightPx - mid > leftPx:
        print("Right", leftPx / (rightPx - mid) * 100)
        if dir:
          return "right"
      else:
        print("Straight")
        if dir:
          return "straight"
    
    
    return cropped_image
from PIL import Image
from matplotlib import cm
def main():
  global tof, tof2, tof3
  parser = argparse.ArgumentParser(
      formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument(
      '--model', help='File path of .tflite file.', required=True)
  parser.add_argument(
      '--labels', help='File path of labels file.', required=True)
  args = parser.parse_args()

  labels = load_labels(args.labels)

  interpreter = Interpreter(args.model)
  interpreter.allocate_tensors()
  _, height, width, _ = interpreter.get_input_details()[0]['shape']

  with picamera.PiCamera(resolution=(640, 480), framerate=30) as camera:
    camera.start_preview()
    try:
      stream = io.BytesIO()
      for _ in camera.capture_continuous(
          stream, format='jpeg', use_video_port=True):
        stream.seek(0)
        
        image = Image.open(stream).convert('RGB').resize((width, height),
                                                         Image.ANTIALIAS)
        image2 = detect_edges(numpy.array(image), False)
        image2 = Image.fromarray(np.uint8(cm.gist_earth(image2)*255))
        image2 = image2.convert('RGB').resize((width, height), Image.ANTIALIAS)
        start_time = time.time()
        results = classify_image(interpreter, image2)
        elapsed_ms = (time.time() - start_time) * 1000
        label_id, prob = results[0]
        #print(labels[label_id],prob,elapsed_ms)
        if detect_edges(numpy.array(image), True) == "right":
          GPIO.output(27, GPIO.HIGH)
        else:
          GPIO.output(27, GPIO.LOW)
        if detect_edges(numpy.array(image), True) == "left":
          GPIO.output(22, GPIO.HIGH)
        else:
          GPIO.output(22, GPIO.LOW)
        if prob > 0.75:
          TCA9548A.I2C_setup(0x70, 0)
          
          if label_id != 0 and label_id != 1:
            engine.say(labels[label_id][2:])
            print(labels[label_id][2:])
            engine.runAndWait()
            
        stream.seek(0)
        stream.truncate()
        camera.annotate_text = '%s %.2f\n%.1fms' % (labels[label_id], prob,
                                                    elapsed_ms)
    finally:
      camera.stop_preview()


if __name__ == '__main__':
  main()
