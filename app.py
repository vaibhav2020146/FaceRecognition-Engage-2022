from flask import Flask,render_template,redirect,request
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime

app=Flask(__name__)
database={'vaibhav':['1234','vaibhavrajpal26@gmail.com'],'shubham':['5678','ab@yahoo.com'],'shivam':['abcd','xyz@gmail.com'],'elon':['tesla','spacex@gmail.com']}
#will make database like key would be the username and value would be list of password and mail

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLD = 'static/uploads'
UPLOAD_FOLDER = os.path.join(APP_ROOT, UPLOAD_FOLD)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/form_signup',methods=['GET','POST'])
def form_signup():
    if request.method=='POST':
        uname=request.form['username']
        passw=request.form['password']
        mail=request.form['mail']
        if uname in database:
            return render_template('/signup_page.html',info='Username Already Exists.Please Try Something Else')
        else:
            database[uname]=[passw,mail]
            print(database)
            return render_template('/signup_page.html',info='UserName Is Available. Now Upload Your Photo')
    return render_template('/signup_page.html')


@app.route('/form_login',methods=['GET','POST'])
def form_login():
    #for logging in the the system
    if request.method=='POST':
        name1=request.form['username']
        pwd=request.form['password']
        #name1='vaibhav'
        # #pwd='12345'
        print(name1,pwd)
        if name1 not in database:
            return render_template('/login_page.html',info='Invalid Username')
        else:
            if database[name1][0]!=pwd:
                # after login gets successful it redirects to the page where attendence woulde be taken
                # # make the attendence webpage and change the below location to it
                return render_template('/login_page.html',info='Invalid Password')
            else:
                return render_template('/index.html',info='All Correct')
    return render_template('/login_page.html')


@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
    #used to upload the image and save it in the same folder in which our project is
   if request.method == 'POST':
      f = request.files['file']
      #f.save(secure_filename(f.filename))
      f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
      #print(database)
      return render_template('/login_page.html',info='Signup Successful')

@app.route("/")
def home():
    #open the home page of the website
    return render_template("index.html")

@app.route("/about", methods=['GET', 'POST'])
def about():
    return render_template("about.html")               

@app.route("/login")
def login():
    path = "static/uploads"
    # just make a Images folder in c drive and put the images in it
    # path should be the path of the folder containing the images
    images = []
    classNames = []
    myList = os.listdir(path)
    print(myList)
    for cl in myList:
        curImg = cv2.imread(f'{path}/{cl}')
        images.append(curImg)
        classNames.append(os.path.splitext(cl)[0])
    print(classNames)
    
    def findEncodings(images):
        #will do encoding of the images and store it in the encodeListKnown
        encodeList = []
        for img in images:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            encode = face_recognition.face_encodings(img)[0]
            encodeList.append(encode)
        return encodeList
    
    def markAttendance(name):
        #will mark the attendance of the student and save it in the csv file
        with open('C:\\Users\\91991\\Desktop\\Project\\Attendance.csv', 'r+') as f:
            myDataList = f.readlines()
            nameList = []
            for line in myDataList:
                entry = line.split(',')
                nameList.append(entry[0])
            if name not in nameList:
                now = datetime.now()
                dtString = now.strftime('%H:%M:%S')
                f.writelines(f'n{name},{dtString}')

    encodeListKnown = findEncodings(images)
    print('Encoding Complete')
    #open the camera and takes the attendence
    #if error occur because of it then put it as same as in FaceDetect.py code
    cap = cv2.VideoCapture(0)
    while True:
        success, img = cap.read()
        # img = captureScreen()
        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
        facesCurFrame = face_recognition.face_locations(imgS)
        encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
        for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            # print(faceDis)
            matchIndex = np.argmin(faceDis)
            
            if matches[matchIndex]:
                name = classNames[matchIndex].upper()
                print(name)
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                markAttendance(name)
        cv2.imshow('Webcam', img)
        cv2.waitKey(1)
    cap.release()
    cv2.destroyAllWindows()
    #return render_template("index.html")
    return redirect("/")


if __name__=="__main__":
    #database.clear()
    app.run(debug=True)
