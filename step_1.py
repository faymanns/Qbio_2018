import os.path
import numpy as np
import cv2
from skimage import io

#path = os.path.expanduser(os.path.expandvars('~/Desktop/R38B08R81E10_0_5mW_1_1.tif'))
path = os.path.expanduser(os.path.expandvars('~/Desktop/sample_input.tif'))
full_video = io.imread(path)
#print(full_video.dtype)
# print(len(full_video))

average_image = np.zeros_like(full_video[0])

for i,frame in enumerate(full_video):
    #thresh = cv2.threshold(frame, 0, 65535, cv2.THRESH_OTSU)
    thresh = cv2.threshold(frame, 25000, 65535, cv2.THRESH_BINARY)
    #print(thresh[0])
    #io.imsave(f'thresh{i}.tif', thresh[1])
    average_image += thresh[1]

average_image = average_image / len(full_video)
print(average_image)
io.imsave('result.tif', average_image.astype(np.uint16))
