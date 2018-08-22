%Calculate median time spent in ROI 2 and 3 (adjacent to wall)
function [mediantimetot, timetot] = mediantimespent(data,ROI1,ROI2)
%data = load(file_address);
count2 = 1;
count3 = 1;
for i=2:length(data)
    %time spend in ROI1 
    if data(i) == ROI1
       time2(count2)=data(i,3)-data(i,2);
       count2 = count2 +1;
    end
    %time spend in ROI2 
    if data(i) == ROI2
       time3(count3)=data(i,3)-data(i,2);
       count3 = count3 +1;
    end   
end
mediantime2 = median(time2);
mediantime3 = median(time3);
timetot = [(time2)'; (time3)'];
mediantimetot = median(timetot);
end