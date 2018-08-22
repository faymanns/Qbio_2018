"""
Get the number of touches while near wall or while near the laser wall.

Created by Nirag Kadakia at 18:00 08-21-2018
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
from detect_peaks import detect_peaks

class postures(object):
	"""
	Classify fly as being in particular region of interest in the assay.
	"""
	
	def __init__(self, genotype, mm_per_px, fps, num_slots):
		"""
		Initialize class. 
		
		Parameters
		----------
		mm_per_px : float
			image resolution in mm per pixel
		fps: float
			recording rate in frames per second
		num_slots: int
			number of slots in walking arena
			
		"""
		
		if genotype is None:
			self.genotypes = ['empty_0.5mW', 'empty_1.5mW', 'iav_0.5mW', 'iav_1.5mW',
						'ppk_0.5mW', 'ppk_1.5mW', 'R14F05_0.5mW', 
						'R14F05_1.5mW', 'R38B08R81E10_0.5mW', 
						'R38B08R81E10_1.5mW', 'R48A07_0.5mW', 'R48A07_1.5mW', 
						'R86D09_0.5mW', 'R86D09_1.5mW', 'stum_0.5mW', 
						'stum_1.5mW']				
		else:
			self.genotypes = [genotype]
			
		self.num_slots = num_slots
		self.pos_arr = sp.zeros((3, self.num_slots))
		self.laser_L_splits = None
		self.laser_R_splits = None
		self.wall_L_splits = None
		self.wall_R_splits = None
		
		self.ROI_switch_idxs = None
		self.frm_ROI = None
		
		# Construct data variables
		self.num_frames = None
		self.Tt = None
		self.fps = fps
		self.mm_per_px = mm_per_px
		self.data = None
		self.DLC_data = None
	
	def get_all_dirs(self, in_dir, genotype):
		"""
		Get all directories in the analysis output directory corresponding 
		to the desired genotype. All directories containing genotype will
		be appended to dirs_to_analyze.
		
		Parameters
		----------
		in_dir: str
			analysis directory.
		genotype: str
			genotype or experimental line (e.g `empty_1.5mW')
		
		"""
	
		all_dirs = next(os.walk(in_dir))[1]
		self.dirs_to_analyze = []
		for dir in all_dirs:
			if genotype in dir:
				full_dir = os.path.join(in_dir, dir)
				self.dirs_to_analyze.append(full_dir)
				
		
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
		
		for iL in range(self.num_slots):
			self.pos_arr[0, iL] = pos_dict['slot_%s' % iL]['left_wall']
			self.pos_arr[1, iL] = pos_dict['slot_%s' % iL]['laser']
			self.pos_arr[2, iL] = pos_dict['slot_%s' % iL]['right_wall']
	
	def load_DLC(self, dir, lane):
		"""
		Load DeepLabCut data.
		
		Parameters
		----------
		
		lane: int
			lane number of walking arena; prob from 0 to 4.
		dir: str
			directory of exp data csv from DLC
		
		"""
		
		DLC_dir = os.path.join(os.path.dirname(dir), '_DLC')
		filename = os.path.join(DLC_dir, '%s_lane_%d_topbyroi.csv' 
								% (os.path.basename(dir), lane))
		self.DLC_data = sp.loadtxt(open(filename, "rb"), delimiter=",", 
									skiprows=3)
		
	def load_frame_ROI(self, in_dir, lane):
		"""
		Load the frame and ROI data. 
		
		Parameters
		----------
		
		lane: int
			lane number of walking arena; prob from 0 to 4.
		dir: str
			directory of exp data csv from DLC
		
		"""
		
		filename = os.path.join(in_dir, 'lane_%s_topbyroi.txt' % lane)
		with open(filename, 'r') as fp:
			self.frm_ROI = sp.loadtxt(fp)
		self.ROI_switch_idxs = sp.where(sp.diff(self.frm_ROI[:, 1]) != 0)[0]
		
	def get_frame_ranges(self):
		"""
		Get the frame ranges of the frames near laser or wall.
		"""
		
		# Get frames ranges of laser and wall proximal reagions
		self.laser_L_splits = []
		self.laser_R_splits = []
		self.wall_L_splits = []
		self.wall_R_splits = []
		for iC in range(len(self.ROI_switch_idxs[:-1])):
			beg_idx = self.ROI_switch_idxs[iC] + 1
			end_idx = self.ROI_switch_idxs[iC + 1]
			if self.frm_ROI[beg_idx, 1] == 2:
				if (self.frm_ROI[end_idx + 1, 1] == 1):
					self.laser_L_splits.append(sp.arange(beg_idx, end_idx))
			elif self.frm_ROI[beg_idx, 1] == 3:
				if (self.frm_ROI[end_idx + 1, 1] == 4):
					self.laser_R_splits.append(sp.arange(beg_idx, end_idx))
			elif self.frm_ROI[beg_idx, 1] == 0:
				self.wall_L_splits.append(sp.arange(beg_idx, end_idx))
			elif self.frm_ROI[beg_idx, 1] == 5:
				self.wall_R_splits.append(sp.arange(beg_idx, end_idx))
			else:
				pass
		
	def smooth(self, arr, window_T=1.0):
		"""
		Smooth a position trace with box average.
		
		Parameters
		----------
		
		arr: 1D array
			array to be smoothed.
		window_T: float
			length of box filter in seconds.
			
		"""
		
		# Box smooth in window of window_T
		smooth_frames = int(1.*self.fps*window_T)
		smoothed_data = sp.zeros(len(arr))
		smoothing_window = sp.arange(-smooth_frames, smooth_frames)
		for iN in smoothing_window:
			smoothed_data += sp.roll(arr, iN)
		smoothed_data = smoothed_data/len(smoothing_window)
			
		return smoothed_data

	def save_touches(self, dir, lane, name):
		"""
		Save the traces and statistics of wall and laser touches.
		
		Parameters
		----------
		
		lane: int
			lane number of walking arena; prob from 0 to 4.
		dir: str
			directory of exp data csv from DLC
		name: str
			Name of posture (left leg, etc.)
			
		"""
		
		plt.xlabel('Time (s)', fontsize=22)
		plt.ylabel('Distance (mm)', fontsize=22)
		plt.xticks(fontsize=18)
		plt.yticks(fontsize=18)
		plt.ylim(-1, 25)
		
		plots_dir = os.path.join(os.path.dirname(dir), '_touches')
		filename = os.path.join(plots_dir, '%s_%s_lane_%d.png' 
								% (os.path.basename(dir), name, lane))
		plt.tight_layout()
		plt.savefig(filename)
		filename = os.path.join(plots_dir, '%s_%s_lane_%d.svg' 
								% (os.path.basename(dir), name, lane))
		plt.tight_layout()
		plt.savefig(filename)
		plt.close()
	
	def get_touches(self, dir, lane, smoothing_dt=0.15, min_peak_sep=0.5, dwall=1):
		"""
		Get number of touches on wall or laser per ROI entrance.
		
		Parameters
		----------
		
		lane: int
			lane number of walking arena; prob from 0 to 4.
		dir: str
			directory of exp data csv from DLC
		smoothing_dt: float
			length of box window smoother in seconds
		min_peak_sep: float
			length of minimum separation between peaks, in seconds
		dwall: float
			distance from wall or laser that counts as a touch, in mm
			
		"""
		
		mpd = int(min_peak_sep*self.fps)
		dw = int(dwall/self.mm_per_px)
		
		posture_names = ['right_leg', 'left_leg']
		R_leg_tip_x = self.smooth(self.DLC_data[:, 22], window_T=smoothing_dt)
		L_leg_tip_x = self.smooth(self.DLC_data[:, 1], window_T=smoothing_dt)
		posture_list = [R_leg_tip_x, L_leg_tip_x]
		
		L_wall_pos = self.pos_arr[0, lane]
		laser_pos = self.pos_arr[1, lane]
		R_wall_pos = self.pos_arr[2, lane]
		
		
		fig = plt.figure()
		fig.set_size_inches(8, 4)
		for iP, arr in enumerate(posture_list):
			
			# Left wall approach
			for iS in range(len(self.wall_L_splits)):
				iRange = self.wall_L_splits[iS]
				hits = detect_peaks(arr[iRange], mpd=mpd, mph=-1e3, valley=1)
				
				# Add number of hits
				num_hits = 0
				for idx in hits:
					if abs(arr[idx + iRange[0]] - L_wall_pos) < dw:
						num_hits += 1
						Tt = 1.*(idx + iRange[0])/self.fps
						plt.scatter(Tt, arr[idx + iRange[0]]*self.mm_per_px, c='r')
				self.num_wall_hits[iP].append(num_hits)
			
			# Right wall approach (hits)
			for iS in range(len(self.wall_R_splits)):
				iRange = self.wall_R_splits[iS]
				hits = detect_peaks(arr[iRange], mpd=mpd, mph=R_wall_pos - dw)
				num_hits = 0
				for idx in hits:
					if abs(arr[idx + iRange[0]] - R_wall_pos) < dw:
						num_hits += 1
						Tt = 1.*(idx + iRange[0])/self.fps
						plt.scatter(Tt, arr[idx + iRange[0]]*self.mm_per_px, c='r')
				self.num_wall_hits[iP].append(num_hits)
			
			# Left laser approach			
			for iS in range(len(self.laser_L_splits)):
				iRange = self.laser_L_splits[iS]
				hits = detect_peaks(arr[iRange], mpd=mpd, mph=laser_pos - dw)
				num_hits = 0
				for idx in hits:
					if abs(arr[idx + iRange[0]] - laser_pos) < dw:
						num_hits += 1
						Tt = 1.*(idx + iRange[0])/self.fps
						plt.scatter(Tt, arr[idx + iRange[0]]*self.mm_per_px, c='b')
				self.num_laser_hits[iP].append(num_hits)
					
			# Right laser approach
			for iS in range(len(self.laser_R_splits)):
				iRange = self.laser_R_splits[iS]
				hits = detect_peaks(arr[iRange], mpd=mpd, mph=-1e3, valley=1)
				num_hits = 0
				for idx in hits:
					if abs(arr[idx + iRange[0]] - laser_pos) < dw:
						num_hits += 1
						Tt = 1.*(idx + iRange[0])/self.fps
						plt.scatter(Tt, arr[idx + iRange[0]]*self.mm_per_px, c='b')
				self.num_laser_hits[iP].append(num_hits)
			plt.plot(sp.arange(self.DLC_data.shape[0])/self.fps, 
						arr*self.mm_per_px, c='k')	
			plt.axhline(laser_pos*self.mm_per_px, linestyle='--')
			plt.axhline(L_wall_pos*self.mm_per_px, linestyle='--')
			plt.axhline(R_wall_pos*self.mm_per_px, linestyle='--')
			self.save_touches(dir, lane, posture_names[iP])
			
			
def main(in_dir, genotype=None, mm_per_px=3./106, fps=60, num_slots=4):
	
	a = postures(genotype, mm_per_px, fps, num_slots)
	for genotype in a.genotypes:
		a.get_all_dirs(in_dir, genotype)
		if len(a.dirs_to_analyze) == 0:
			print ('Nothing loaded for genotype %s' % genotype)
			continue
		
		# This is a list, each entry of which is the number of hits in ROI
		a.num_laser_hits = [[] for i in range(2)]
		a.num_wall_hits = [[] for i in range(2)]
		
		# For each dir of genotype, load laser pos, DLC data, frame/orient data
		for dir in a.dirs_to_analyze:
			a.load_laser_wall_pos(dir)
			
			# For each slot, different file; load sequentially
			for iL in range(a.num_slots):
				try:
					a.load_DLC(dir, iL)
				except FileNotFoundError:
					print ('%s_lane_%s_topbyroi.csv not found' % (iL, dir))
					continue
				try:
					a.load_frame_ROI(dir, iL)
				except FileNotFoundError:
					print ('lane_%s_topbyroi.txt not found' % dir)
					continue
				a.get_frame_ranges()
				a.get_touches(dir, iL)
				
if __name__ == '__main__':
	argh.dispatch_command(main)