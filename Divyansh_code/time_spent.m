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
    [strlaswall(j,1),strlaswall(j,2),strlaswall(j,3)]= mediantimespent(maindata,2,3);
    [strrealwall(j,1),strrealwall(j,2),strrealwall(j,3)]= mediantimespent(maindata,0,5);
    
end
laswall_05 = strlaswall(1:8,3);
laswall_15 = strlaswall(9:16,3);
realwall_05 = strrealwall(1:8,3);
realwall_15 = strrealwall(9:16,3);
figure(1)
plot(laswall_05,'r*')
hold on 
plot(realwall_05,'k*')
title ('0.5 mW')
figure(2)
plot(laswall_15,'r*')
hold on 
plot(realwall_15,'k*')
title ('1.5 mW')

