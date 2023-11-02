import cv2
import os
from keras.models import load_model
import numpy as np
from pygame import mixer
import speech_recognition as sr
import pyttsx3
import time
import serial
from twilio.rest import Client

s = serial.Serial('COM5',9600)

# +12538678873
#set TWILIO_ACCOUNT_SID=ACa3fe27abd20c066336b86591edd8b45e
#set TWILIO_AUTH_TOKEN=632e19e907b60ba9a42e216d4d46b15b


# mixer.init()
# sound = mixer.Sound('alarm.wav')

face = cv2.CascadeClassifier('haar cascade files\haarcascade_frontalface_alt.xml')
leye = cv2.CascadeClassifier('haar cascade files\haarcascade_lefteye_2splits.xml')
reye = cv2.CascadeClassifier('haar cascade files\haarcascade_righteye_2splits.xml')

lbl=['Close','Open']

model = load_model('models/cnncat2.h5')
path = os.getcwd()
cap = cv2.VideoCapture(0)
font = cv2.FONT_HERSHEY_COMPLEX_SMALL
status=""
count=0
score=0
listen=0
thickRed=2
thickGreen = 10
thickYellow = 2
rpred=[99]
lpred=[99]

while(True):
    ret, frame = cap.read()
    height,width = frame.shape[:2] 

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    faces = face.detectMultiScale(gray,minNeighbors=5,scaleFactor=1.1,minSize=(25,25))
    left_eye = leye.detectMultiScale(gray)
    right_eye =  reye.detectMultiScale(gray)

    cv2.rectangle(frame, (0,height-50) , (200,height) , (0,0,0) , thickness=cv2.FILLED )

    for (x,y,w,h) in faces:
        cv2.rectangle(frame, (x,y) , (x+w,y+h) , (100,100,100) , 1 )

    for (x,y,w,h) in right_eye:
        r_eye=frame[y:y+h,x:x+w]
        count=count+1
        r_eye = cv2.cvtColor(r_eye,cv2.COLOR_BGR2GRAY)
        r_eye = cv2.resize(r_eye,(24,24))
        r_eye= r_eye/255
        r_eye=  r_eye.reshape(24,24,-1)
        r_eye = np.expand_dims(r_eye,axis=0)
        rpred = model.predict(r_eye)
        rpred = np.argmax(rpred,axis=1)
        #print(rpred)
        if(rpred[0]==1):
            lbl='Open' 
        else:
            lbl='Closed'
        break

    for (x,y,w,h) in left_eye:
        l_eye=frame[y:y+h,x:x+w]
        count=count+1
        l_eye = cv2.cvtColor(l_eye,cv2.COLOR_BGR2GRAY)  
        l_eye = cv2.resize(l_eye,(24,24))
        l_eye= l_eye/255
        l_eye=l_eye.reshape(24,24,-1)
        l_eye = np.expand_dims(l_eye,axis=0)
        lpred = model.predict(l_eye)
        lpred = np.argmax(lpred,axis=1)
        #print(lpred)
        if(lpred[0]==1):
            lbl='Open'   
        else:
            lbl='Closed'
        break

    
    if(rpred[0]==1 and lpred[0]==1):
        if(score>0):
            score=score-1
        cv2.putText(frame,"Eyes Open",(20,height-20), font, 1,(255,255,255),1,cv2.LINE_AA)
        if(thickGreen<10):
            thickGreen=thickGreen+1
        s.write(b'o')
        time.sleep(2)
        status="Active:)"

    else:
        score=score+1
        cv2.putText(frame,"Eyes Closed",(20,height-20), font, 1,(255,255,255),1,cv2.LINE_AA)
        if(thickGreen>1):
            thickGreen=thickGreen-1
        status="Drowsy!"
        
    cv2.putText(frame,'Score : '+str(score),(230,height-20), font, 1,(255,255,255),1,cv2.LINE_AA)
    cv2.putText(frame,'Status : '+status,(420,height-20), font, 1,(255,255,255),1,cv2.LINE_AA)

    if(score<0):
        score=0  
    if(score>=0 and score<=3):
        if(score<=1):
            cv2.rectangle(frame,(0,0),(width,height),(0,255,0),thickGreen)
        else:
            if(thickYellow<16):
                thickYellow = thickYellow+2
            else:
                thickYellow = thickYellow-2
                if(thickYellow<2):
                    thickYellow=2
            cv2.rectangle(frame,(0,0),(width,height),(0,255,255),thickYellow)
    if(score>3):
        #person is feeling sleepy so we beep the alarm
        cv2.imwrite(os.path.join(path,'image.jpg'),frame)

        try:
            s.write(b'c')
            time.sleep(2)
        except Exception as e:
            print(e)

        if(score>5):
            # sound.stop()
            listener = sr.Recognizer()
            engine = pyttsx3.init()
            engine.say('Are you active?')
            engine.runAndWait()
            try:
                with sr.Microphone() as source:
                    listen+=1
                    if(listen>1):
                        print("not active")
                        # sound.play()
                        client = Client()
                        call = client.calls.create(
                            from_='+12538678873',
                            to='+919566492380',
                            url='https://handler.twilio.com/twiml/EHacf5fa52339cd74cde1a12bf94c1b485'
                        )
                        print("end")
                    print('Listening...',listen)
                    voice = listener.listen(source)
                    command = listener.recognize_google(voice)
                    print(len(command))
                    print("command :",command,"...")
                    if 'active' in command:
                        engine.say('Okay, please focus on the driving')
                        engine.runAndWait()
                        score = 0
                        listen = 0
                    else:
                        print("not active")
                        # sound.play()
                        client = Client()
                        call = client.calls.create(
                            from_='+12538678873',
                            to='+919566492380',
                            url='https://handler.twilio.com/twiml/EHacf5fa52339cd74cde1a12bf94c1b485'
                        )
                        print("end")
 
                    
            except Exception as e:
                print(e)


        if(thickRed<16):
            thickRed= thickRed+2
        else:
            thickRed=thickRed-2
            if(thickRed<2):
                thickRed=2
        cv2.rectangle(frame,(0,0),(width,height),(0,0,255),thickRed)
    cv2.imshow('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()