#! /bin/bash

for dir in ~/Desktop/Qbio_2018/data*
do
    tif_file="${dir}/sample_input.tif"
    laser_file="${dir}/laserposition_paper.jpg"
    out_dir="${dir}/analysis_output"
    mkdir $out_dir
    ./step_1.py $tif_file $laser_file $out_dir
done
