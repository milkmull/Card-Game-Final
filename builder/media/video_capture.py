import cv2
import pygame as pg

class Video_Capture:  
    def __init__(self):
        self.cap = None
        
    @property
    def exists(self):
        if self.cap:
            return self.cap.isOpened()
            
    def __del__(self):
        self.close()
        
    def start(self):
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        
    def stop(self):
        if self.cap:
            self.cap.release()
            self.cap = None
      
    def close(self):
        self.stop()
        cv2.destroyAllWindows()
        
    def get_frame(self):
        if self.cap:
            ret, frame = self.cap.read()
            if ret:
                image = pg.image.frombuffer(frame.tobytes(), frame.shape[1::-1], "BGR").convert_alpha()
                return image
            
    