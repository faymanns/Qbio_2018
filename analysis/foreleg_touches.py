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
			self.genotypes = ['empty_0.5mW', 'empty_1.5mW', 'iav_0.5mW', 
						'iav_1.5mW', 'ppk_0.5mW', 'ppk_1.5mW', 'R14F05_0.5mW',
						'R14F05_1.5mW', 'R38B08R81E10_0.5mW', 
						'R38B08R81E10_1.5mW', 'R48A07_0.5mW', 'R48A07_1.5mW', 
						'R86D09_0.5mW', 'R86D09_1.5mW', 'stum_0.5mW', 
						'stum_1.5mW']				
			#self.genotypes = ['R14F05_0.5mW', 'R48A07_0.5mW', 
			#self.genotypes = ['R38B08R81E10_0.5mW', 'ppk_0.5mW']
			
			
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
		self.num_postures = 2
		self.posture_names = ['right_leg', 'left_leg']
		
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
		Save the traces of wall and laser touches.
		
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
		
		plots_dir = os.path.join(os.path.dirname(dir), '_postures')
		filename = os.path.join(plots_dir, '%s_%s_lane_%d.png' 
								% (os.path.basename(dir), name, lane))
		plt.tight_layout()
		plt.savefig(filename)
		filename = os.path.join(plots_dir, '%s_%s_lane_%d.svg' 
								% (os.path.basename(dir), name, lane))
		plt.tight_layout()
		plt.savefig(filename)
		plt.close()
	
	def get_touches(self, dir, lane, smoothing_dt=0.15, peak_sep=0.5, dwall=1):
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
		peak_sep: float
			length of minimum separation between peaks, in seconds
		dwall: float
			distance from wall or laser that counts as a touch, in mm
			
		"""
		
		mpd = int(peak_sep*self.fps)
		dw = int(dwall/self.mm_per_px)
		
		# Two postures to track (left and right leg); change this in __init__
		R_leg_tip_x = self.smooth(self.DLC_data[:, 1], window_T=smoothing_dt)
		L_leg_tip_x = self.smooth(self.DLC_data[:, 22], window_T=smoothing_dt)
		
		# Need y's for each posture
		R_leg_tip_y = self.smooth(self.DLC_data[:, 2], window_T=smoothing_dt)
		L_leg_tip_y = self.smooth(self.DLC_data[:, 23], window_T=smoothing_dt)
		
		posture_xlist = [R_leg_tip_x, L_leg_tip_x]
		posture_ylist = [R_leg_tip_y, L_leg_tip_y]
		
		# Wall and laser positions
		L_wall_pos = self.pos_arr[0, lane]
		laser_pos = self.pos_arr[1, lane]
		R_wall_pos = self.pos_arr[2, lane]
		
		# Get number of touches and x,y positions for each ROI, for wall/laser
		fig = plt.figure()
		fig.set_size_inches(8, 4)
		for iP, arr in enumerate(posture_xlist):
			
			posture_x = posture_xlist[iP]
			posture_y = posture_ylist[iP]
			
			# Left wall approach
			for iS in range(len(self.wall_L_splits)):
				iRange = self.wall_L_splits[iS]
				if iRange[-1] > len(arr) - 1:
					continue
				hits = detect_peaks(arr[iRange], mpd=mpd, mph=-1e3, valley=1)
				num_hits = 0
				for idx in hits:
					if abs(arr[idx + iRange[0]] - L_wall_pos) < dw:
						num_hits += 1
						frame = idx + iRange[0]
						self.wall_xs[iP].append(posture_x[frame]/self.fps)
						self.wall_ys[iP].append(posture_y[frame]/self.fps)
						plt.scatter(1.*frame/self.fps, 
									posture_x[frame]*self.mm_per_px, c='r')
				self.num_wall_hits[iP].append(num_hits)
			
			# Right wall approach 
			for iS in range(len(self.wall_R_splits)):
				iRange = self.wall_R_splits[iS]
				if iRange[-1] > len(arr) - 1:
					continue
				hits = detect_peaks(arr[iRange], mpd=mpd, mph=R_wall_pos - dw)
				num_hits = 0
				for idx in hits:
					if abs(arr[idx + iRange[0]] - R_wall_pos) < dw:
						num_hits += 1
						frame = idx + iRange[0]
						self.wall_xs[iP].append(posture_x[frame]/self.fps)
						self.wall_ys[iP].append(posture_y[frame]/self.fps)
						plt.scatter(1.*frame/self.fps, 
									posture_x[frame]*self.mm_per_px, c='r')
				self.num_wall_hits[iP].append(num_hits)
			
			# Left laser approach			
			for iS in range(len(self.laser_L_splits)):
				iRange = self.laser_L_splits[iS]
				if iRange[-1] > len(arr) - 1:
					continue
				hits = detect_peaks(arr[iRange], mpd=mpd, mph=laser_pos - dw)
				num_hits = 0
				for idx in hits:
					if abs(arr[idx + iRange[0]] - laser_pos) < dw:
						num_hits += 1
						frame = idx + iRange[0]
						self.laser_xs[iP].append(posture_x[frame]/self.fps)
						self.laser_ys[iP].append(posture_y[frame]/self.fps)
						plt.scatter(1.*frame/self.fps, 
									posture_x[frame]*self.mm_per_px, c='b')
				self.num_laser_hits[iP].append(num_hits)
					
			# Right laser approach
			for iS in range(len(self.laser_R_splits)):
				iRange = self.laser_R_splits[iS]
				if iRange[-1] > len(arr) - 1:
					continue
				hits = detect_peaks(arr[iRange], mpd=mpd, mph=-1e3, valley=1)
				num_hits = 0
				for idx in hits:
					if abs(arr[idx + iRange[0]] - laser_pos) < dw:
						num_hits += 1
						frame = idx + iRange[0]
						self.laser_xs[iP].append(posture_x[frame]/self.fps)
						self.laser_ys[iP].append(posture_y[frame]/self.fps)
						plt.scatter(1.*frame/self.fps, 
									posture_x[frame]*self.mm_per_px, c='b')
				self.num_laser_hits[iP].append(num_hits)
			
			# Plot the full trace and save to check by eye
			plt.plot(sp.arange(self.DLC_data.shape[0])/self.fps, 
						arr*self.mm_per_px, c='k')	
			plt.axhline(laser_pos*self.mm_per_px, linestyle='--')
			plt.axhline(L_wall_pos*self.mm_per_px, linestyle='--')
			plt.axhline(R_wall_pos*self.mm_per_px, linestyle='--')
			self.save_touches(dir, lane, self.posture_names[iP])
	
	def plot_num_touches_per_ROI(self, in_dir, genotype):
		"""
		Plot the number of touches per ROI, average and sem.
		
		Parameters
		----------
		
		in_dir: str
			directory of data 
		genotyp: str
			genotype to be saved and plotted.
			
		"""
		
		fig = plt.figure()
		fig.set_size_inches(2, 4.0)
		for iP in range(self.num_postures):
			avg = sp.average(self.num_wall_hits[iP])
			sem = sp.std(self.num_wall_hits[iP])/\
							len(self.num_wall_hits[iP])**0.5
			plt.errorbar(iP/2.0, avg, sem, color=plt.cm.Blues(0.4 + 
							iP/(self.num_postures)), lw = 3, capsize=4)
			avg = sp.average(self.num_laser_hits[iP])
			sem = sp.std(self.num_laser_hits[iP])/\
							len(self.num_laser_hits[iP])**0.5
			plt.errorbar(1 + iP/2.0, avg, sem, color=plt.cm.Reds(0.4
							+ iP/(self.num_postures)), capsize=4, lw=3)
		plt.xticks([0, 0.5, 1, 1.5], ['R foreleg', 'L foreleg', 
					'R foreleg', 'L foreleg'], rotation=90)
		plt.ylim(0, 3)
		plots_dir = os.path.join(in_dir, '_postures')
		filename = os.path.join(plots_dir, '_num_touches', '%s.svg' % genotype)
		plt.tight_layout()
		plt.savefig(filename)
		filename = os.path.join(plots_dir, '_num_touches', '%s.png' % genotype)
		plt.savefig(filename)
		plt.close()
		
	def plot_xy_data(self, in_dir, genotype):
		"""
		"""
		
		plots_dir = os.path.join(in_dir, '_postures')
		
		for iP, posture in enumerate(self.posture_names):
			filename = os.path.join(plots_dir, '_xys', '%s_laser_x_%s.txt' 
									% (genotype, posture))
			sp.savetxt(filename, self.laser_xs[iP])
			filename = os.path.join(plots_dir, '_xys', '%s_laser_y_%s.txt' 
									% (genotype, posture))
			sp.savetxt(filename, self.laser_ys[iP])
			filename = os.path.join(plots_dir, '_xys', '%s_wall_x_%s.txt' 
									% (genotype, posture))
			sp.savetxt(filename, self.wall_xs[iP])
			filename = os.path.join(plots_dir, '_xys', '%s_wall_y_%s.txt' 
									% (genotype, posture))
			sp.savetxt(filename, self.wall_ys[iP])
		
		# Plot wall y-distribution; aggregate all postures (L and R leg)
		wall_data = []
		laser_data = []
		for iP in range(len(self.posture_names)):
			wall_data.extend(self.wall_ys[iP])
			laser_data.extend(self.laser_ys[iP])
		
		filename = os.path.join(plots_dir, '_xys', '%s_y_hist.png' % genotype)
		hist, bins = sp.histogram(wall_data, bins=sp.linspace(0, 2.1, 20), 
									density=True)
		fig = plt.figure()
		fig.set_size_inches(3, 3)
		plt.plot(bins[:-1], hist, color='b')
		hist, bins = sp.histogram(laser_data, bins=sp.linspace(0, 2.1, 20), 
									density=True)
		plt.plot(bins[:-1], hist, color='r')
		plt.tight_layout()
		plt.savefig(filename)
			
		
def main(in_dir, genotype=None, mm_per_px=3./106, fps=60, num_slots=4):
	
	a = postures(genotype, mm_per_px, fps, num_slots)
	for genotype in a.genotypes:
		a.get_all_dirs(in_dir, genotype)
		
		if len(a.dirs_to_analyze) == 0:
			print ('Nothing loaded for genotype %s' % genotype)
			continue
		
		# This is a list, each entry of which is the number of hits in ROI
		a.num_laser_hits = [[] for i in range(a.num_postures)]
		a.num_wall_hits = [[] for i in range(a.num_postures)]
		a.wall_xs = [[] for i in range(a.num_postures)]
		a.wall_ys = [[] for i in range(a.num_postures)]
		a.laser_xs = [[] for i in range(a.num_postures)]
		a.laser_ys = [[] for i in range(a.num_postures)]
		
		# For each dir of genotype, load laser pos, DLC data, frame/orient data
		for dir in a.dirs_to_analyze:
			
			print (dir)
			a.load_laser_wall_pos(dir)
			
			# For each slot, different file; load sequentially
			for iL in range(a.num_slots):
				try:
					a.load_DLC(dir, iL)
				except FileNotFoundError:
					print ('%s_lane_%s_topbyroi.csv not found' % (dir, iL))
					continue
				try:
					a.load_frame_ROI(dir, iL)
				except FileNotFoundError:
					print ('%s_lane_%s_topbyroi.txt not found' % (dir, iL))
					continue
				a.get_frame_ranges()
				a.get_touches(dir, iL)
		
		a.plot_xy_data(in_dir, genotype)
		a.plot_num_touches_per_ROI(in_dir, genotype)
		
		
if __name__ == '__main__':
	argh.dispatch_command(main)