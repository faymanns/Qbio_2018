#! /anaconda3/bin/python

import os.path
import shutil
from subprocess import call
import numpy as np
import cv2
from skimage import io
import json
import csv
import argh
import datetime
import time

def hysteresis_filter(seq, n=5, n_false=None):
    """
    This function implements a hysteresis filter for boolean sequences.
    The state in the sequence only changes if n consecutive element are in a different state.

    Parameters
    ----------
    seq : 1D np.array of type boolean
        Sequence to be filtered.
    n : int, default=5
        Length of hysteresis memory.
    n_false : int, optional, default=None
        Length of hystresis memory applied for the false state.
        This means the state is going to change to false when it encounters
        n_false consecutive entries with value false.
        If None, the same value is used for true and false.

    Returns
    -------
    seq : 1D np.array of type boolean
        Filtered sequence.
    """
    if n_false is None:
        n_false = n
    seq = seq.astype(np.bool)
    state = seq[0]
    start_of_state = 0
    memory = 0

    current_n = n
    if state:
        current_n = n_false
    
    for i in range(len(seq)):
        if state != seq[i]:
            memory += 1
        elif memory < current_n:
            memory = 0
            continue
        if memory == current_n:
            seq[start_of_state:i - current_n + 1] = state
            start_of_state = i - current_n + 1
            state = not state
            if state:
                current_n = n_false
            else:
                current_n = n
            memory = 0
    seq[start_of_state:] = state
    return seq

def laser_position(path, start, stop):
    """
    This function computes the average position of the laser within a slot.

    Parameters
    ----------
    path : string
        Path to image file with laser on paper.
    start : int
        Index of first row belonging to slot.
    stop : int
        Index of the last row of the slot.

    Returns
    -------
    int
        Position of laser in pixels.
    """
    image = (io.imread(path) / np.iinfo(np.uint16).max * np.iinfo(np.uint8).max).astype(np.uint8)
    off_set = int(image.shape[1] / 2 - 100)
    image = image[:, off_set:off_set + 200]
    val, thresh = cv2.threshold(image, 0, np.iinfo(image.dtype).max, cv2.THRESH_OTSU)
    
    results = np.zeros(len(image))
    
    for i, row in enumerate(thresh):
        indices = np.nonzero(row)[0]
        if len(indices) == 0:
            continue
        results[i] = round((indices[-1] - indices[0]) / 2 + indices[0])
    
    return int(round(np.mean(results[start:stop]))) + off_set

