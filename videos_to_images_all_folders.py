# Importing all necessary libraries
import numpy as np
import cv2
import os
import argparse
import ffmpeg
import json


#This code is made to run using the following structure:
#-code
#-<field_name>
#   |---<field_name>_<dates>
#           |--->raw_images
#           |--->video
#                   |--->.mp4 files
#
#This code creates new directories with the names of the field and the output
#resolution.The structure within the new directory has the same configuration
#as the previous one, but within the <field_name><dates>, a new direcotry
#called "extracted images" is created.
#-<resolution>_<field_name>
#   |---<field_name>_<dates>
#           |--->raw_images
#           |--->video
#           |--->extracted images
#Where resolution can be 1080x720, 1920x1080 or other resolutions.


#function to resize images
def image_resizing(image,new_width,new_height):
    """
    @args:
    image: image array
    new_width: new width in the image
    new_height: new height in the image
    """
    #set up the new dimension and resize
    dim=(int(new_width),int(new_height))
    resized_image=cv2.resize(image, dim, interpolation = cv2.INTER_AREA)

    #return resized image
    return resized_image

#function to flip images to have an horizontal ratio
def horizontal_rotation_function(image):
    """
    @args:
    image: image array
    """
    #image dimensions
    height, width, color_channel = image.shape

    #Check whether the image is in vertical orientation to rotate it horizontally.
    if height > width:
        image= cv2.rotate(image,cv2.ROTATE_90_CLOCKWISE)
        return image
    else:
        return image

    return image

#function to flip images to have an vertical ratio
def vertical_rotation_function(image):
    """
    @args:
    image: image array
    """
    #image dimensions
    height, width, color_channel = image.shape

    #Check whether the image is in horizontal orientation to rotate it vertically.
    if width > height:
        image= cv2.rotate(image,cv2.ROTATE_90_CLOCKWISE)
        return image
    else:
        return image

    return image

def image_ratio_cropping(image,ratio_width,ratio_height):
    """
    @args:
    image: image array
    ratio_width: proportion of the width e.g. 16
    ratio_height: proportion of the height e.g. 9
    """

    #image dimensions
    height, width, color_channel = image.shape

    #orientation independent cropping
    if width > height:
        longest_side= width
        shortest_side= height
    else:
        longest_side= height
        shortest_side= width


    #get the current width to height ratio.
    current_ratio=float(float(longest_side)/float(shortest_side))

    #Get the desired ratio
    desired_ratio=float(float(ratio_width)/float(ratio_height))

    #In the new image, we need to decrease the "advantage" of the shortest side over the longest side
    if desired_ratio > current_ratio:
        #get the height we need to get
        new_shortest_side=int(float((float(longest_side)*float(ratio_height))/float(ratio_width)))

        #crop the image
        if width > height:
            image=image[0:new_shortest_side,:]
        else:
            image=image[:,0:new_shortest_side]

    #In the new image, we need to reduce the advantage of the longest side over the shortest side
    elif desired_ratio < current_ratio:
        #get the width we need to get.
        new_longest_side=float((float(shortest_side)*float(ratio_width))/float(ratio_height))

        #crop the image
        if width > height:
            image=image[:,0:new_longest_side]
        else:
            image=image[0:new_longest_side:]

    #we have finished with the cropping. Then, return image
    return image

