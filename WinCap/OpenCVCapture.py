from config import config
import os
import cv2
from PIL import Image
import time

class WindowMgr():
    def __init__(self):
        pass
    
    def checkWindow(self, fileName):
        return True
    
    def getWindows(self):
        return [[int(config.WINDOW_NAME), config.WINDOW_NAME]]

class OpenCVMgr():
    def __init__(self):
        self.inputDevice = None
        self.imgBuf = None
        self.frameCount = 0

    def videoCheck(self, cv2_input_device_index):
        if self.inputDevice is None:
            self.inputDevice = cv2.VideoCapture(cv2_input_device_index)
            self.NextFrame()
                
    def ImageCapture(self, rectangle, cv2_input_device_index):
        self.videoCheck(cv2_input_device_index)
        return self.imgBuf.crop([rectangle[0],
                                rectangle[1],
                                rectangle[0]+rectangle[2],
                                rectangle[1]+rectangle[3]])

    def NextFrame(self):        
        if self.inputDevice.isOpened():
            ret, cv2_im = self.inputDevice.read()
            if ret:
                cv2_im = cv2.cvtColor(cv2_im,cv2.COLOR_BGR2RGB)
                self.imgBuf = Image.fromarray(cv2_im)
                self.frameCount += 1
                if (self.frameCount % 1000 == 0):
                    print ('frames', self.frameCount)
                return True
    
        return False

imgCap = OpenCVMgr()

def ImageCapture(rectangle, hwndTarget):
    global imgCap
    return imgCap.ImageCapture(rectangle,hwndTarget)

#returns false if we want to exit the program
def NextFrame():
    global imgCap
    return imgCap.NextFrame()