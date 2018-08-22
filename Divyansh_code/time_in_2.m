%clear
%clc
function [mediantime2, mediantime3] = mediantimespent(file_address)
data = load(file_address);
count2 = 1;
count3 = 1;
for i=2:length(data)
    %time spend in 2 
    if data(i) == 2
       time2(count2)=data(i,3)-data(i,2);
       count2 = count2 +1;
    end
    %time spend in 3 
    if data(i) == 3
       time3(count3)=data(i,3)-data(i,2);
       count3 = count3 +1;
    end   
end
mediantime2 = median(time2);
mediantime3 = median(time3);