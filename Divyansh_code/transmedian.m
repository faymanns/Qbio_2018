% calculat the time spend in either ROI 2 or 3 when transitioning from
% either side
function [median1to2,median3to2,timetot1to2,timetot3to2] = transmedian(data)
%data = load(file_address);

count1to2 =1;
count3to2 =1;

count4to3 =1;
count2to3 =1;

for i=2:length(data)-1
    %time spend in 2 when going from 1 to 2
    if data(i,1) == 1 && data(i+1,1) ==2
        time1to2(count1to2)=data(i+1,3)-data(i+1,2);
        count1to2 = count1to2 +1;
    end
    %time spend in 2 when going from 3 to 2
    if data(i,1) == 3 && data(i+1,1) ==2
        time3to2(count3to2)=data(i+1,3)-data(i+1,2);
        count3to2 = count3to2 +1;
    end
    
    %time spend in 3 when going from 4 to 3
    if data(i,1) == 4 && data(i+1,1) ==3
        time4to3(count4to3)=data(i+1,3)-data(i+1,2);
        count4to3 = count4to3 +1;
    end
    %time spend in 3 when going from 2 to 3
    if data(i,1) == 2 && data(i+1,1) ==3
        time2to3(count2to3)=data(i+1,3)-data(i+1,2);
        count2to3 = count2to3 +1;
    end 
end
timetot1to2= [(time1to2)'; (time4to3)'];
timetot3to2= [(time3to2)'; (time2to3)'];

median1to2 = median(timetot1to2);
median3to2 = median(timetot3to2);
end