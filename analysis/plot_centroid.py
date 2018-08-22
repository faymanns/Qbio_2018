"""
Smooth and plot centroid data and color by acceleration 

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


class centroid(object):
	"""
	Classify fly as being in particular region of interest in the assay.
	"""
	
	def __init__(self, mm_per_px, fps, num_slots):
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
		
		# Genotypes to load
		self.genotypes = ['empty', 'iav', 'ppk', 'R14F05', 'R38B08R81E10', 
						'R48A07', 'R86D09', 'stum']
		
		# Number of slots in assay. 3 values for L, laser, and R, respectively.
		self.num_slots = num_slots
		self.pos_arr = sp.zeros((3, self.num_slots))
		
		# Construct data variables
		self.num_frames = None
		self.Tt = None
		self.fps = fps
		self.data = None
		
	
	def get_all_dirs(self, in_dir):
		"""
		Get all directories in the analysis output directory corresponding to 
		those that are in the self.genotypes attribute. 
		
		Parameters
		----------
		in_dir: str
			analysis directory.
		
		"""
	
		all_dirs = next(os.walk(in_dir))[1]
		self.dirs_to_analyze = []
		for dir in all_dirs:
			genotype_exists = False
			for genotype in self.genotypes:
				if genotype in dir:
					genotype_exists = True
					break
			if genotype_exists == True:
				full_dir = os.path.join(in_dir, dir)
				self.dirs_to_analyze.append(full_dir)
		assert len(self.dirs_to_analyze) != 0, 'No dirs loaded; check in_dir.'
	
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
		
		self.data = None
		for iS in range(self.num_slots):
			filename = os.path.join(in_dir, 'lane_%s.avi_x.txt' % (iS))
			slot_data = sp.loadtxt(filename)
			if self.data is None:
				self.data = sp.zeros((len(slot_data), self.num_slots))
			self.num_frames = len(slot_data)
			self.Tt = sp.linspace(0, self.num_frames/self.fps, self.num_frames)
			self.data[:, iS] = slot_data
		
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
		
	def plot_centroid_trace(self, in_dir):
		"""
		Plot the centroid position over time.
		
		in_dir : str
			Directory of centroid file. Centroid files are in txt format, one 
			for each slot. Files are named 'slot_1.avi_x.txt, ..., 
			slot_N.avi_x.txt'. Each is a 1D list with with N frames, 
			corresponding to the x-pos of the centroid for that slot.
		
		"""
		
		base_dir = os.path.dirname(in_dir)
		exp_dir = os.path.basename(in_dir)
		
		for iS in range(self.num_slots):
			
			fig = plt.figure()
			fig.set_size_inches(15, 3)
			plt.xlim(-2, 302)
			plt.ylim(0, 800)
			plt.xticks([])
			plt.yticks([])
			
			smoothed_data = self.smooth(self.data[:, iS])
			plt.scatter(self.Tt, smoothed_data, s=1, color='k')
			plt.axhline(y = self.pos_arr[1, iS], color='r', lw=3)
			
			filename = os.path.join(base_dir, '_tracks', 
									'%s_track=%s.png' % (exp_dir, iS))
			plt.tight_layout()
			plt.savefig(filename)
			
			
def main(in_dir, mm_per_px=3./106, fps=60, num_slots=4):
	
	a = centroid(mm_per_px, fps, num_slots)
	a.get_all_dirs(in_dir)
	for dir in a.dirs_to_analyze:
		a.load_laser_wall_pos(dir)
		a.load_centroid_data(dir)
		a.plot_centroid_trace(dir)
		
	
if __name__ == '__main__':
	argh.dispatch_command(main)