#fucnction to extract images from a video given a framerate extraction
def image_extraction_video(videopath,framerate_extraction_interval,output,
                            resize=False, horizontal_rotation=True,vertical_rotation=False,
                            new_width=1980, new_height=1080, rename_videoframe=False,
                            new_name='initial'):
    """
    @args
    videopath: path of the video where are about to open.
    framerate_extraction_interval: Every how many frames of the video we get an image
    output: path where the ouptput is gonna be saved
    resize (bool): whether the  frames are resized or not.
    horizontal_rtation (bool): Whether rotate the image to have a horizontal orientation.
    vertical_rotation (bool): Whether rotate the image to have a vertical orientation.
    new_width: In case resize == True, this is the new width of the image.
    new_height:In case resize == True, this is the new height of the image.
    """

    #read the video from specified path
    cam = cv2.VideoCapture(videopath)
    video_name=os.path.basename(videopath)
    video_name_no_extension=video_name.split(".")[0]

    #frame counter for filtering frames (currentframe) and for naming (frame_saving_name)
    currentframe = 0
    frame_saving_name=0

    #print statement
    print ('Saving information in %s' %str(output))

    #While loop to go through all the frame in the video.
    while(True):

        #reading from frame
        ret,frame = cam.read()

        #if there are frames availabel, continue.
        if ret:
            # if video is still left continue creating image
            # writing the extracted images
            if currentframe % framerate_extraction_interval == 0:
                #save videos.

                #If rename_videoframe is "True", then, it will rename the frame with

                #the name given in new_name
                if rename_videoframe:
                    image_name = os.path.join(output,str(new_name)+'_'+str(frame_saving_name)+'.png')
                else:
                    image_name = os.path.join(output,video_name_no_extension+'_'+str(frame_saving_name)+'.png')

                #Rotation and resizing options depending on the given information
                if resize:
                    frame=image_resizing(frame,new_width,new_height)

                #Horizontal rotation true will make the width of the image larger than the height.
                if horizontal_rotation:
                    frame=horizontal_rotation_function(frame)

                #Vertical rotation true will make the height of the image larger than the width.
                if vertical_rotation:
                    frame=vertical_rotation_function(frame)

                #save the frame
                print (image_name)
                cv2.imwrite(image_name, frame)
                print (os.path.join('./all_'+str(new_width)+"_"+str(new_height),str(new_name)+'_'+str(frame_saving_name)+'.png'))
                cv2.imwrite(os.path.join('./all_'+str(new_width)+"_"+str(new_height),str(new_name)+'_'+str(frame_saving_name)+'.png'), frame)
                frame_saving_name+=1

            #increasing counter so that it will,show how many frames are created
            currentframe += 1

        #stop if there are no more frames
        else:
            break

    # Release all space and windows once done
    cam.release()
    cv2.destroyAllWindows()


#Function to process the images based on our needs.
def image_processing(imagepath,output,resize=False,horizontal_rotation=True,vertical_rotation=False,
                    new_width=1980, new_height=1080, rename_image=False,new_name='initial',
                    image_ratio=False, ratio_width=16, ratio_height=9):
    """
    @args
    imagepath: path of the image where are about to open.
    output: path where the ouptput is gonna be saved
    resize (bool): whether the  frames are resized or not.
    horizontal_rtation (bool): Whether rotate the image to have a horizontal orientation.
    vertical_rotation (bool): Whether rotate the image to have a vertical orientation.
    new_width: In case resize == True, this is the new width of the image.
    new_height:In case resize == True, this is the new height of the image.
    """

    #Open the image
    image = cv2.imread(imagepath)


    #get the image name and extension
    image_name=os.path.basename(imagepath)
    image_name_no_extension=image_name.split(".")[0]

    #We have to make rename_image "True" to change the name of the image according
    #with our needs
    if rename_image:
        image_name = os.path.join(output,str(new_name)+'.png')
    else:
        image_name = os.path.join(output,image_name_no_extension+'.png')

    if image_ratio:
        image=image_ratio_cropping(image,ratio_width,ratio_height)


    #Horizontal rotation true will make the width of the image larger than the height.
    if horizontal_rotation:
        image=horizontal_rotation_function(image)

    #Vertical rotation true will make the height of the image larger than the width.
    if vertical_rotation:
        image=vertical_rotation_function(image)


    #Rotation and resizing options depending on the given information
    if resize:
        image=image_resizing(image,new_width,new_height)


    #save the frame
    print (image_name)
    cv2.imwrite(image_name,image)
    print (os.path.join('./all_'+str(new_width)+"_"+str(new_height),str(new_name)+'.png'))
    cv2.imwrite(os.path.join('./all_'+str(new_width)+"_"+str(new_height), str(new_name)+'.png'),image)


