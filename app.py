from flask import Flask,render_template,redirect,request
import openpyxl
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
import cv2
import numpy as np
import face_recognition
import os
from os.path import exists
from datetime import datetime,date
import pandas as pd
from openpyxl import load_workbook
import csv

app=Flask(__name__)
database={'vaibhav':['1234','vaibhavrajpal26@gmail.com'],'vrinda':['5678','ab@yahoo.com'],'shivam':['abcd','xyz@gmail.com'],'elon':['tesla','spacex@gmail.com']}
#will make database like key would be the username and value would be list of password and mail

@app.route('/table')
def table():
    df = pd.read_excel('Attendance.xlsx')
    df.to_excel('Attendance.xlsx', index=None)
    data = pd.read_excel('Attendance.xlsx')
    return render_template('/attendance_record.html', tables=[data.to_html()], titles=[''])



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
                return render_template('/mark_attendance.html')
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
    return render_template("/about.html")               

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
        #df = pd.read_excel("Attendance.xlsx", usecols = ['Username'])
        #print(df)
        with open('Attendance.csv', 'r+') as f:
            myDataList = f.readlines()
            nameList = []
            print(nameList)
            if(name in myDataList):
                return True

            for line in myDataList:
                entry = line.split(',')
                nameList.append(entry[0])
            if name not in nameList:
                now = datetime.now()
                date_today=date.today();
                dtString = now.strftime('%H:%M:%S')
                convert_to_format=date_today.strftime("%d-%m-%Y")
                #f.writelines(f'{name},{dtString},{convert_to_format}')
                '''writer = pd.ExcelWriter('Attendance.xlsx', engine='openpyxl') 
                wb  = writer.book
                df = pd.DataFrame({'Username': [name],
                    'Date': [convert_to_format],
                  'Time': [dtString]})
                df.to_excel(writer, index=False)
                wb.save('Attendance.xlsx')'''
                wb=openpyxl.load_workbook('Attendance.xlsx')
                sh1=wb['Sheet1']
                row=sh1.max_row
                column=sh1.max_column
                is_added=False
                for i in range(1,row+1):
                    if (sh1.cell(row=i,column=1).value==name) and (sh1.cell(row=i,column=3).value==convert_to_format):
                            is_added=True

                if(is_added==False):
                    sh1.cell(row=row+1,column=1,value=name)
                    sh1.cell(row=row+1,column=2,value=dtString)
                    sh1.cell(row=row+1,column=3,value=convert_to_format)
                wb.save('Attendance.xlsx')
                return True
        return False
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
        to_close_the_web_cam=False
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
                to_close_the_web_cam=markAttendance(name)
            if(to_close_the_web_cam):
                break
        cv2.imshow('Webcam', img)
        cv2.waitKey(1)
        if(to_close_the_web_cam):
            break
    cap.release()
    cv2.destroyAllWindows()
    #return render_template("index.html")
    return render_template("/mark_attendance.html",info='Your Attendance Has Been Taken')


if __name__=="__main__":
    #database.clear()

    app.run(debug=True)
