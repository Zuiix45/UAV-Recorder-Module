from recorder import VideoCapture

def main():
    capture = VideoCapture("Cam_1", 0)
    
    while True:
        capture.parseNextFrame(True)
        capture.getFrame().addLockingRect(150, 150, 50, 50)
        
        # break the loop if q key is pressed
        if capture.getFrame().showFrame() & 0xFF == ord('q'):
            break
        
    capture.exportVideo("video.mp4", "mp4v", 15, True)

if __name__ == "__main__":
    main()
    