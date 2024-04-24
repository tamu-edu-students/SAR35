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
from PIL import Image, ImageDraw, ImageFont, ImageTk

global results, run_ml, surv_count
results = []
run_ml = 0
surv_count = 0

def least_blurry(img_folder:str):
    '''
    Finds least blurry image in a folder and sends it to the image_processing folder.
    
    @param img_folder: Directory to folder with images to use. format = str(path)
    '''
    #print(colored("starting image blurriness test...", 'dark_grey'))
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
            #print(colored("total time for image blurriness "+str(end - start), 'dark_grey'))
            del_directory = os.path.dirname(most_clear_image_path)
            file_name = os.path.basename(del_directory)
            num = file_name.split("_")[-1]
            que_num = file_name.split("_")[0]
            os.rename(most_clear_image_path, os.path.join(HOME, "im_rec_folder", "im_process",str(que_num)+"_video_pic_"+str(num)+".jpg"))
            #print(colored("Directory to be removed: "+str(del_directory), "dark_grey"))
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
            results.append((model(source=image_file, conf=0.7, verbose=False), #, save_crop=True, project=os.path.join(HOME, "im_rec_folder"), name=str(que_num)+"_predict"
                            cone_model(source=image_file, conf=0.6, verbose=False), 
                            box_model(source=image_file,iou=0.3,conf=0.7, verbose=False), 
                            num, 
                            que_num)) #
            #move the used image to used
            shutil.move(image_file, os.path.join(os.getcwd(), "im_rec_folder", "used", image_name))
            #make survivor images
            #make_surv_img()
            #reset variables for detection
            lst1 = []
            lst2 = []
            human_detected1, obst_detected1 = 0, 0
            human_detected2, obst_detected2 = 0, 0
            #count number of detections found
            i = results[-1]
            for r in i[0]:
                r.save_crop(os.path.join(HOME, "im_rec_folder"), file_name=str(que_num)+"_predict")
                #detection count
                if (r.boxes.cls.numel() != 0):
                    for box in r.boxes:
                        if r.names[int(box.cls)] == "person":
                            if int(num) == 1:
                                human_detected1 += 1
                                #pathfinding bounding box
                                xywh_box = box.xywh  # Get the bounding boxes in XYWH format
                                xywh_box = xywh_box.tolist()
                                xywh_box = xywh_box[0]
                                #pf.obstacleDetection("human", (xywh_box[0], xywh_box[1]), (xywh_box[2] * xywh_box[3]), 1)
                            else:
                                human_detected2 += 1
                                #pathfinding bounding box
                                xywh_box2 = box.xywh  # Get the bounding boxes in XYWH format
                                xywh_box2 = xywh_box2.tolist()
                                xywh_box2 = xywh_box2[0]
                                #pf.obstacleDetection("human", (xywh_box2[0], xywh_box2[1]), (xywh_box2[2] * xywh_box2[3]), 2)
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
                if obst_detected1 == 0:
                    pf.pf_stop1 = 0
                if obst_detected2 == 0:
                    pf.pf_stop2 = 0
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

'''def make_surv_img():
    
    Takes an image and a bounding box for a detection and crops it to make a survivor image.

    @param image: Path to image that will be copyed and cropped to make the survivor image.
    @param tensor: List that includes information about the bounding box of the detected object. format = [x_center, y_center, width, height]
    
    global surv_count
    predict_im_list = [x for x in os.listdir(os.path.join(HOME, "im_rec_folder")) if x.__contains__("predict")]
    image_path_list = []
    que = ''
    predict = predict_im_list[0].split("_")[0]
    predict_count = 0
    for x in predict_im_list:
        predict_count += 1
        que = x.split("_")[0]
        if predict_count == 3: 
            predict = que
            predict_count = 0
        if predict == que:
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
    for x in predict_im_list:
        shutil.rmtree(os.path.join(HOME, "im_rec_folder", x))
    return'''
'''def create_surv_image():
        image_pil = Image.open(os.path.join(os.getcwd(),'images','blank_surv_img.jpg'))
        image_pil = image_pil.resize((290, 170))

        #add survivor picture from image recognition files
        pic_name = 'surv_pic2.jpg'
        try:
            surv_pic = Image.open(os.path.join(os.getcwd(),'im_rec_folder',pic_name)) #test sample for now
            surv_pic = surv_pic.resize((124, 170))
            offset = (0, 0)
            image_pil.paste(surv_pic, offset)

            im_draw = ImageDraw.Draw(image_pil) #make able to add text
            im_font = ImageFont.truetype("c:\Windows\Fonts\Bahnschrift.ttf", 12)

            #add text (sample for now)
            #self.create_image_text()
            im_draw.text((148,12), "???", font=im_font, fill="#2C2C2C") #age
            im_draw.text((162,44), "???", font=im_font, fill="#2C2C2C") #gender
            im_draw.text((173,75), "???", font=im_font, fill="#2C2C2C") #condition
            surv_img_name = "surv_img1.jpg"
            image_pil.save(os.path.join(os.getcwd(),"images",surv_img_name))
            
        except:
            print("ERROR: Image could not be made for 1")
            

create_surv_image()'''

'''def age_gen_lst(results):
    lst = []
    lst.append(age_gender_result)
    return lst'''

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


