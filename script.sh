#! /bin/bash

dir="~/Desktop/Qbio_2018"
tif_file="${dir}/sample_input.tif"
laser_file="${dir}/laserposition_paper.jpg"
out_dir="."
./step_1.py $tif_file $laser_file $out_dir
