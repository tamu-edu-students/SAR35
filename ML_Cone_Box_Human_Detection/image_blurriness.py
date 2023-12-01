import cv2
from imutils import paths
import argparse

# def calculate_blurriness(image_path):
#     image = cv2.imread(image_path)
#     if image is None:
#         raise ValueError("image cannot be read.")

#     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#     return cv2.Laplacian(gray, cv2.CV_64F).var()

# image_path = r"C:\Users\hafsa\OneDrive\Pictures\Screenshots\Screenshot 2023-10-31 104730.png"
# blurriness = calculate_blurriness(image_path)

import cv2

def least_blurry(*img_paths):
    max_clarity = float('-inf')
    most_clear_image_path = None

    for img_path in img_paths:
        img = cv2.imread(img_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) #image converted to grayscale to allow for same scale
        blur = cv2.Laplacian(gray, cv2.CV_64F).var() #variation of laplace helps to see which one has max clairty

        if blur > max_clarity:
            max_clarity = blur
            most_clear_image_path = img_path

    return most_clear_image_path


    



#least_blurry(img_path1=r"C:\Users\hafsa\Downloads\Image_20231114_155140_352.jpeg", img_path2 = r"C:\Users\hafsa\Downloads\Image_20231114_155140_498.jpeg", img_path3=r"C:\Users\hafsa\Downloads\Image_20231114_155140_659.jpeg", img_path4=r"C:\Users\hafsa\Downloads\Image_20231114_155140_791.jpeg", img_path5=r"C:\Users\hafsa\Downloads\Image_20231114_155140_939.jpeg")
