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
    [mediantime(1,j),mediantime(2,j),alltime1to2{j} ,alltime3to2{j}] = transmedian(maindata);
    
    
end
tabl = cell2table(alltime1to2')
writetable(tabl,'time1to2.csv')

tab2 = cell2table(alltime3to2')
writetable(tab2,'time3to2.csv')

%figures
figure(1)
plot(mediantime(1,1:8),'k*') %1to2
hold on
plot(mediantime(2,1:8),'r*') %3to2
title('0.5mW')
figure(2)
plot(mediantime(1,9:16),'k*') %1to2
hold on
plot(mediantime(2,9:16),'r*') %3to2
title('1.5mW')