#Function to scan all the folder with videos and extract the frames.
def video_to_frame_folders(args):
    """
    args: args indications used in the command to run the code.
    """

    #List formats for images and videos.
    img_formats = ['bmp', 'jpg', 'jpeg', 'png', 'tif', 'tiff', 'dng', 'webp', 'JPG','JPEG','PNG']
    vid_formats = ['mov', 'avi', 'mp4', 'mpg', 'mpeg', 'm4v', 'wmv', 'mkv', 'MOV','MP4', 'AVI','MPG','MPEG']


    #printing statement to verify the number of fields
    print ('There are %s fields to scan' %str(len(args.fields.split(" "))))

    #make the directory where we are going to store "all" the new images.
    alternative_directory_save_new_data_all=os.path.join('./','all'+'_'+str(args.reshaped_width)+'_'+str(args.reshaped_height))

    os.makedirs(alternative_directory_save_new_data_all,exist_ok=True)

    #creation of dictionary to keep track of the characteristics of the extracted
    #video frames.
    video_frame_dictionary={}

    #Go through every field
    for field in args.fields.split(" "):

        #print statement to know where we are.
        print ('Going through all the videos in the field %s' %field)

        #make the directory where we are going to store the new images.
        alternative_directory_save_new_data=os.path.join('./',str(field)+'_'+str(args.reshaped_width)+'_'+str(args.reshaped_height))

        os.makedirs(alternative_directory_save_new_data,exist_ok=True)

        #printing statement to keep track
        print ('There are %s dates in the field %s' %(len(os.listdir(os.path.join('./',field))), str(field)))

        #access to the folders within the field directory, adn loop through them
        for date in os.listdir(os.path.join('./',field)):
            print ('Scanning the videos in ' + str(date))

            #Access to all the videos on that date and that field
            #path of the videos directory
            video_path=os.path.join('./',str(field),str(date),'videos')

            #Create a list for the paths of the video files we need to transfrom.
            video_files_paths=[]

            #Get all the video files in the directory of the field and date
            for video_extension in vid_formats:
                #Get the names of all the files within the video folder
                for file in os.listdir(video_path):
                    #Get the videos with a video file extension.
                    if file.endswith(video_extension):
                        video_files_paths.append(os.path.join(video_path,file))

            #Print the number of videos for that field and that specific date
            print ('There are %s videos in the recording at field' %(str(len(video_files_paths))),str(field))

            #create a folder to put the placed extracted images.
            save_frames_directory=os.path.join(alternative_directory_save_new_data,str(date),'videos')
            os.makedirs(save_frames_directory,exist_ok=True)

            #counter for the video naming. Each video will be associated with a
            #number. THis is to keep track of the videos.
            video_counter=0

            #Go through every video we have to extract the frames.
            for video_path in video_files_paths:
                #all the frames extracted from this video will have this name
                #in front of it.
                images_video_name=str(field)+'_'+str(date)+'_'+'v'+'_'+str(video_counter)

                #fill the entry in the dictionary to keep track of the characteristics
                #of the videos
                video_frame_dictionary[os.path.basename(video_path)]={
                'image_name':str(images_video_name),'field':str(field),
                'date':date}


                #extract all
                print ('normal')
                image_extraction_video(video_path,args.fpsinterval,save_frames_directory,
                                            resize=args.resize,horizontal_rotation=args.hrotation,
                                            vertical_rotation=args.vrotation,
                                            new_width=args.reshaped_width, new_height=args.reshaped_height,
                                            rename_videoframe=True, new_name=images_video_name)


                #video counter update
                video_counter = video_counter+1

                #printing statment to keep track of the progress.
                print ('Video %s modified; progress %s out of %s videos' %(video_path,str(video_counter),str(len(video_files_paths))))



    #Save the dictionary we have created to keep track of things.
    json_file= json.dumps(video_frame_dictionary)
    json_name="json_videos"+"_"+str(args.fields)+'_'+str(args.reshaped_width)+'_'+str(args.reshaped_height)+"dict.json"
    f = open(os.path.join(alternative_directory_save_new_data_all,json_name),"w")
    f.write(json_file)
    f.close()

    #save the json file in current directory
    f = open(os.path.join("./",json_name),"w")
    f.write(json_file)
    f.close()

