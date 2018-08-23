"""
Find transition probability across laser or away from laser.

Created by Nirag Kadakia at 17:40 08-20-2018
This work is licensed under the 
Creative Commons Attribution-NonCommercial-ShareAlike 4.0 
International License. 
To view a copy of this license, visit 
http://creativecommons.org/licenses/by-nc-sa/4.0/.
"""

import scipy as sp
import matplotlib.pyplot as plt
import argh
import os


class transitions(object):
	"""
	Classify fly as being in particular region of interest in the assay.
	"""
	
	def __init__(self, num_slots):
		"""
		Initialize class. 
		
		Parameters
		---------
		num_slots: int
			number of slots in fly arena.
			
		"""
		
		self.num_slots = num_slots
		self.dirs_to_analyze = None
		self.ROI_data = None
		self.trans_mat = sp.zeros((6, 6))
		self.trans_mat_n = sp.zeros(6)
		self.backs = None
		self.fwds = None
		self.pct_fwds = None
		self.pct_fwd_avg = None
		self.pct_fwd_sem = None
		
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
			
	def load_ROI_data(self, dir):
		"""
		Set the ROI data from file.
		
		Parameters
		----------
		dir : str
			diretory from which to load `ROI_frame_splits.txt' file.
		"""
		
		filename = os.path.join(dir, 'ROI_frame_splits.txt')
		ROI_data = sp.loadtxt(filename, dtype='int')
			
		for iS in range(self.num_slots):
			if self.ROI_data is None:
				self.ROI_data = sp.empty((self.num_slots), dtype='object')
			curr_lane_idxs =  sp.where(ROI_data[..., -1] == iS)
			self.ROI_data[iS] = ROI_data[curr_lane_idxs][..., :-1]
			
	def transition_matrix(self):
		"""
		Get transition likelihood out of an ROI.
		"""
		
		# Calculate transitions starting at a given ROI region = iRi
		for iRi in range(6):
			for iS in range(self.num_slots):
				idxs = sp.where(self.ROI_data[iS][..., 0] == iRi)[0]
				if len(idxs) <= 1: 
					continue
				if idxs[-1] >= self.ROI_data[iS].shape[0] - 1:
					idxs  = idxs[:-1]
				ROI_end = self.ROI_data[iS][idxs + 1, 0]
				
				# Get transitions from iRi to iRf
				for iRf in range(6):
					self.trans_mat[iRf, iRi] += sp.sum(ROI_end == iRf)
				
		# Normalize each column to number of values in that column
		for iRi in range(6):
			self.trans_mat_n[iRi] = sp.sum(self.trans_mat[:, iRi])
			self.trans_mat[:, iRi] = self.trans_mat[:, iRi]/\
										sp.sum(self.trans_mat[:, iRi])
	
	def trans_prob_laser(self):
		"""
		Get the transitions near the laser; either through or backs away.
		These values are the percentage of forwards when entering the region
		in the direction toward the laser wall.
		"""
		
		for iS in range(self.num_slots):
			
			# Calculate for fwd = 1->2->3 and for 4->3->2
			for ROI in [[1, 2, 3], [4, 3, 2]]:
		
				idxs_1 = sp.where(self.ROI_data[iS][..., 0] == ROI[0])[0]
				idxs_2 = sp.where(self.ROI_data[iS][..., 0] == ROI[1])[0]
				
				# Find places where fly went from ROI[0] to ROI[1]
				idxs12 =  [val for val in idxs_2 if val in (idxs_1 + 1)]
				
				# For each ROI = ROI[1], determine if it went fwd or bckward
				for idx2 in idxs12:
				
					# If too short, ignore
					if idx2 >= self.ROI_data[iS].shape[0] - 1:
						continue
						
					# ROI it transitioned to next
					out_idx = self.ROI_data[iS][idx2 + 1, 0]
					if out_idx == ROI[2]:
						self.fwds += 1
					else:
						self.backs += 1
		
	def calc_pct_fwd(self):
		"""
		Calculate the statistics of likelihhod to go forward or turn
		back when entering region of laser. Stats are found from bootstrapping.
		"""
		
		# Get all the data; set fwds == 1 and bkwds == 0
		vals = sp.zeros(self.fwds + self.backs)
		vals[:self.fwds] = 1
		
		# Samples per bootstrap; number of bootstrap reps
		num_samples = int(len(vals)/5)
		num_reps = 10000
		num_total = num_samples*num_reps
		
		# Resample num_total times w/replacement; then reshape to bootstraps
		bootstraps = sp.random.choice(vals, size=num_total, replace=True)
		bootstraps = sp.reshape(bootstraps[:num_total], (num_samples, -1))
		
		# Get statistic for each bootstrap sample
		self.pct_fwds = (1.*sp.sum(bootstraps, axis=0)/bootstraps.shape[0])
		
	def save_data(self, in_dir, genotype):
		"""
		Output fwd and bkwd percent averages and stds. 
		
		Parameters
		----------
		in_dir : str
			Directory of where to save data / same as input directory.
		genotype: str
			Name of genotype.
		
		"""
		
		out_dir = os.path.join(in_dir, '_centroid', genotype)
		out_file = os.path.join(out_dir, 'pct_fwd.txt')
		
		if not os.path.isdir(out_dir):
			os.makedirs(out_dir)
		with open(out_file, 'w') as fp:
			sp.savetxt(fp, self.pct_fwds, fmt='%.5f', delimiter='\t')
		
		
def main(in_dir, genotype=None, num_slots=4):
	
	a = transitions(num_slots)
	if genotype == None:
		genotypes = ['empty_0.5mW', 'empty_1.5mW', 'iav_0.5mW', 'iav_1.5mW',
						'ppk_0.5mW', 'ppk_1.5mW', 'R14F05_0.5mW', 
						'R14F05_1.5mW', 'R38B08R81E10_0.5mW', 
						'R38B08R81E10_1.5mW', 'R48A07_0.5mW', 'R48A07_1.5mW', 
						'R86D09_0.5mW', 'R86D09_1.5mW', 'stum_0.5mW', 
						'stum_1.5mW']				
	else:
		genotypes = [genotype]
	
	for genotype in genotypes:
		a.get_all_dirs(in_dir, genotype)
		if len(a.dirs_to_analyze) == 0:
			continue
		a.fwds = 0
		a.backs = 0
		for dir in a.dirs_to_analyze:
			a.load_ROI_data(dir)
			a.trans_prob_laser()
		a.calc_pct_fwd()
		a.save_data(in_dir, genotype)
		
if __name__ == '__main__':
	argh.dispatch_command(main)