from flask import Flask
from flask import request
import os
os.environ['CUDA_VISIBLE_DEVICES'] = "0" 
import urllib.request as req
import urllib.parse as parse
import uuid
from gender2 import get_face_detector,get_gender_classifier
from time import time
import json

app = Flask(__name__)
MALE_THRESHOLD = 0.62
FEMALE_THRESHOLD = 0.36
detector = get_face_detector("./trained_models/face/mmod_human_face_detector.dat","./trained_models/face/shape_predictor_68_face_landmarks.dat")
classifier = get_gender_classifier("./trained_models/gender/alex.hdf5")
#alexNet is not uploaded to github,please using 'SimpleCNN'
def toJSON(gender = 3,err = "",vector = None):
    j = {"gender":str(gender),"err":err} 
    if vector != None:
        j["vector"] = vector
    return json.dumps(j)
       
@app.route("/")
def hello():
    return "Hello FaceGender!<br> please VISIT <b>/test</b> "

@app.route("/url",methods=["POST"])
def remote():
    url = request.values.get("url",0)
    print("raw url:" + url + "\n")
    if url == "":
        return toJSON(err="no url")
    randstr = uuid.uuid1().hex
    filename = "./tmp/"+randstr
    try:
      #  url = parse.unquote(url) 
      #  print(url)
        req.urlretrieve(url,filename)
        faces = detector(filename)
        if len(faces) >0:
            vector = classifier(faces[0])[0].tolist()
            gender = vector[1]
            if gender > MALE_THRESHOLD:
                gender = 0 #male
            elif gender < FEMALE_THRESHOLD:
                gender = 1 #female
            else:
                gender = 3 #unknown
            os.remove(filename)
            return toJSON(gender=gender,vector=vector) 
        else:
            os.remove(filename)
            return toJSON(err = "no faces") 
    except Exception as e:
        #raise(e)
        return toJSON(err = repr(e)) 

@app.route("/post",methods=["POST"])
def post():
    randstr = uuid.uuid1().hex
    filename = "./tmp/" + randstr
    f = request.files["img"]
    f.save(filename)
    last = time()
    faces = detector(filename)
    if len(faces) > 0:
        vector = classifier(faces[0])[0].tolist()
        gender = vector[1]
        if gender > MALE_THRESHOLD:
            gender = 0 #male
        elif gender < FEMALE_THRESHOLD:
            gender = 1#female
        else:
            gender = 3 #unknown
        os.remove(filename)
        print(time() - last)
        return toJSON(gender=gender,vector=vector) 
    else:
        os.remove(filename)
        return toJSON(err="no faces") 

@app.route("/test")
def test():
    html = \
    '''
    <form action="post" method="post" enctype="multipart/form-data" name="upload_form">
  <label>choose file</label>
 <input name="img" type="file" accept="*"/>
 <input name="upload" type="submit" value="upload" />
</form>
</body>
'''
    return html

if __name__ == "__main__":
    if not os.path.exists("./tmp"):
        os.mkdir("tmp")
    app.run(host='0.0.0.0', port=8080, debug=True)
