#! /anaconda3/bin/python

import os.path
import shutil
from subprocess import call
import csv
import argh
import numpy as np
import cv2
from skimage import io

def main(input_dir, max_frame = 18000):
    print('start to read : '+input_dir)
    roi_file = input_dir + '/corrected_ROIs.txt'
    orient_file = input_dir + '/corrected_orient.txt'

    roi_list = list(csv.reader(open(roi_file, 'rt'), delimiter='\t'))
    orient_list = list(csv.reader(open(orient_file, 'rt'), delimiter='\t'))

    
    
    
    frame_seq = 749
    

    for lane_id in range(len(roi_list[0])):
        print('start to process lane :'+str(lane_id))
        
        # open avi
        cap = cv2.VideoCapture(input_dir+'/lane_'+str(lane_id)+'.avi')
        
        # make temporary frames
        
        if os.path.exists('tmpframes'):
            shutil.rmtree('tmpframes')
        os.makedirs('tmpframes')

        j = 0
        for i in range(len(roi_list)):
            if i % 100 == 0:
                print('frame: '+str(i))
            roi = int(roi_list[i][lane_id])
            orient = int(orient_list[i][lane_id])
            
            if orient==0 and (roi==0 or roi==2 or roi==3 or roi==5):
                frame_no = (i / max_frame)
                cap.set(1,i);
                ret, frame = cap.read()

                #Store this frame to an image
                #cv2.imwrite('tmpframes/ext_'+str(i)+'.jpg', frame)
                io.imsave(f'tmpframes/ext_{j}.tif', frame)
                j = j + 1

        video_output_path = os.path.join(input_dir, f'lane_{lane_id}_top.avi')
        call(['ffmpeg', '-y', '-i', f'tmpframes/ext_%d.tif', video_output_path])
        shutil.rmtree('tmpframes')


if __name__ == '__main__':
    argh.dispatch_command(main)
