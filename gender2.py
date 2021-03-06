import cv2
import dlib
#dlib 19.9 or later version.
import numpy as np

from keras.models import load_model
from myutils.datasets import get_labels
from myutils.inference import detect_faces
from myutils.inference import apply_offsets
from myutils.inference import load_image
from myutils.preprocessor import preprocess_input

def get_face_detector(detect_model,sp_model):
    cnn_face_detector = dlib.cnn_face_detection_model_v1(detect_model)
    sp = dlib.shape_predictor(sp_model)
    def inner(path):
        raw_img = cv2.imread(path) #bgr
        print(path)
        if type(raw_img) == type(None):
            return []
        raw_img = resize_image(raw_img,320,320)
        rgb_img = cv2.cvtColor(raw_img,cv2.COLOR_BGR2RGB)
        dets = cnn_face_detector(rgb_img, 1)
        ret = []
        for d in dets:
            face = sp(rgb_img, d.rect)
            image = dlib.get_face_chip(rgb_img, face, size=320)
            ret.append(image)
        return ret
    return inner


def resize_image(image, height, width):
    top, bottom, left, right = (0, 0, 0, 0)
    shape = image.shape
    h = shape[0]
    w = shape[1]
    # 对于长宽不相等的图片，找到最长的一边
    longest_edge = max(h, w)
    # 计算短边需要增加多少像素宽度使其与长边等长
    if h < longest_edge:
        dh = longest_edge - h
        top = dh // 2
        bottom = dh - top
    elif w < longest_edge:
        dw = longest_edge - w
        left = dw // 2
        right = dw - left
    else:
        pass
    BLACK = [0, 0, 0]
    # 给图像增加边界，是图片长、宽等长，cv2.BORDER_CONSTANT指定边界颜色由value指定
    constant = cv2.copyMakeBorder(image, top, bottom, left, right, cv2.BORDER_CONSTANT, value=BLACK)
    # 调整图像大小并返回
    return cv2.resize(constant, (height, width))

def get_gender_classifier(model_path):
    # loading models
    gender_classifier = load_model(model_path, compile=False)
    # getting input model shapes for inference
    gender_target_size = gender_classifier.input_shape[1:4]
    print(gender_target_size)
    def inner(img):
        face = cv2.resize(img,(gender_target_size[0],gender_target_size[1]))
        if face.shape[-1] == 3:
            #gray
            face = cv2.cvtColor(face,cv2.COLOR_RGB2GRAY)
        face = preprocess_input(face,True)
        face = np.expand_dims(face,-1)
        face = np.expand_dims(face,0)
        print(face.shape)
        prediction = gender_classifier.predict(face)
        return prediction
    print("test :" +str( inner(np.zeros(gender_target_size))))
    return inner
