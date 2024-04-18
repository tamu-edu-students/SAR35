# from ultralytics import YOLO
# from ultralytics.utils import ASSETS
import os
HOME = os.getcwd()
from ultralytics import YOLO
from threading import Thread
#from image_recognition.age_gender_detection.age_gender_detection.age_gender_class_2 import *
#show=True is enabled for age/gender/human/cone/box detection
import cv2, time, csv, shutil
import pathfinding.pathfinding as pf
from termcolor import colored
from PIL import Image

global results, run_ml, surv_count
results = []
run_ml = 0
surv_count = 0

def least_blurry(img_folder:str):
    '''
    Finds least blurry image in a folder and sends it to the image_processing folder.
    
    @param img_folder: Directory to folder with images to use. format = str(path)
    '''
    print(colored("starting image blurriness test...", 'dark_grey'))
    start = time.time()
    list_ = []
    path_list = []
    image_files = []
    if os.path.isdir(img_folder):
        file_list = os.listdir(img_folder)
        for i in file_list:
            image_files.append(os.path.join(img_folder, i))
        most_clear_image = 0
        most_clear_image_path = ''
        if len(image_files) >= 1:
            for img_path in image_files:
                img = cv2.imread(img_path)
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) #image converted to grayscale to allow for same scale
                blur = cv2.Laplacian(gray, cv2.CV_64F).var() #variation of laplace helps to see which one has max clairty
                list_.append(blur)
                most_clear_image = max(list_)
                path_list.append((img_path, blur))
            for i in path_list:
                if most_clear_image == i[1]:
                    most_clear_image_path = i[0]
            end=time.time()
            print(colored("total time for image blurriness "+str(end - start), 'dark_grey'))
            del_directory = os.path.dirname(most_clear_image_path)
            file_name = os.path.basename(del_directory)
            num = file_name.split("_")[-1]
            que_num = file_name.split("_")[0]
            os.rename(most_clear_image_path, os.path.join(HOME, "im_rec_folder", "im_process",str(que_num)+"_video_pic_"+str(num)+".jpg"))
            print(colored("Directory to be removed: "+str(del_directory), "dark_grey"))
            shutil.rmtree(del_directory)
        else: print("empty file folder")
    return

def ml_running():
    global results, run_ml, surv_count
    model = YOLO('yolov8n.pt')
    cone_model = YOLO(os.path.join(os.getcwd(), "image_recognition", "runs_100", "best.pt"))
    box_model = YOLO(os.path.join(os.getcwd(), "image_recognition", "runs_box_new", "best.pt"))
    folder_path = os.path.join(os.getcwd(), "im_rec_folder", "im_process")
    image_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path)]
    while (run_ml or (len(os.listdir(folder_path)) > 0)):
        image_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path)]
        for image_file in image_files:
            #get image base name
            image_name = os.path.basename(image_file)
            #get rover number from base name
            num = image_name.split("_")[-1]
            num = num.split(".")[0]
            que_num = image_name.split("_")[0]
            #add results to list
            results.append((model(source=image_file, save_crop=True, project=os.path.join(HOME, "im_rec_folder"), conf=0.7), cone_model(source=image_file, conf=0.7), box_model(source=image_file,iou=0.3,conf=0.7), num, que_num)) #, cone_model(image_file), box_model(source=image_file,iou=0.3,conf=0.7)
            #move the used image to used
            shutil.move(image_file, os.path.join(os.getcwd(), "im_rec_folder", "used", image_name))
            #make survivor images
            make_surv_img()
            #reset variables for detection
            lst1 = []
            lst2 = []
            human_detected1, obst_detected1 = 0, 0
            human_detected2, obst_detected2 = 0, 0
            #count number of detections found
            i = results[-1]
            for r in i[0]:
                #detection count
                if (r.boxes.cls.numel() != 0):
                    for box in r.boxes:
                        if r.names[int(box.cls)] == "person":
                            if int(num) == 1:
                                human_detected1 += 1
                            else:
                                human_detected2 += 1
                #pathfinding bounding box
                xywh_boxes = r.boxes.xywh  # Get the bounding boxes in XYWH format
                for box in xywh_boxes:
                    #'box' is a tensor containing [x_center, y_center, width, height]
                    #convert it to a list
                    box = box.tolist()
                    if int(num) == 1: pf.obstacleDetection("human", (box[0], box[1]), (box[2] * box[3]), 1)
                    else: pf.obstacleDetection("human", (box[0], box[1]), (box[2] * box[3]), 2)
            for r_c in i[1]: #add CONE_DETECTED = True somewhere
                if (r_c.boxes.cls.numel() != 0):
                    if int(num) == 1:
                        obst_detected1 += r_c.boxes.cls.numel()
                    else: obst_detected2 += r_c.boxes.cls.numel()
                #pathfinding bounding box
                xywh_boxes = r_c.boxes.xywh  # Get the bounding boxes in XYWH format
                for box in xywh_boxes:
                    # 'box' is a tensor containing [x_center, y_center, width, height]
                    if int(num) == 1: pf.obstacleDetection("Cone", (box[0], box[1]), (box[2] * box[3]), 1)
                    else: pf.obstacleDetection("Cone", (box[0], box[1]), (box[2] * box[3]), 2)
            for r_b in i[2]: #add BOX_DETECTED = True somewhere
                if (r_b.boxes.cls.numel() != 0):
                    if int(num) == 1:
                        obst_detected1 += r_b.boxes.cls.numel()
                    else: obst_detected2 += r_b.boxes.cls.numel()
                #pathfinding bounding box
                xywh_boxes = r_b.boxes.xywh  # Get the bounding boxes in XYWH format
                for box in xywh_boxes:
                    # 'box' is a tensor containing [x_center, y_center, width, height]
                    if int(num) == 1: pf.obstacleDetection("Box", (box[0], box[1]), (box[2] * box[3]), 1)
                    else: pf.obstacleDetection("Box", (box[0], box[1]), (box[2] * box[3]), 2)
            #add number of each detection to respective lists
            lst1.append(human_detected1)
            lst1.append(obst_detected1)
            lst2.append(human_detected2)
            lst2.append(obst_detected2)
            #write the values to csv files
            with open(os.path.join(os.getcwd(), "im_rec_folder", "results_folder", str(que_num)+"_results_"+str(num)+".csv"), 'w', newline='') as file:
                write_file = csv.writer(file)
                if int(num) == 1:
                    write_file.writerow(lst1)
                else:
                    write_file.writerow(lst2)

