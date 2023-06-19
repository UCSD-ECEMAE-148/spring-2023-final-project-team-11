# GPS DonkeyCar Meets OpenCV
  ![robocar](https://github.com/UCSD-ECEMAE-148/spring-2023-final-project-team-11/blob/381a6774dd6c780c78b22fd4cef08677185b0f17/robocar.png)

## Team Members 
Nelson Mejia (ECE) 
Trevor Oshiro (MAE)
Fatima Rivera(MAE)

# Class Assignments
DONKEY CAR GPS LAP
https://youtu.be/HF_uWr-LfZc 

DONKEY CAR 3 AUTONOMOUS LAPS
https://youtu.be/48AIkPg58hs

ROS2 LANE/LINE DETECTION LAPS

https://youtu.be/FVdoV9Ju1tA (line following)

https://youtu.be/wVU0CtzTTLg (outer lane)

https://youtu.be/kGFEa9MHVKs (inner lane) 

# Final Project Overview 
As a team, we wanted to build up from the GPS assignment we had at the beginning of the spring 2023 quarter. So we wanted to use DonkeyCar to create a predefined waypoint path that we wanted our car to follow while also doing sign detection. Depending on what sign out Robocar saw it would either turn left (_left.png), right (_right.png) or stop (_park.png). At first we wanted to use YOLO for the sign detection but after the advisement of our TA, we used OpenCV instead. 
## Project Hardware
BATTERY HOLDER
![Battery Holder](https://github.com/UCSD-ECEMAE-148/spring-2023-final-project-team-11/blob/1f2ff2040c63c73849d0fed2d56ef6b0848c5629/battery%20holder.png)
https://drive.google.com/file/d/1CBKftGoKpYAd6sONSb91aAE9nv0K9wOS/view?usp=sharing 

CAMERA MOUNT
![Camera Holder](https://github.com/UCSD-ECEMAE-148/spring-2023-final-project-team-11/blob/95d3698ba76fe9bdd440be4e1cb2df6f27e9c0b1/cameramount.png)
https://drive.google.com/file/d/1UGOAdFSb1FseyxyXQ38SEtlAVXhtqSz_/view?usp=sharing 

JETSON NANO BOX
![Jetson Nano Box](https://github.com/UCSD-ECEMAE-148/spring-2023-final-project-team-11/blob/2ad4946b3deb140e450b29f611d32e5377afdae4/jetsonnano.png)
https://drive.google.com/file/d/1mRmjw0yh-ud6LM5NPJpmIvlIRE6YK5zS/view?usp=sharing

GPS ANTENNA HOLDER
![Gps antenna](https://github.com/UCSD-ECEMAE-148/spring-2023-final-project-team-11/blob/29044bc4fc2926ed3c90b616b73a5f8f6f5585c7/gpsantennabox.png)
https://drive.google.com/file/d/1NxUeukkxruL37zQcKq5dU6Qp4947hLyl/view?usp=sharing 

OUR BASE
![base](https://github.com/UCSD-ECEMAE-148/spring-2023-final-project-team-11/blob/b4bb2b8e3c5cfcfc6559e24f26d613ec78e2cb63/top.png)
![base](https://github.com/UCSD-ECEMAE-148/spring-2023-final-project-team-11/blob/f0288253a1da134d82cac0e02485542b9c3a0a17/view.png)
![base](https://github.com/UCSD-ECEMAE-148/spring-2023-final-project-team-11/blob/903045cc1f24e84ae3c78fb32253ca0b6a2ae88d/actual.png)

CIRCUIT DIAGRAM
![wires](https://github.com/UCSD-ECEMAE-148/spring-2023-final-project-team-11/blob/966e17f99d5ce88e912dde342c222c295c03093d/circut.png) 

## Documentation                                                                                                                                                                                                                               
https://docs.google.com/presentation/d/1tIUrr8ocEmKy1naIhokfaQ5sWk7dOD0NittV1mmkf3Q/edit?usp=sharing (Progress slides)
https://docs.google.com/presentation/d/1rF5Uken820gmBtOeDeFbb__R1WndTImoSI1vXXBAYzQ/edit?usp=sharing (Final slides)

## Project Software
NEEDED                                                                                                                                                                                                                                 
OpenCV                                                                                                                                                                                                                       
Depth ai                                                                                                                                                                                                                                           
DonkeyCar                      

THE PROCESS                                                                                                                                                                                                                     
Using Donkeycar GPS navigation we added a Python script to path_follow_car directory that mimicked the manage.py we used for the assignment given in class. In our case, this Python script is called manage_detect.py. Then in donkeycar/donkeycar/parts we added our SignDiff.py. This script would control the throttle and steering of our car when it would detect any of the signs we had. 

Depth ai was utilized through the incorporation of the OAKD camera part within the donkeycar framework. When activating the part, we specified values for the frame dimensions it would output. Through the pipeline created for the camera, the OAKD camera part continuously received image frames through the threaded execution of the run_threaded function for the part. This allowed for the component to run alongside the other part's processes for more efficient image processing. 


Importing OAKD part:
```
from donkeycar.parts.camera import OAKD
```
Initializing the part with frame dimensions:
```
frames = OAKD(image_w=640, image_h=480)
```

The sign detection part of the process was carried out with the SignDetect part created with the donkeycar framework. The code takes in the images from the OAKD camera and outputs the signs it recognizes (if any) via a string. For debugging purposes, the code also can be set to output frames to show live feed for the sign detection. This was mainly utilized to spot any areas needed for tuning within the application of computer vision filtering techniques. The DaiDis part was utilized for this purpose, as it only takes inputs from the camera/sign detection and displays them in a separate window.

Adding sign detection part to te vehicle:
```
V.add(signd, inputs=['camera/image','camera/sign'], outputs=['camera/sign'])
```
Adding image display part for debugging:
```
display = DaiDis()
V.add(display, inputs=['camera/sign'])
```

We then triggered the car's throttle and steering to react to the signs with the use of another part named Throttle. This was placed sequentially after the PID control outputs for navigation. This was done to override the path follwowing values when the sign was detected. After the dign was detected, the throttle controls then reverted back to the GPS navigation code through the pass statement used within Throttle, for signs not detected. 

Stop sign control example:
```
if sign == "_park.png":
  self.throttle = 0
  return self.steering, self.throttle
```

WARNING the png images you use for the sign detection must go in the same directory as your Python script. So our images were also uploaded into the parts directory of DonkeyCar. This gave us a functional robocar that performed well for our final project. 
We would also like to give thanks to https://github.com/jayeshbhole/Sign-Detection-OpenCV.git which helped us figure out how to go on with OpenCV and our sign detection. 

