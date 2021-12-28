
import cv2
import cv2 as cv
import numpy as np
global width 
global height
boxes = []

# Function to crop the object to track from video at initialization
def on_mouse(event, x, y, flags, params):

    global width
    global height
    if event == cv.EVENT_LBUTTONDOWN:
         print('Start Mouse Position: '+str(x)+', '+str(y))
         sbox = [x, y]
         boxes.append(sbox)

    elif event == cv.EVENT_LBUTTONUP:
        print('End Mouse Position: '+str(x)+', '+str(y))
        ebox = [x, y]
        boxes.append(ebox)
        print(boxes)
        crop = imgCamColor[boxes[-2][1]:boxes[-1][1],boxes[-2][0]:boxes[-1][0]]
        cv2.imshow('crop',crop)
        cv2.imwrite('Crop.jpg',crop)
        print("Written to file")
        print("Press Enter to continue")
        width=(boxes[-1][1]-boxes[-2][1])/2
        height=(boxes[-2][0]-boxes[-2][1])

ESC=27   
camera = cv2.VideoCapture('robot.mp4')
orb = cv.ORB_create()
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

cv2.destroyAllWindows()
ret, imgCamColor = camera.read()

#The time at which the tracking starts
init=0
while init<1230:
    ret, imgCamColor = camera.read()
    init=init+1

cv2.namedWindow('Bound the robot')
cv2.setMouseCallback('Bound the robot',on_mouse,0)
cv2.imshow('Bound the robot',imgCamColor)
cv2.waitKey(0)
firsttime=True
pts=[]
second=True


while True:
    imgTrainColor=cv2.imread('Crop.jpg')
    imgTrainGray = cv2.cvtColor(imgTrainColor, cv2.COLOR_BGR2GRAY)
    kpTrain = orb.detect(imgTrainGray,None)
    kpTrain, desTrain = orb.compute(imgTrainGray, kpTrain)


    ret, imgCamColor = camera.read()
    if not ret:
        break
    imgCamGray = cv2.cvtColor(imgCamColor, cv2.COLOR_BGR2GRAY)
    kpCam = orb.detect(imgCamGray,None)
    kpCam, desCam = orb.compute(imgCamGray, kpCam)
    matches = bf.match(desCam,desTrain)
    dist = [m.distance for m in matches]
    
    
    if len(dist)==0:
        dist=[1]
    thres_dist = (sum(dist) / len(dist)) * 0.5
    matches = [m for m in matches if m.distance < thres_dist]

    if firsttime==True:

        h1, w1 = imgCamColor.shape[:2]
        h2, w2 = imgTrainColor.shape[:2]
        nWidth = w1+w2
        nHeight = max(h1, h2)
        hdif = int((h1-h2)/2)
        firsttime=False
    if h1>h2:
        
        result = np.zeros((nHeight, nWidth, 3), np.uint8)
        result[hdif:hdif+h2, :w2] = imgTrainColor
        result[:h1, w2:w1+w2] = imgCamColor
    else:
    
        result = np.zeros((nHeight, nWidth, 3), np.uint8)
        result[:h2, :w2] = imgTrainColor
        result[hdif:hdif+h1, w2:w1+w2] = imgCamColor
    pts=[]    
    for i in range(len(matches)):
        pt_a=(int(kpTrain[matches[i].trainIdx].pt[0]), int(kpTrain[matches[i].trainIdx].pt[1]+hdif))
        pt_b=(int(kpCam[matches[i].queryIdx].pt[0]+w2), int(kpCam[matches[i].queryIdx].pt[1]))
        pts.append(pt_b)
        cv2.line(result, pt_a, pt_b, (255, 0, 0))

    #newcrop
    #reference image gets updated every loop
    if (len(pts)<5)&(second==False):

        crop=imgCamColor[int(cg[0][1]-height):int(cg[0][1]+height),int(cg[0][0]-width):int(cg[0][0]+width)]
        cv2.imshow('crop',crop)
        cv2.imwrite('Crop.jpg',crop)
        firsttime=True
        continue

    su=[0,0]
    cg=[]
    
    for i in pts:
        su[0]=su[0]+i[0]-w2
        su[1]=su[1]+i[1]

    cg.append([su[0]/len(pts),su[1]/len(pts)])
    vert1=()
    vert2=()
    cgx=cg[0]
    vert1=(int(cg[0][0]-width),int(cg[0][1]-height))
    vert2=(int(cg[0][0]+width),int(cg[0][1]+height))

    cv2.rectangle(imgCamColor,vert1,vert2,(255,255,0))
    cv2.imshow('Camera', imgCamColor)
    

    key = cv2.waitKey(1)
    if key == ESC:
        break
    second=False
cv2.waitKey(0)    
cv2.destroyAllWindows()
camera.release()