def make_surv_img():
    '''
    Takes an image and a bounding box for a detection and crops it to make a survivor image.

    @param image: Path to image that will be copyed and cropped to make the survivor image.
    @param tensor: List that includes information about the bounding box of the detected object. format = [x_center, y_center, width, height]
    '''
    global surv_count
    predict_fold_list = [x for x in os.listdir(os.path.join(HOME, "im_rec_folder")) if x.__contains__("predict")]
    for x in predict_fold_list:
        x = os.path.join(HOME, "im_rec_folder", x)
    image_path_list = []
    for x in predict_fold_list:
        if os.path.exists(os.path.join(HOME, "im_rec_folder", x, "crops", "person")):
            dir_list = os.listdir(os.path.join(HOME, "im_rec_folder", x, "crops", "person"))
            for i in dir_list:
                image_path_list.append(os.path.join(HOME, "im_rec_folder", x, "crops", "person", i))
    for image in image_path_list:
        #open image
        im = Image.open(image)
        #set new name and save
        surv_count += 1
        pic_name = 'surv_pic'+str(surv_count)+'.jpg'
        im.save(os.path.join(os.getcwd(),'im_rec_folder',pic_name))
    for x in predict_fold_list:
        shutil.rmtree(os.path.join(HOME, "im_rec_folder", x))
    return

'''def age_gen_lst(results):
    lst = []
    lst.append(age_gender_result)
    return lst'''

current_coord = []
with open(os.path.join(os.getcwd(), "gps_folder", "1_gps_coords_1", "gps_coords_1.csv"), 'r') as file:
    read_file = csv.reader(file, delimiter=",")
    for i in read_file:
        current_coord = [float(i[0]), float(i[1])]
print(current_coord)

'''path_list = [os.path.join(os.getcwd(), "im_rec_folder", "1_images_1", "video_pic_1_1.jpg"), 
             os.path.join(os.getcwd(), "im_rec_folder", "1_images_1", "video_pic_1_2.jpg"), 
             os.path.join(os.getcwd(), "im_rec_folder", "1_images_1", "video_pic_1_3.jpg"), 
             os.path.join(os.getcwd(), "im_rec_folder", "1_images_1", "video_pic_1_4.jpg"), 
             os.path.join(os.getcwd(), "im_rec_folder", "1_images_1", "video_pic_1_5.jpg")]

img = least_blurry(path_list)
#x = ml_running(img)'''
'''run_ml = 1
ml_thread = Thread(target=ml_running)
ml_thread.start()
time.sleep(3)
start = time.time()

run_ml = 0
while len(os.listdir(os.path.join(HOME, "im_rec_folder", "used"))) < 11:
    continue
end = time.time()
print("time elapsed:", (end - start))'''

'''if x[0] > 0: # if there is a human detected, then predict age and gender
    #age_gender_result = predict_age_and_gender(img)
    #age_gen_lst(age_gender_result)'''


