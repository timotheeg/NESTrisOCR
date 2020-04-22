from config import config
import os
import cv2
from PIL import Image
import time
import threading

class WindowMgr():
    def __init__(self):
        pass
    
    def checkWindow(self, ocv2_device_id):
        return True
    
    def getWindows(self):
        ocv2_device_id = int(config.WINDOW_NAME)

        return [[ocv2_device_id, config.WINDOW_NAME]]


class VideoCaptureThreading:
    def __init__(self, src=0, width=640, height=480):
        self.src = src
        self.cap = cv2.VideoCapture(self.src)
        # self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        # self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.grabbed, self.frame = self.cap.read()
        self.started = False
        self.read_lock = threading.Lock()

    def set(self, var1, var2):
        self.cap.set(var1, var2)

    def start(self):
        if self.started:
            print("[!] Threaded video capturing has already been started.")
            return None
        self.started = True
        self.thread = threading.Thread(target=self.update, args=())
        self.thread.start()
        return self

    def update(self):
        while self.started:
            grabbed, frame = self.cap.read()
            with self.read_lock:
                self.grabbed = grabbed
                self.frame = frame

    def read(self):
        with self.read_lock:
            frame = self.frame.copy()
            grabbed = self.grabbed
        return grabbed, frame

    def stop(self):
        self.started = False
        self.thread.join()

    def __exit__(self, exec_type, exc_value, traceback):
        self.cap.release()


class OpenCVMgr():
    def __init__(self):
        self.imgBuf = None
        self.frameCount = 0
        self.cap = None

    def videoCheck(self, ocv2_device_id):
        if not self.cap:
            self.cap = VideoCaptureThreading(ocv2_device_id)
            self.cap.start()
            time.sleep(1)
            self.NextFrame()
                
    def ImageCapture(self, rectangle, ocv2_device_id):
        self.videoCheck(ocv2_device_id)
        return self.imgBuf.crop([rectangle[0],
                                rectangle[1],
                                rectangle[0]+rectangle[2],
                                rectangle[1]+rectangle[3]])

    def NextFrame(self):        
        if self.cap.started:
            ret, cv2_im = self.cap.read()
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