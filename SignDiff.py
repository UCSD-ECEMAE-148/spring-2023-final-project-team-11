import cv2
import numpy as np

class Throttle(object):
    def __init__(self):
        # Initialize the throttle and steering values as zero
        self.throttle = 0
        self.steering = 0
    
    def run(self,sign):
        if sign == "_park.png":
            # Send a zero throttle value to the controller at a stop sign
            self.throttle = 0
            return self.steering, self.throttle
        elif sign == "_right.png":
            # Swerves right when encountering the sign
            # Sends a positive throttle
            self.throttle = 0.8
            # Sends a positive steering value for the PWM steering
            self.steering = 0.5
            return self.steering, self.throttle
        elif sign == "_left.png":
            # Swerves left when encountering the sign
            # Sends a positive throttle
            self.throttle = 0.8
            # Sends a negative steering value for the PWM steering
            self.steering = -0.5
            return self.steering, self.throttle
        else: 
            # If there isn't a sign detection outputted from the sign detection part,
            # throttle and steering values aren't outputted, and the gps resumes its route
            pass

class DaiDis(object):
    def __init__(self):
        # Initializing the frame
        self.signframe = "None"

    def run(self,image):
        # Displaying the resulting image processed with the sign detection code 
        # This part is mainly used for debugging the sign detection
        self.signframe = image
        cv2.imshow("Video", self.signframe)
        # print(image)

class SignDetect(object):
 
    def __init__(self):
        # Difference Variables/Initialization
        self.minDiff = 12000
        self.minSquareArea = 5000
        self.match = -1
        self.w=640
        self.h=480
        self.tarea = 1000
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        
        # Getting reference pictures for reading
        # png files for the images were copied directly into the parts directory of donkeycar
        self.ReferenceImages = ["_turnAround.png", "_park.png", "_left.png", "_right.png", "_spinAround.png", "_charge.png"]
        self.ReferenceTitles = ["_turnAround.png", "_park.png", "_left.png", "_right.png", "_spinAround.png", "_charge.png"]
        
        # Initializing variables to be returned for the sign detection code
        self.signFrame = "None"
        self.sign_read =  "None"
        self.running = True

    def run(self,image_in, read):
        self.signRead(image_in)

        # Used when debugging returned sign values with a separate sign reverting part added
        # if read == "Switch":
        #     self.sign_read = "None"
        print(self.sign_read)

        # For debugging the sign detection algorithm
        # return self.signFrame
        return self.sign_read

    def signRead(self,image_in,read):
        class Symbol:
            def __init__(self):
                self.img = 0
                self.name = 0
        # define class instances (6 objects for 6 different images)
        symbol= [Symbol() for i in range(6)]
        
        for count in range(6):
            image = cv2.imread(self.ReferenceImages[count], cv2.COLOR_BGR2GRAY)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            symbol[count].img = cv2.resize(image,(self.w//2,self.h//2),interpolation = cv2.INTER_AREA)
            symbol[count].name = self.ReferenceTitles[count]
            #cv2.imshow(symbol[count].name,symbol[count].img);

        # Storing image taken in by the camera
        OriginalFrame = image

        gray = cv2.cvtColor(OriginalFrame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray,(3,3),0)
            
        # Detecting Edges: CV was giving errors for the autocanny function outside, so it was moved in the run loop
        # compute the median of the single channel pixel intensities
        v = np.median(image)
        # apply automatic Canny edge detection using the computed median
        lower = int(max(0, (1.0 - 0.33) * v))
        upper = int(min(255, (1.0 + 0.33) * v))
        edges = cv2.Canny(image, lower, upper)

        # Contour Detection & checking for squares based on the square area
        contours, hierarchy = cv2.findContours(edges,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            approx = cv2.approxPolyDP(cnt,0.0337*cv2.arcLength(cnt,True),True)

            if len(approx)==4:
                area = cv2.contourArea(approx)

                if area > self.minSquareArea:
                    cv2.drawContours(OriginalFrame,[approx],0,(0,0,255),2)
                    warped = self.four_point_transform(OriginalFrame, approx.reshape(4, 2))
                    warped_eq = self.resize_and_threshold_warped(warped)
                                    
                    pts = approx.reshape(4,2)
                    di_st ,di_rn = self.dist_dir(pts)
                                    
                                    
                    for i in range(6):
                        diffImg = cv2.bitwise_xor(warped_eq, symbol[i].img)
                        diff = cv2.countNonZero(diffImg);

                        if diff < self.minDiff:
                            match = i

                            # Setting read sign to the variable sign_read
                            # Outputs to the throttle part which responds to the detection
                            self.sign_read = symbol[i].name

                            # Debugging for finding sign detections outputted
                            # print(symbol[i].name)
                            # cv2.putText(OriginalFrame,symbol[i].name, tuple(approx.reshape(4,2)[0]), self.font, 1, (200,0,255), 2, cv2.LINE_AA)

                            # Reverts the sign read to none for the car to resume normal PID piloting along the path
                            if self.sign_read == read:
                                self.sign_read = "None"
                                            
                            diff = self.minDiff
                                            
                            break;
    
                    # Part DaiDis takes in modified OriginalFrame to give users a preview for debugging
                    # cv2.putText(OriginalFrame,str(di_rn),(100,100), self.font, 2,(0,0,255),2,cv2.LINE_AA)
                    # self.signFrame = OriginalFrame
           


    def dist_dir(self, pts):
        rect = self.order_points(pts)
        markerSize = rect[1][0] - rect[0][0]
     
        if markerSize == 0:
            distance = 0
        else:
            distance = int( (10 * 1200 )/ markerSize)
    
        direction = (640) - ((rect[0][0] + rect[1][0] + rect[2][0] + rect[3][0]) // 4)
        return distance, direction
    
    def order_points(self, pts):
        # initialzie a list of coordinates that will be ordered
        # such that the first entry in the list is the top-left,
        # the second entry is the top-right, the third is the
        # bottom-right, and the fourth is the bottom-left
        rect = np.zeros((4, 2), dtype = "float32")

        # the top-left point will have the smallest sum, whereas
        # the bottom-right point will have the largest sum
        s = pts.sum(axis = 1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]

        # now, compute the difference between the points, the
        # top-right point will have the smallest difference,
        # whereas the bottom-left will have the largest difference
        diff = np.diff(pts, axis = 1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]

        # return the ordered coordinates
        return rect

    def four_point_transform(self, image, pts):
        # obtain a consistent order of the points and unpack them
        # individually
        rect = self.order_points(pts)
        (tl, tr, br, bl) = rect                 #top-left top-right bottom-right bottom-left

        maxWidth = self.w//2
        maxHeight = self.h//2

        dst = np.array([
                [0, 0],
                [maxWidth - 1, 0],
                [maxWidth - 1, maxHeight - 1],
                [0, maxHeight - 1]], dtype = "float32")

        # compute the perspective transform matrix and then apply it
        M = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

        # return the warped image
        return warped

    def resize_and_threshold_warped(self, image):
        #Resize the corrected image to proper size & convert it to grayscale
        #warped_new =  cv2.resize(image,(w/2, h/2))
        warped_new_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        #Smoothing Out Image
        blur = cv2.GaussianBlur(warped_new_gray,(5,5),0)

        #Calculate the maximum pixel and minimum pixel value & compute threshold
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(blur)
        threshold = (min_val + max_val)/2

        #Threshold the image
        ret, warped_processed = cv2.threshold(warped_new_gray, threshold, 255, cv2.THRESH_BINARY)
        warped_processed = cv2.resize(warped_processed,(320, 240))
        
            #return the thresholded image
        return warped_processed
