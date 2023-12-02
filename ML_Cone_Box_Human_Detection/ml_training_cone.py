import os
HOME = os.getcwd()
import csv
print(HOME)
from ultralytics import YOLO
from IPython.display import display, Image
from roboflow import Roboflow
import sys
from image_blurriness import *
from age_gender_class_2 import *
#box: predict47 and predict53 and predict80
#cone: predict37 and predict73 and predict79
#models previously trained for cones and boxes with the use of roboflow
#human: predict60
img = least_blurry(r"C:\Users\hafsa\ecen_403\demo_day\pics\pics\test0.jpg", r"C:\Users\hafsa\ecen_403\demo_day\pics\pics\test1.jpg", r"C:\Users\hafsa\ecen_403\demo_day\pics\pics\test2.jpg", r"C:\Users\hafsa\ecen_403\demo_day\pics\pics\test3.jpg", r"C:\Users\hafsa\ecen_403\demo_day\pics\pics\test4.jpg")
predict_age_and_gender(img)
model = YOLO(f'{HOME}/yolov8n.pt')
model_cone =YOLO(f'{HOME}/ecen_403/runs_100/content/runs/detect/train/weights/best.pt')
model_box = YOLO(f'{HOME}/ecen_403/runs_box_detection/content/runs/detect/train/weights/best.pt')
#confidence levels to be adjusted as seen necessary
results1 = model.predict(source=img,conf=0.7,save=True)
results2 = model_cone.predict(source=img,conf=0.4,save=True)
results3 = model_box.predict(source=img,conf=0.4,save=True)
