# MotionDetector

An application which detects motion from a video source and displays the times at which motion was recorded, aswell as drawing rectangles around moving objects in the video. Can accept video from pre recorded files or live webcam footage. Many settings can be modified such as sensitivity of the detector and minimum rectangle size for it to draw.

To run:  
    1) open terminal  
    2) cd directory to the MotionDetector/src folder  
    3) run "pip install -r requirements.txt" - all dependencies will then be installed  
    4) run "main.pyw" in the "src" folder  

Tested on python 3.10, will not work on older versions of python due to match statement being used
