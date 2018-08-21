#! /anaconda3/bin/python

import os.path
import shutil
from subprocess import call
import csv
import argh
import numpy as np
import cv2
import time
from skimage import io

def main(input_dir, par_th = 0.95, max_frame = 18000):
    print('start to read : '+input_dir)
    roi_file = input_dir + '/ROI_frame_splits.txt'
    orient_file = input_dir + '/corrected_orient.txt'

    path, folder = os.path.split(input_dir)
    if folder == 'analysis_output':
        path, folder = os.path.split(path)

    roi_list = list(csv.reader(open(roi_file, 'rt'), delimiter='\t'))
    orient_list = list(csv.reader(open(orient_file, 'rt'), delimiter='\t'))

    cap = None
    img_path = []
    img_lane = []
    side_name = []
    frame_info = []
    top_frames = []
    max_lane = -1
    for k in range(len(roi_list)):
        roi = int(roi_list[k][0])
        fstart = int(roi_list[k][1])
        fend = int(roi_list[k][2])
        lane_id = int(roi_list[k][3])
        new_lane = False

        # bug??
        if fstart==0 and fend==0:
            continue;

        #if roi==1 or roi==4:
        #    continue

        bottom_count = 0;
        for i in range(fstart, fend):
            if orient_list[i][lane_id] == '0':
                bottom_count = bottom_count + 1
        
        bottom_late = float(bottom_count) / (fend-fstart)

        side = 'top'
        if bottom_late < par_th:
            side = 'bad'

        if max_lane < lane_id:
            max_lane = lane_id
            new_lane = True

        print('process lane='+str(lane_id)+' fstart='+str(fstart)+' fend='+str(fend)+' rate='+str(bottom_late))

        if new_lane:
            if cap is not None:
                cap.release()
                cap = None
                frame_info.append(top_frames)

            # open avi
            cap = cv2.VideoCapture(input_dir+'/lane_'+str(lane_id)+'.avi')

            # make temporary frames
            top_path = 'tmp_'+folder+'_lane_'+str(lane_id)+'_top'
#            bad_path = 'tmp_'+folder+'_lane_'+str(lane_id)+'_bad'
            img_path.append(top_path)
#            img_path.append(bad_path)
            img_lane.append(lane_id)
#            img_lane.append(lane_id)
            side_name.append('top')
#            side_name.append('bad')
            if not os.path.exists(top_path):
                os.makedirs(top_path)
#            if not os.path.exists(bad_path):
#                os.makedirs(bad_path)
            tCount = 0
#            sCount = 0
            top_frames = []

#        continue

        tmp_path = 'tmp_'+folder+'_lane_'+str(lane_id)+'_'+side
        for i in range(fstart, fend):
            #Store this frame to an image
            if bottom_late >= par_th:
                cap.set(1,i);
                ret, frame = cap.read()
                io.imsave(f'{tmp_path}/ext_{tCount}.tif', frame)
                tCount = tCount+1
                crr_frame = [i,roi]
                top_frames.append(crr_frame)
                
#            else:
#                cap.set(1,i);
#                ret, frame = cap.read()
#                io.imsave(f'{tmp_path}/ext_{sCount}.tif', frame)
#                sCount = sCount+1

    # release object
    if cap is not None:
        cap.release()
        cap = None
        frame_info.append(top_frames)

    for i in range(len(img_path)):
        lane_id = img_lane[i]
        tmp_path = img_path[i]
        sname = side_name[i]
        csvdata = frame_info[i]
        video_output_path = os.path.join(input_dir, 'lane_'+str(lane_id)+'_'+sname+'byroi.avi')
        print('generage movie : '+video_output_path)
        call(['ffmpeg', '-y', '-i', f'{tmp_path}/ext_%d.tif', video_output_path])
        time.sleep(3)
        
        csv_output_path = os.path.join(input_dir, 'lane_'+str(lane_id)+'_'+sname+'byroi.txt')
        with open(csv_output_path, "wt") as csv_file:
            writer = csv.writer(csv_file, delimiter='\t')
            for line in csvdata:
                writer.writerow(line)

        shutil.rmtree(tmp_path)
        time.sleep(3)


if __name__ == '__main__':
    argh.dispatch_command(main)
