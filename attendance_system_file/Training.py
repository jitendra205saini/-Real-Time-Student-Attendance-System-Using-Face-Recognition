import cv2
import numpy as np
from os import listdir
from os.path import isfile, join, isdir

data_path = 'D:/face-attendance-system-gui/data/'

Training_Data = []
Labels = []
label_dict = {}
label_count = 0

for person_folder in listdir(data_path):
    person_folder_path = join(data_path, person_folder)

    if not isdir(person_folder_path):
        continue

    for file in listdir(person_folder_path):
        image_path = join(person_folder_path, file)
        images = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

        if images is None:
            print(f"Error loading image {image_path}. Skipping this file.")
            continue

        Training_Data.append(np.asarray(images, dtype=np.uint8))

        if person_folder not in label_dict:
            label_dict[person_folder] = label_count
            label_count += 1

        Labels.append(label_dict[person_folder])

print(f"Number of training images: {len(Training_Data)}")
# print(f"Labels: {Labels}")

if len(Training_Data) > 1:
    Labels = np.asarray(Labels, dtype=np.int32)

    try:
        if hasattr(cv2, 'face') and hasattr(cv2.face, 'LBPHFaceRecognizer_create'):
            model = cv2.face.LBPHFaceRecognizer_create()
            model.train(np.asarray(Training_Data), np.asarray(Labels))
            print("Dataset Model Training Completed")

            model.save('D:/face-attendance-system-gui/model/face_trained_model.yml')
            print("Model saved successfully.")
        else:
            raise AttributeError("Face recognition module not available. Make sure opencv-contrib-python is installed.")

    except cv2.error as e:
        print("OpenCV error: ", e)
    except AttributeError as e:
        print("Error: ", e)

else:
    print("Not enough training data to train the model.")