def main(path_tif, path_laser_position, output_dir):
    """
    Main function for the first analysis step.
    Separates the different slots and finds the positions of the walls and the laser.

    Parameters
    ----------
    path_tif : string
        Path to tif stack with video frames.
    path_laser_position : string
        Path to image with laser position.
    output_dir : string
        Directory where output is stored.
    """
    print('start to read : '+path_tif)
    path = os.path.expanduser(os.path.expandvars(path_tif))
    full_video = io.imread(path)
    # if files were renamed it fails to automatically load all files
    if len(full_video) < 18000:
        full_video = np.concatenate((full_video, io.imread(path[:-8] + '_1.ome.tif')), axis=0)
    if len(full_video) < 18000:
        full_video = np.concatenate((full_video, io.imread(path[:-8] + '_2.ome.tif')), axis=0)
    if len(full_video) < 18000:
        full_video = np.concatenate((full_video, io.imread(path[:-8] + '_3.ome.tif')), axis=0)
    if len(full_video) < 18000:
        full_video = np.concatenate((full_video, io.imread(path[:-8] + '_4.ome.tif')), axis=0)
    assert len(full_video) >= 18000
        
    
    average_thresh_image = np.zeros_like(full_video[0])
    average_image = np.zeros_like(full_video[0])
    
    for i,frame in enumerate(full_video):
        if i % 100 == 0:
            print(i)
        #thresh = cv2.threshold(frame, 0, 65535, cv2.THRESH_OTSU)
        thresh = cv2.threshold(frame, 28000, np.iinfo(frame.dtype).max, cv2.THRESH_BINARY)
        #io.imsave(f'thresh{i}.tif', thresh[1])
        average_thresh_image += thresh[1]
        #average_image += frame
    
    average_thresh_image = average_thresh_image / len(full_video)
    #average_image = average_image / len(full_video)
    average_image = np.mean(full_video, axis=0)
    #io.imsave('result.tif', average_thresh_image.astype(np.uint16))
    
    bool_rows = np.any(average_thresh_image, axis=1)
    bool_rows = hysteresis_filter(bool_rows, 50, 1)
    
    lanes = []
    new_lane = True
    for i,b in enumerate(bool_rows):
        if new_lane and b:
            lanes.append(i-1)
            new_lane = False
        elif not new_lane and not b:
            lanes.append(i)
            new_lane = True
    if len(lanes) == 7:
        lanes.append(len(bool_rows))
    print(lanes)
    with open(os.path.join(output_dir,'lanes.csv'), 'w') as fp:
        wr = csv.writer(fp, quoting=csv.QUOTE_ALL)
        wr.writerow(lanes)
    
    assert len(lanes) == 8
    now = datetime.datetime.now()
    unix = str(int(time.mktime(now.timetuple())))
    frame_path = 'frames' + unix
    if not os.path.exists(frame_path):
        os.makedirs(frame_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    for i in range(0, len(lanes)-1, 2):
        lane_id = int(i/2)
        #io.imsave(f'lane{lane_id}.tif', full_video[:, lanes[i]:lanes[i+1], :])
        for j,img in enumerate(full_video[:, lanes[i]:lanes[i+1], :]):
            io.imsave(f'{frame_path}/lane_{lane_id}_frame_{j}.tif', img)
        video_output_path = os.path.join(output_dir, f'lane_{lane_id}.avi')
        call(['ffmpeg', '-y', '-i', f'{frame_path}/lane_{lane_id}_frame_%d.tif', video_output_path])
    shutil.rmtree(frame_path)
    
    position = {'slot_0': {}, 'slot_1': {}, 'slot_2': {}, 'slot_3': {}}
    path_laser_position = os.path.expanduser(os.path.expandvars(path_laser_position))

    for i in [0, 1, 2, 3]:
        #io.imsave(f'average_imgage_lane_{i}.tif', average_image[lanes[i * 2] : lanes[i * 2 + 1]].astype(np.uint16))
        #io.imsave(f'soblex_{i}.tif', cv2.Sobel(average_image[lanes[i *2] : lanes[i * 2 +1]], cv2.CV_16U, 1, 0, ksize=5))
        left_average_image =  average_image[lanes[i *2] : lanes[i * 2 +1], :40].astype(np.uint16) / np.iinfo(np.uint16).max * np.iinfo(np.uint8).max
        right_average_image = average_image[lanes[i *2] : lanes[i * 2 +1], -40:].astype(np.uint16) / np.iinfo(np.uint16).max * np.iinfo(np.uint8).max
        left_average_image = left_average_image.astype(np.uint8)
        right_average_image = right_average_image.astype(np.uint8)
        #io.imsave(f'left_average_image_{i}.tif', left_average_image)
        #io.imsave(f'right_average_image_{i}.tif', right_average_image)
        ret, left_wall_thresh_image = cv2.threshold(left_average_image, 0, np.iinfo(left_average_image.dtype).max, cv2.THRESH_OTSU)
        ret, right_wall_thresh_image = cv2.threshold(right_average_image, 0, np.iinfo(right_average_image.dtype).max, cv2.THRESH_OTSU)
        #io.imsave(f'left_wall_thresh_image_{i}.tif', left_wall_thresh_image)
        #io.imsave(f'right_wall_thresh_image_{i}.tif', right_wall_thresh_image)
        mid_col_num = int((lanes[i * 2 + 1] - lanes[i * 2]) / 2) # int(np.mean([lanes[i * 2], lanes[i * 2 + 1]]))
        left_slot_col_num = np.argwhere(left_wall_thresh_image[mid_col_num]>0)
        right_slot_col_num = np.argwhere(right_wall_thresh_image[mid_col_num]>0)
        position[f'slot_{i}']['left_wall'] = int(left_slot_col_num[0])
        position[f'slot_{i}']['right_wall'] = int(right_slot_col_num[-1] + average_image.shape[1] - 40)
        position[f'slot_{i}']['laser'] = laser_position(path_laser_position, lanes[i * 2], lanes[i * 2 + 1])
    
    position_output_path = os.path.join(output_dir, 'position.json')
    with open(position_output_path, 'w') as fp:
        json.dump(position, fp, sort_keys=True, indent=4)


if __name__ == '__main__':
    argh.dispatch_command(main)
