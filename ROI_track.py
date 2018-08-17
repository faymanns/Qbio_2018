"""
Class objects and functions to categorize fly in to various regions of 
interest within the walking assay.


Created by Nirag Kadakia at 12:00 08-14-2018
This work is licensed under the 
Creative Commons Attribution-NonCommercial-ShareAlike 4.0 
International License. 
To view a copy of this license, visit 
http://creativecommons.org/licenses/by-nc-sa/4.0/.
"""

import scipy as sp
import matplotlib.pyplot as plt
import json
import argh
import os


class classify_ROIs(object):
	"""
	Classify fly as being in particular region of interest in the assay.
	"""
	
	def __init__(self, mm_per_px, ROI_width, fps, min_ROI_sec, num_slots):
		"""
		Initialize class. 
		
		Parameters
		----------
		mm_per_px : float
			image resolution in mm per pixel
		ROI_width: float
			width of region of interest near wall or laser in mm
		fps: float
			recording rate in frames per second
		min_ROI_sec: float
			minimum dwell time in a given ROI; transitions shorter than this
			will not count as transitions.
		num_slots: int
			number of slots in walking arena
			
		"""
		
		
		# Number of slots in assay. 3 values for L, laser, and R, respectively.
		self.num_slots = num_slots
		self.pos_arr = sp.zeros((3, self.num_slots))
		
		# Minimum number of frames to count as a region-to-region transition
		self.min_ROI_frames = fps*min_ROI_sec
		
		# Width of near-wall zone in pixels
		self.ROI_width = ROI_width/mm_per_px
		
		# Bin edges for the ROIs. There are 6 ROIs in each slot.
		self.ROI_bins = sp.zeros((7, self.num_slots))
		
		# Construct data variables
		self.num_frames = None
		self.data = None
		
		# ROI nominal assignments
		self.raw_ROI = None
		self.corr_ROI = None
		self.ROI_splits = None
		
	def load_laser_wall_pos(self, in_dir):
		"""
		Set the x-position of the walls for each channel in the walking assay.
		
		Parameters
		----------
		in_dir : str
			Directory location of json file. Json file itself should be 
			named 'position.json', and is a dictionary with x keys, 
			slot_1,..., slot_x, each of which is a dictionary containing 3 
			keys, "right_wall", "laser", and "left_wall". The values of 
			each of these keys are floats representing the pixels.
		
		"""
		
		filename = os.path.join(in_dir, 'position.json')
		with open(filename, 'r') as fp:
			pos_dict = json.load(fp)
		
		for iS in range(self.num_slots):
			self.pos_arr[0, iS] = pos_dict['slot_%s' % iS]['left_wall']
			self.pos_arr[1, iS] = pos_dict['slot_%s' % iS]['laser']
			self.pos_arr[2, iS] = pos_dict['slot_%s' % iS]['right_wall']
		
		self.ROI_bins[0] = self.pos_arr[0]
		self.ROI_bins[1] = self.pos_arr[0] + self.ROI_width
		self.ROI_bins[2] = self.pos_arr[1] - self.ROI_width
		self.ROI_bins[3] = self.pos_arr[1] 
		self.ROI_bins[4] = self.pos_arr[1] + self.ROI_width
		self.ROI_bins[5] = self.pos_arr[2] - self.ROI_width
		self.ROI_bins[6] = self.pos_arr[2] 
	
	def load_centroid_data(self, in_dir):
		"""
		Set the centroid x-coordiantes from file. 
		
		Parameters
		----------
		in_dir : str
			Directory of centroid file. Centroid files are in txt format, one 
			for each slot. Files are named 'slot_1.avi_x.txt, ..., 
			slot_N.avi_x.txt'. Each is a 1D list with with N frames, 
			corresponding to the x-pos of the centroid for that slot.
		
		"""
		
		for iS in range(self.num_slots):
			filename = os.path.join(in_dir, 'lane_%s.avi_x.txt' % (iS))
			slot_data = sp.loadtxt(filename)
			
			if self.data is None:
				self.data = sp.zeros((len(slot_data), self.num_slots))
				self.num_frames = len(slot_data)			
			self.data[:, iS] = slot_data
		
		self.raw_ROI = sp.empty((self.num_frames, self.num_slots))
		self.corr_ROI = sp.zeros(self.data.shape)
			
	def ROI_nominal(self):
		"""
		Set the ROIs nominally from file, for each slot separately.
		"""
		
		for iS in range(self.num_slots):
			self.raw_ROI[:, iS] = sp.digitize(self.data[:, iS], 
									self.ROI_bins[:, iS]) - 1
			self.corr_ROI[:, iS] = self.raw_ROI[:, iS]
	
	def ROI_corrected(self):
		"""
		Correct ROI by incorporating minimum transition time
		"""
		
		for iS in range(self.num_slots):

			# Indices at which ROI changes
			splits = sp.nonzero(sp.diff(self.raw_ROI[:, iS]))[0]
			
			# For each of these transitions, check length for false transitions
			for iSplit in sp.arange(len(splits))[::-1]:
				
				# Frame-length of the current ROI
				split_beg = splits[iSplit - 1]
				split_end = splits[iSplit]
				split_len =  split_end - split_beg 
				
				# If ROI is too short, keep moving backward until you find an 
				# ROI of sufficient length (i.g. ROI > min_ROI_frames)
				split_shift = 0
				while split_len < self.min_ROI_frames:
					split_shift += 1
					
					# If at beginning of array; break the loop
					if iSplit - split_shift < 0: 
						break
					split_shift_beg = splits[iSplit - split_shift - 1]
					split_shift_end = splits[iSplit - split_shift]
					split_len = split_shift_end - split_shift_beg
				
				# Change all false regions back to ROI of sufficient length
				if split_shift > 0:
					frames_to_change = range(split_shift_end, split_end + 1)
					self.corr_ROI[frames_to_change, iS] = \
						self.raw_ROI[split_shift_end, iS]
	
	def get_ROI_splits(self):
		"""
		Get the frames corresponding to a beginning and end of an ROI.
		"""
		
		# The columns of ROI_splits are: ROI, beg idx, end idx, slot number
		self.ROI_splits = sp.zeros(4)
		
		for iS in range(self.num_slots):
			split_idxs = sp.nonzero(sp.diff(self.corr_ROI[:, iS]))[0]
			split_idxs = sp.hstack(([-1], split_idxs))
			if (self.num_frames - 1) not in split_idxs:
				split_idxs = sp.hstack((split_idxs, self.num_frames - 1))
			
			for iI in range(len(split_idxs) - 1):
				idx_beg = split_idxs[iI] + 1
				idx_end = split_idxs[iI + 1] + 1
				arr = [self.corr_ROI[idx_beg + 1, iS], idx_beg, idx_end, iS]
				self.ROI_splits = sp.vstack((self.ROI_splits.T, arr)).T
		self.ROI_splits = self.ROI_splits.astype(int)
		
	def save_data(self, out_dir):
		"""
		Output nominal and corrected data and ROI splits as txt files. The
		ROI_splits file is saved by row, where each row corresponnds to 
		a given snippet of the video in which the fly is in a unique ROI.
		The first column is the ROI (from {0, 6} as defined above), second 
		and third are the beg and end frame numbers of the snippet, and 
		last column is the slot number (up to num_slots).
		
		Parameters
		----------
		out_dir : str
			Directory of where to save data.
		
		"""
		
		nominal_output_path =  os.path.join(out_dir, 'nominal_ROIs.txt')
		corr_output_path =  os.path.join(out_dir, 'corrected_ROIs.txt')
		ROI_splits_path = os.path.join(out_dir, 'ROI_frame_splits.txt')
		with open(nominal_output_path, 'w') as fp:
			sp.savetxt(fp, self.raw_ROI, fmt='%d', delimiter='\t')
		with open(corr_output_path, 'w') as fp:
			sp.savetxt(fp, self.corr_ROI, fmt='%d', delimiter='\t')
		with open(ROI_splits_path, 'w') as fp:
			sp.savetxt(fp, self.ROI_splits.T, fmt='%d', delimiter='\t')
		
		
def main(in_dir, out_dir, mm_per_px=3./106, ROI_width=3.5, fps=60, 
			min_ROI_sec=0.25, num_slots=4):
	
	a = classify_ROIs(mm_per_px, ROI_width, fps, min_ROI_sec, num_slots)
	a.load_laser_wall_pos(in_dir)
	a.load_centroid_data(in_dir)
	a.ROI_nominal()
	a.ROI_corrected()
	a.get_ROI_splits()
	a.save_data(out_dir)
	
	
if __name__ == '__main__':
	argh.dispatch_command(main)