% calculat the time spend in either ROI 2 when coming from 1 and going back
% to 1
% 
% modified: time spend in ROIcur when moving from ROIpre and going to
% ROIpost
function [median1to2,timetot] = transmedian_new2(data,ROIpre1,ROIcur1,ROIpost1,ROIpre2,ROIcur2,ROIpost2)
%data = load(file_address);

count1to2 =1;
count3to2 =1;

for i=2:length(data)-2
    %time spend in 2 when going from 1 to 2 to 1
    if data(i,1) == ROIpre1 && data(i+1,1) == ROIcur1 && data(i+2,1) == ROIpost1
        time1(count1to2)=data(i+1,3)-data(i+1,2);
        count1to2 = count1to2 +1;
    end

    if data(i,1) == ROIpre2 && data(i+1,1) == ROIcur2 && data(i+2,1) == ROIpost2
        time2(count3to2)=data(i+1,3)-data(i+1,2);
        count3to2 = count3to2 +1;
    end

end
timetot = [(time1)'; (time2)']; 
median1to2 = median(timetot);
end