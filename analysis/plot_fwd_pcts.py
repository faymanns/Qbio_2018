"""
Plot laser crossing transition probabilities.

Created by Nirag Kadakia at 23:50 08-20-2018
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

class plot_fwd_pcts(object):
	"""
	Plot forward percentages for each genotype on single plot.
	"""
	
	def __init__(self, laser_int):
		"""
		Initialize class. 
		
		Parameters
		----------
		laser_int: str
			laser intensity (in filename). e.g. `_0.5mW' 
			
		"""
	
		self.dirs_to_plot = None
		self.data = None
		self.genotypes = None
		self.laser_int = laser_int
		
	def get_all_dirs(self, in_dir):
		"""
		Get all directories in the analysis output directory corresponding 
		to the desired genotype. All directories containing genotype will
		be appended to dirs_to_plot.
		
		Parameters
		----------
		in_dir: str
			analysis directory.
		
		"""
		
		if not os.path.isdir(in_dir):
			print ('%s does not exist!' % in_dir)
			quit()
		
		full_dir = os.path.join(in_dir, '_centroid')
		all_dirs = next(os.walk(full_dir))[1]
		self.dirs_to_plot = []
		self.genotypes = []
		for dir in all_dirs:
			if self.laser_int in dir:
				self.dirs_to_plot.append(os.path.join(full_dir, dir))
				self.genotypes.append('%s' % (dir.replace(self.laser_int, '')))
		self.genotypes = sp.array(self.genotypes, dtype='object')
		
	def plot_pct_fwds(self):
		"""
		Plot the pct of forward motion for each genotype.
		"""
		
		Nn = len(self.dirs_to_plot)
		for iD, dir in enumerate(self.dirs_to_plot):
			filename = os.path.join(dir, 'pct_fwd.txt')
			tmp_data = sp.loadtxt(filename)
			if self.data is None:
				self.data = sp.zeros((Nn, len(tmp_data)))
			self.data[iD, :] = tmp_data
		
		# Get average fwd_pcts with error bars (1 sem)
		self.avgs = sp.average(self.data, axis=1)*100
		self.stds = sp.std(self.data, axis=1)*100
		sort_idxs = sp.argsort(self.avgs)[::-1]
		
		# Make empty zero index if not yet (hacky!!)
		if sort_idxs[0] != 0:
			zero_idx = sp.argwhere(sort_idxs == 0)[0]
			change_idx = sort_idxs[zero_idx]
			sort_idxs[zero_idx] = sort_idxs[0]
			sort_idxs[0] = 0
			
		sort_labels = self.genotypes[sort_idxs]
		sort_avgs = self.avgs[sort_idxs]
		sort_stds = self.stds[sort_idxs]
		
		
		# Plot for each genotype
		fig = plt.figure()
		fig.set_size_inches(3, 4)
		plt.errorbar(range(Nn), sort_avgs, sort_stds, lw=0, 
						elinewidth=1.5, capsize=5, color='k')
		plt.scatter(range(Nn), sort_avgs, c=sp.arange(Nn), 
						cmap=plt.cm.winter, zorder=100, s=30)
		plt.ylim(0, 105)
		plt.xticks(rotation=90)
		plt.xticks(range(Nn), sort_labels)
					
	def save_data(self, in_dir):
		"""
		Output fwd and bkwd percent averages and stds. 
		
		Parameters
		----------
		in_dir : str
			Directory of where to save data / same as input directory.
		
		"""
		
		out_file = os.path.join(in_dir, '_centroid', 'pct_fwds%s.png' 
					% self.laser_int)
		plt.tight_layout()
		plt.savefig(out_file)
		out_file = os.path.join(in_dir, '_centroid', 'pct_fwds%s.svg' 
					% self.laser_int)
		plt.tight_layout()
		plt.savefig(out_file)
		
		
def main(in_dir, laser_int='_0.5mW'):
	a = plot_fwd_pcts(laser_int)
	a.get_all_dirs(in_dir)
	a.plot_pct_fwds()
	a.save_data(in_dir)
	
if __name__ == '__main__':
	argh.dispatch_command(main)