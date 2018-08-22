close all
%for looping all the folders for analysis of timme spent in particular ROI
clear
clc

%select the genotype and power text file
fileID = fopen('C:\Users\Divyansh Mittal\Desktop\KITP_Qbio_data\genotype_power.txt');
geno=textscan(fileID,'%s');

%select the folder containing all the analysis output
filepath = uigetdir('./subfolder1/');
cd (filepath)% navigating to the folder

for j = 1:length(geno{1}) % loop for all the genotype and power
    temp = geno{1}(j);
    temp = cell2mat(temp);
    filesname = dir(temp);
    maindata = [];
    for i = 1:length(filesname)%loop for collecting data from one genotype and power from different folder
        cd (filesname(i).name)
        data = load('ROI_frame_splits.txt');
        maindata = [maindata; data];
        cd ..  
    end
    [onetwoone(j), alltimeonetwoone{j}] = transmedian_new2(maindata,1,2,1,4,3,4);
    [onetwothree(j), alltimeonetwoone{j}] = transmedian_new2(maindata,1,2,3,4,3,2);
    
end
laswall_back_05 = onetwoone(1:8);
laswall_back_15 = onetwoone(9:16);
laswall_cross_05 = onetwothree(1:8);
laswall_corss_15 = onetwothree(9:16);

tabl = cell2table(alltimeonetwoone')
writetable(tabl,'time1to2to1.csv')

tab2 = cell2table(alltimeonetwoone')
writetable(tab2,'time1to2to3.csv')


figure(1)
plot(laswall_back_05,'r*')
hold on 
plot(laswall_cross_05,'k*')
title ('0.5 mW')
figure(2)
plot(laswall_back_15,'r*')
hold on 
plot(laswall_corss_15,'k*')
title ('1.5 mW')

