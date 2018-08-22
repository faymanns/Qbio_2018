% calculat the time spend in either ROI 2 or 3 when transitioning from
% either side
% modified: time spend in ROIcur when moving from ROIpre 
function [median1to2] = transmedian_new(data,ROIpre,ROIcur)
%data = load(file_address);

count1to2 =1;

for i=2:length(data)-1
    %time spend in 2 when going from 1 to 2
    if data(i,1) == ROIpre && data(i+1,1) ==ROIcur
        time1to2(count1to2,1)=data(i+1,3)-data(i+1,2);
        count1to2 = count1to2 +1;
    end
end
   
median1to2 = median(time1to2);
end