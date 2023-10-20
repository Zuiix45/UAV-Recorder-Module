import cv2 as cv
import numpy as np
import datetime

# The `Frame` class is used to create and display frames with various rectangles and a timestamp.
class Frame:
    def __init__(self, captureName: str, frame, width: int, height: int):
        self.captureName = captureName
        self.frame = frame
        self.Ak = (0, 0, width, height)
        self.Av = (int(width*0.25), int(height*0.1), int(width*0.75), int(height*0.9)) # Calculate Target Hitting Area coordinates
                    
        cv.rectangle(self.frame, (self.Av[0], self.Av[1]), (self.Av[2], self.Av[3]), (255, 0, 0), 2) # View range of camera
        cv.rectangle(self.frame, (self.Ak[0], self.Ak[1]), (self.Ak[2], self.Ak[3]), (0, 255, 0), 2) # Target Hitting Area
        
        # Add Timestamp
        currentTime = datetime.datetime.utcnow().strftime('%d/%m/%Y, %T.%f')[:-3] # dd/mm/yyyy, hh:mm:ss.ms
    
        fontFace: int = cv.FONT_HERSHEY_PLAIN
        fontScale: float = 1
        textThickness: int = 1
        
        # Adjust timestamp location
        (timeStampW, timeStampH), baseline = cv.getTextSize(str(currentTime), cv.FONT_HERSHEY_PLAIN, fontScale, textThickness)
        
        timeStampX = self.Ak[2] - timeStampW - baseline
        timeStampY = timeStampH + baseline
        
        cv.putText(self.frame, str(currentTime), (timeStampX, timeStampY), fontFace, fontScale, (0, 255, 0), textThickness)
        
    def addLockingRect(self, x, y, width, height):
        self.Ah = (x, y, width, height)
        
        # Check if the locking rectangle is inside of the Target Hitting Area
        # Display locking rectangle and return true if the locking area is inside of the Target Hitting Area
        if (self.Ah[0] > self.Av[0] and self.Ah[0]+self.Ah[2] < self.Av[2]):
            if (self.Ah[1] > self.Av[1] and self.Ah[1]+self.Ah[3] < self.Av[3]):
                cv.rectangle(self.frame, (self.Ah[0], self.Ah[1]), (self.Ah[0]+self.Ah[2], self.Ah[1]+self.Ah[3]), (0, 0, 255), 2)
                return True
            
        return False
        
    def showFrame(self):
        cv.imshow(self.captureName, self.frame)
        return cv.waitKey(1)
        
# The `VideoCapture` class is a Python class that provides functionality for capturing frames from a
# video source, resizing and flipping frames, storing frames in a list, retrieving frames by index,
# exporting frames to a video file, and closing the video capture.
class VideoCapture:
    def __init__(self, name: str, source, width: int=0, height: int=0):
        """
        Don't set width and height values to capture frames with original size
        
        Source parameter can be a video file path, local camera port, IP camera url
        """
        self.name = name
        self.capture = cv.VideoCapture(source) # start capturing
        self.width = width
        self.height = height
        self.resize = True
        self.frameList = list()
        
        if self.width == 0:
            self.width = int(self.capture.get(3))
            self.resize = False
        
        if self.height == 0:
            self.height = int(self.capture.get(4))
            self.resize = False
        
    def parseNextFrame(self, flip: bool = False):
        isSuccessful, capturedFrame = self.capture.read()
        
        if not(isSuccessful):
            # Replace with the blank frame if the frame is not captured successly.
            capturedFrame = np.zeros((self.width, self.height), dtype="uint8")
            
        if self.resize:
            capturedFrame = cv.resize(capturedFrame, (self.width, self.height), interpolation=cv.INTER_AREA)
            
        if flip:
            capturedFrame = cv.flip(capturedFrame, 1) # Flip horizontally
        
        self.frameList.append(Frame(self.name, capturedFrame, self.width, self.height)) # Save frames into the list
        
        return len(self.frameList)-1 # Index of parsed frame

    def getFrame(self, index: int=-1) -> Frame:
        if abs(index) >= len(self.frameList):
            return self.frameList[-1]
        
        return self.frameList[index]

    def exportVideo(self, outFile: str, codec: str, frameRate: int, close: bool):
        fourcc = cv.VideoWriter_fourcc(*codec)
        out = cv.VideoWriter(outFile, fourcc, frameRate, (self.width, self.height))
        
        for f in self.frameList:
            out.write(f.frame)
            
        out.release()
        
        if close:
            cv.destroyAllWindows()
            