# Importing all necessary libraries
import cv2
import os
import argparse
import ffmpeg

parser = argparse.ArgumentParser()
parser.add_argument('--video', type=str, default='image', help='initial image')
parser.add_argument('--output', type=str, default='image', help='initial image')
parser.add_argument('--fpsinterval', type=int, default=1, help='fps interval')
opt = parser.parse_args()


vid = ffmpeg.probe(opt.video)
print(vid['streams'])


# Read the video from specified path
cam = cv2.VideoCapture(opt.video)


# creating a folder named data
if not os.path.exists(os.path.join(opt.output,'framerate'+str(opt.fpsinterval))):
    os.makedirs(os.path.join(opt.output,'framerate'+str(opt.fpsinterval)))


# frame
currentframe = 0

while(True):

    # reading from frame
    ret,frame = cam.read()

    if ret:
        # if video is still left continue creating images
        name = './'+os.path.join(opt.output,'framerate'+str(opt.fpsinterval),'frame') + str(currentframe) + '.jpg'
        print ('Creating...' + name)

        # writing the extracted images
        if currentframe % opt.fpsinterval == 0:
            cv2.imwrite(name, frame)

        # increasing counter so that it will
        # show how many frames are created
        currentframe += 1
    else:
        break

# Release all space and windows once done
cam.release()
cv2.destroyAllWindows()
