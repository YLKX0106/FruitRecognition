import tensorflow as tf
import os
import cv2
from PIL import Image
import numpy as np
import re

model = tf.keras.models.load_model("models/mobilenet_fv_0611.h5")

def predict_img(path):
    class_names = ['Apple', 'Banana', 'Kiwi', 'Mango', 'Orange', 'Peach', 'Pear']
    img_init = cv2.imread(path)  
    h, w, c = img_init.shape
    scale = 400 / h
    img_init = cv2.resize(img_init, (224, 224))  
    cv2.imwrite('images/target.png', img_init)
    img = Image.open('images/target.png')  
    img = np.asarray(img)  
    outputs = model.predict(img.reshape(1, 224, 224, 3))  
    result_index = int(np.argmax(outputs))
    resultin = outputs[0][result_index]  
    resultin = "%.2f%%" % (resultin * 100)
    result=f'结果：{class_names[result_index]}，识别率：{resultin}'
    return result

if __name__ == '__main__':

    path=r"data/Test"
    images=os.listdir(path)
    for image in images:
        res1 = predict_img(os.path.join(path, image))
        a = re.search(r'([a-zA-Z]+)\d+?\..+', image).group(1)
        print(image, a, res1)

