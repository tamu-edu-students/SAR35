import cv2 
import numpy as np
#issues to think about
FACE_PROTO = r"C:\Users\hafsa\ecen_403\age_gender_detection\deploy.prototxt.txt"
FACE_MODEL = r"ecen_403\age_gender_detection\res10_300x300_ssd_iter_140000_fp16.caffemodel"

GENDER_PROTO = r"C:\Users\hafsa\ecen_403\age_gender_detection\gender_net.caffemodel"
GENDER_MODEL = r"ecen_403\age_gender_detection\deploy_gender.prototxt"

MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)
GENDER_LIST = ['Male', 'Female']

AGE_MODEL = r"C:\Users\hafsa\ecen_403\age_gender_detection\deploy_age.prototxt"
AGE_PROTO = r"C:\Users\hafsa\ecen_403\age_gender_detection\age_net.caffemodel"

AGE_INTERVALS = ['(0, 2)', '(4, 6)', '(8, 12)', '(15, 20)',
                 '(25, 32)', '(38, 43)', '(48, 53)', '(60, 100)']

frame_width = 1280
frame_height = 720
# load face Caffe model
face_net = cv2.dnn.readNetFromCaffe(FACE_PROTO, FACE_MODEL)
# Load age prediction model
age_net = cv2.dnn.readNetFromCaffe(AGE_MODEL, AGE_PROTO)
# Load gender prediction model
gender_net = cv2.dnn.readNetFromCaffe(GENDER_MODEL, GENDER_PROTO)
lst = []
def get_faces(frame, confidence_threshold=0.5):
    # convert the frame into a blob to be ready for NN input
    blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), (104, 177.0, 123.0))
    # set the image as input to the NN
    face_net.setInput(blob)
    # perform inference and get predictions
    output = np.squeeze(face_net.forward())
    # initialize the result list
    faces = []
    # Loop over the faces detected
    for i in range(output.shape[0]):
        confidence = output[i, 2]
        if confidence > confidence_threshold:
            box = output[i, 3:7] * \
                np.array([frame.shape[1], frame.shape[0],
                         frame.shape[1], frame.shape[0]])
            # convert to integers
            start_x, start_y, end_x, end_y = box.astype(int)
            # widen the box a little
            start_x, start_y, end_x, end_y = start_x - \
                10, start_y - 10, end_x + 10, end_y + 10
            start_x = 0 if start_x < 0 else start_x
            start_y = 0 if start_y < 0 else start_y
            end_x = 0 if end_x < 0 else end_x
            end_y = 0 if end_y < 0 else end_y
            # append to our list
            faces.append((start_x, start_y, end_x, end_y))
    return faces

def display_img(title, img):
    #helps to display the image
    cv2.imshow(title, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def image_resize(image, width = None, height = None, inter = cv2.INTER_AREA):
    dim = None
    (h, w) = image.shape[:2]
    # return image if no height or width
    if width is None and height is None:
        return image
    # check to see if the width is None
    if width is None:
        # calculate the ratio of the height and construct the
        # dimensions
        r = height / float(h)
        dim = (int(w * r), height)
    # otherwise, the height is None
    else:
        # calculate the ratio of the width and construct the
        # dimensions
        r = width / float(w)
        dim = (width, int(h * r))
    # resize the image
    return cv2.resize(image, dim, interpolation = inter)

def get_gender_predictions(face_img):
    #image preprocessing & analysis
    blob = cv2.dnn.blobFromImage(
        image=face_img, scalefactor=1.0, size=(227, 227),
        mean=MODEL_MEAN_VALUES, swapRB=False, crop=False
    )
    gender_net.setInput(blob)
    return gender_net.forward()


def get_age_predictions(face_img):
    #image prepocessing & analysis
    blob = cv2.dnn.blobFromImage(
        image=face_img, scalefactor=1.0, size=(227, 227),
        mean=MODEL_MEAN_VALUES, swapRB=False
    )
    age_net.setInput(blob)
    return age_net.forward()

def predict_age_and_gender(input_path: str):
    # Initialize frame size (to look into)
    # frame_width = 1280
    # frame_height = 720

    img = cv2.imread(input_path)
    # possible resizing - not necessary at the moment
    # img = cv2.resize(img, (frame_width, frame_height))
    # copy of initial image and resize
    frame = img.copy()
    if frame.shape[1] > frame_width:
        frame = image_resize(frame, width=frame_width)
    # predict the faces
    faces = get_faces(frame)
    # Loop over the faces detected
    for i, (start_x, start_y, end_x, end_y) in enumerate(faces):
        face_img = frame[start_y: end_y, start_x: end_x]
        age_preds = get_age_predictions(face_img)
        gender_preds = get_gender_predictions(face_img)
        i = gender_preds[0].argmax()
        gender = GENDER_LIST[i]
        gender_confidence_score = gender_preds[0][i]
        i = age_preds[0].argmax()
        age = AGE_INTERVALS[i]
        age_confidence_score = age_preds[0][i]
        # Draw the box
        label = f"{gender}-{gender_confidence_score*100:.1f}%, {age}-{age_confidence_score*100:.1f}%"
        lst.append(label)
        print(label)
        yPos = start_y - 15
        while yPos < 15:
            yPos += 15
        box_color = (0,0,0) if gender == "Male" else (0,0,0)
        cv2.rectangle(frame, (start_x, start_y), (end_x, end_y), box_color, 2)
        # Label processed image
        font_scale = 0.54
        cv2.putText(frame, label, (start_x, yPos),
                    cv2.FONT_HERSHEY_SIMPLEX, font_scale, box_color, 2)

        # Display processed image
    display_img("Gender Estimator", frame)
    cv2.imwrite("output.jpg", frame)
    cv2.destroyAllWindows()    
# predict_age_and_gender(r"C:\Users\hafsa\OneDrive\Pictures\Screenshots\Screenshot 2023-11-14 113851.png")
# predict_age_and_gender(r"C:\Users\hafsa\OneDrive\Pictures\Screenshots\Screenshot 2023-11-14 114230.png")
# predict_age_and_gender(r"C:\Users\hafsa\OneDrive\Pictures\Screenshots\Screenshot 2023-11-14 114332.png")
# predict_age_and_gender(r"C:\Users\hafsa\OneDrive\Pictures\Screenshots\Screenshot 2023-11-14 120025.png")
# predict_age_and_gender(r"C:\Users\hafsa\Downloads\blurry-human.jpg")
# predict_age_and_gender(r"C:\Users\hafsa\OneDrive\Pictures\Screenshots\Screenshot 2023-11-14 121004.png")
# predict_age_and_gender(r"C:\Users\hafsa\OneDrive\Pictures\Screenshots\Screenshot 2023-11-14 121155.png")

#put this into a csv.- list will function as that right now 
print(lst)


