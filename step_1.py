import os.path
import shutil
from subprocess import call
import numpy as np
import cv2
from skimage import io
import json

def hysteresis_filter(seq, n=5):
    """
    This function implements a hysteresis filter for boolean sequences.
    The state in the sequence only changes if n consecutive element are in a different state.

    Parameters
    ----------
    seq : 1D np.array of type boolean
        Sequence to be filtered.
    n : int, default=5
        Length of hysteresis memory.

    Returns
    -------
    seq : 1D np.array of type boolean
        Filtered sequence.
    """
    seq = seq.astype(np.bool)
    state = seq[0]
    start_of_state = 0
    memory = 0
    for i in range(len(seq)):
        if state != seq[i]:
            memory += 1
        elif memory < n:
            memory = 0
            continue
        if memory == n:
            seq[start_of_state:i-n+1]=state
            start_of_state = i-n+1
            state = not state
            memory = 0
    seq[start_of_state:]=state
    return seq

def laser_position(path, start, stop):
    image = io.imread(path)
    val, thresh = cv2.threshold(image, 0, np.iinfo(image.dtype).max, cv2.THRESH_OTSU)
    
    results = np.zeros(len(image))
    
    for i, row in enumerate(thresh):
        indices = np.nonzero(row)[0]
        results[i] = round((indices[-1] - indices[0]) / 2 + indices[0])
    
    return int(round(np.mean(results[start:stop])))

path = os.path.expanduser(os.path.expandvars('sample_input.tif'))
full_video = io.imread(path)

average_image = np.zeros_like(full_video[0])

for i,frame in enumerate(full_video):
    #thresh = cv2.threshold(frame, 0, 65535, cv2.THRESH_OTSU)
    thresh = cv2.threshold(frame, 25000, 65535, cv2.THRESH_BINARY)
    #io.imsave(f'thresh{i}.tif', thresh[1])
    average_image += thresh[1]

average_image = average_image / len(full_video)
#io.imsave('result.tif', average_image.astype(np.uint16))

bool_rows = np.any(average_image, axis=1)
bool_rows = hysteresis_filter(bool_rows, 4)

lanes = []
new_lane = True
for i,b in enumerate(bool_rows):
    if new_lane and b:
        lanes.append(i-1)
        new_lane = False
    elif not new_lane and not b:
        lanes.append(i)
        new_lane = True
print(lanes)
if not os.path.exists('frames'):
    os.makedirs('frames')
for i in range(0, len(lanes)-1, 2):
    lane_id = int(i/2)
    #io.imsave(f'lane{lane_id}.tif', full_video[:, lanes[i]:lanes[i+1], :])
    for j,img in enumerate(full_video[:, lanes[i]:lanes[i+1], :]):
        io.imsave(f'frames/lane_{lane_id}_frame_{j}.tif', img)
    call(['ffmpeg', '-y', '-i', f'frames/lane_{lane_id}_frame_%d.tif', f'lane_{lane_id}.avi'])
shutil.rmtree('frames')


wall_col_num = []
laser_col_num = []
position = {'slot_0': {}, 'slot_1': {}, 'slot_2': {}, 'slot_3': {}}
for i in [0, 1, 2, 3]:
    mid_col_num = int(np.mean([lanes[i * 2], lanes[i * 2 + 1]]))
    slot_col_num = np.argwhere(average_image[mid_col_num]>0)
    position[f'slot_{i}']['left_wall'] = int(slot_col_num[0]-1)
    position[f'slot_{i}']['right_wall'] = int(slot_col_num[-1]+1)
    position[f'slot_{i}']['laser'] = laser_position('laserposition_paper.jpg', lanes[i * 2], lanes[i * 2 + 1])

with open('position.json', 'w') as fp:
    json.dump(position, fp, sort_keys=True, indent=4)