#Function to scan all the folders with images. Then resize, rotate, and rename
#this images depending on our needs.
def image_modification(args):
    """
    args: args indications used in the command to run the code.
    """
    #List formats for images and videos.
    img_formats = ['bmp', 'jpg', 'jpeg', 'png', 'tif', 'tiff', 'dng', 'webp','JPG','JPEG','PNG']

    #printing statement to verify the number of fields
    print ('Images: There are %s fields to scan' %str(len(args.fields)))

    #make the directory where we are going to store "all" the "new" images.
    alternative_directory_save_new_data_all=os.path.join('./',
                'all'+'_'+str(args.reshaped_width)+'_'+str(args.reshaped_height))

    #creation of dictionary to keep track of the characteristics of the extracted
    #video frames.
    image_frame_dictionary={}

    #Go through every field.
    for field in args.fields.split(" "):

        #print statement to know where we are.
        print ('Going through all the images in the field %s' % field)

        #make the directory where we are going to store the new images.
        alternative_directory_save_new_data=os.path.join('./',
                    str(field)+'_'+str(args.reshaped_width)+'_'+str(args.reshaped_height))

        os.makedirs(alternative_directory_save_new_data,exist_ok=True)

        #printing statement to keep track
        print ('There are %s dates in the field %s' %(len(os.listdir(os.path.join('./',field))), str(field)))

        #access to the folders within the field directory, and loop through them
        for date in os.listdir(os.path.join('./',str(field))):
            #printing statement for safety// knowing what is going on.
            print ('Scanning the raw images  in ' + str(date))

            #Access to all the images on that date and that field
            #path of the videos directory
            images_path=os.path.join('./',str(field),str(date),'raw_images')

            #Print statement to verify correct development.
            print ('Scanning images in the s% directory '+str(images_path))

            #Create an empy file to store the image paths that we are going to modify
            image_files_paths=[]

            #Get all the video files in the directory of the field and date
            for img_extension in img_formats:
                #Get the names of all the files within the video folder
                for file in os.listdir(images_path):
                    #Get the videos with a video file extension.
                    if file.endswith(img_extension):
                        image_files_paths.append(os.path.join(images_path,file))

            #Print the number of images for that field and that specific date
            print ('There are %s images in the recordings ' + str(len(image_files_paths)))

            #create a folder to put the placed extracted images.
            save_frames_directory=os.path.join(alternative_directory_save_new_data,str(date),'raw_images')
            os.makedirs(save_frames_directory,exist_ok=True)

            #counter for the image naming. Each image will be associated with a number.
            #This is to keep track of the images.
            image_counter=0

            #Go through every video we have to extract the frames.
            for image_path in image_files_paths:
                #New image name
                image_name=str(field)+'_'+str(date)+'_'+'i'+'_'+str(image_counter)

                #fill the entry in the dictionary to keep track of the characteristics
                #of the images

                #extract all
                image_processing(image_path,save_frames_directory,resize=args.resize,
                                horizontal_rotation=args.hrotation,
                                vertical_rotation=args.vrotation,new_width=1980,
                                new_height=1080, rename_image=True,
                                new_name=image_name,image_ratio=True,
                                ratio_width=args.ratiolongside, ratio_height=args.ratioshortside)


                #update counter
                image_counter = image_counter+ 1

                #printing statment to keep track of the progress.
                print ('Image %s modified; progress %s out of %s images' %(image_path,str(image_counter),str(len(image_files_paths))))

    #Save the dictionary we have created to keep track of things.
    json_file= json.dumps(image_frame_dictionary)
    json_name="json_images"+"_"+str(args.fields)+'_'+str(args.reshaped_width)+'_'+str(args.reshaped_height)+"dict.json"
    f = open(os.path.join(alternative_directory_save_new_data_all,json_name),"w")
    f.write(json_file)
    f.close()

    #save the json file in current directory
    f = open(os.path.join("./",json_name),"w")
    f.write(json_file)
    f.close()

if __name__ == '__main__':

    #Parser to make this code work.
    parser = argparse.ArgumentParser()
    parser.add_argument('--video', type=str, default='image', help='initial image')
    parser.add_argument('--output', type=str, default='image', help='initial image')
    parser.add_argument('--fpsinterval', type=int, default=30, help='fps interval')
    parser.add_argument('--fields', type=str, default='bbro near30 walledgarden',
                        help='Name of the fields to transform the videos to images.')
    parser.add_argument('--reshaped_width', type=int, default=1920,
                        help='width of the retrieved images')
    parser.add_argument('--reshaped_height', type=int, default=1080,
                        help='height of the retrieved images')
    parser.add_argument('--resize', action='store_true', help='Save images horizontally')
    parser.add_argument('--hrotation', action='store_true', help='Save images horizontally')
    parser.add_argument('--vrotation', action='store_true', help='Save images vertically')
    parser.add_argument('--ratiolongside', type=int, default=16)
    parser.add_argument('--ratioshortside', type=int, default=9)

    args=parser.parse_args()

    #video_to_frame_folders(args)
    image_modification(args)
