import cv2
import math
import tqdm
import torch

from mtcnn import MTCNN
from facelib import AgeGenderEstimator

# INITIALIZE MODELS
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)
age_gender_detector = AgeGenderEstimator()
MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)
padding = 20


def highlightFace(face_cascade, frame):
    # This is done through the legacy harcascade models
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    facedata = face_cascade.detectMultiScale(gray, 1.1, 4)
    faceBoxes = []
    for face in facedata:
        x1, y1, width, height = face
        x2 = x1 + width
        y2 = y1 + height
        faceBoxes.append([x1, y1, x2, y2])
    return faceBoxes


def get_tags_for_one_image(image_file):
    # read image
    frame = cv2.imread(image_file)
    faceBoxes = highlightFace(face_cascade, frame)
    if faceBoxes == []:
        return "No face in this image"
    gender_tags = []
    for faceBox in faceBoxes:
        face = frame[
            max(0, faceBox[1] - padding) : min(
                faceBox[3] + padding, frame.shape[0] - 1
            ),
            max(0, faceBox[0] - padding) : min(
                faceBox[2] + padding, frame.shape[1] - 1
            ),
        ]

        blob = cv2.dnn.blobFromImage(
            face, 1.0, (112, 112), MODEL_MEAN_VALUES, swapRB=False
        )
        blob_facelib = blob.transpose(0, 2, 3, 1)
        genders, ages = age_gender_detector.detect(torch.Tensor(blob_facelib))
        gender_tags += genders

    if "Male" in gender_tags and "Female" in gender_tags:
        val = "Contains both female and male"
    # elif "Hard" in gender_age["Gender"]:
    #    val =  "Hard to identify the gender"
    elif "Male" in gender_tags:
        val = "Male"
    elif "Female" in gender_tags:
        val = "Female"
    return val


if __name__ == "__main__":
    import sys

    image_files = sys.argv[1:]
    for image_file in tqdm.tqdm(image_files):
        print(image_file.split("/")[-1] + "," + get_tags_for_one_image(image_file))
