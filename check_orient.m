function varargout = check_orient(varargin)
    % check command line input
	if size(varargin, 2) < 2
        disp('usage: check_orient input_dir output_dir [boxSize] [yTh] [sideTh] [gap] [duration] [showFigure]');
        return;
    end

    % set param
    inputPath = varargin{1};
    outputPath = varargin{2};
    if size(varargin, 2) >= 3
        boxSize = str2num(varargin{3});
    else
        boxSize = 80;
    end
    if size(varargin, 2) >= 4
        yTh = str2num(varargin{4});
    else
        yTh = 35;
    end
    if size(varargin, 2) >= 5
        sideTh = str2num(varargin{5});
    else
        sideTh = 15;
    end
    if size(varargin, 2) >= 6
        gapFrames = str2num(varargin{6});
    else
        gapFrames = 30;
    end
    if size(varargin, 2) >= 7
        minDuration = str2num(varargin{7});
    else
        minDuration = 10;
    end
    if size(varargin, 2) >= 8
        showImage = str2num(varargin{8});
    else
        showImage = 0;
    end
    csvOutput = [];
    
    % open movie file
    aviList = dir([inputPath '/*.avi']);
    if showImage
        figure;
    end
    for i=1:size(aviList,1)
        % processing
        fname = [aviList(i).folder '/' aviList(i).name];
        disp(['open : ' fname]);

        % open video file
        videoStructs = VideoReader(fname);
        height = videoStructs.Height;
        % open background image
        bgImageFile = [fname '_tpro/background.png'];
        if ~exist(bgImageFile, 'file')
            disp(['can not open background image : ' bgImageFile]);
            continue;
        end
        bgImage = imread(bgImageFile);
        % open data files
        x = tblread([fname '_x.txt'],'tab');
        if size(x,1) == 0
            disp(['can not read csv file : ' fname]);
            continue;
        end
        if size(x,2) == 0
            x = csvread([fname '_x.txt']);
            y = csvread([fname '_y.txt']);
            ori = csvread([fname '_angle.txt']);
        else
            x = tblread([fname '_x.txt'],'tab');
            y = tblread([fname '_y.txt'],'tab');
            ori = tblread([fname '_angle.txt'],'tab');
        end

        output = zeros(videoStructs.NumberOfFrames,1);
        
        for j = 1:videoStructs.NumberOfFrames
            % check y axis first
            if height-y(j,1) > yTh && y(j,1) > yTh
                %disp(['j=' num2str(j) ' center position y']);
                continue;
            end

            % trim & rotate image
            img = read(videoStructs,j);
            img = rgb2gray(img);

            img2 = bgImage - img;
            img2 = uint8(img2);

            img3 = getOneFlyBoxImage_(img2,x(j,1),height-y(j,1),ori(j,1),boxSize);
            %
            %flipImg = fliplr(img4);
            %img4 = abs(img4 - flipImg);

            img3(img3>20) = 255;
            img4 = imbinarize(img3);
            width = size(img4,2);
            lCount = length(find(img4(:,1:sideTh)));
            rCount = length(find(img4(:,width-sideTh+1:width)));
            if (lCount>0 && rCount>0) || (lCount==0 && rCount==0)
                %disp(['j=' num2str(j) ' found leg both side.']);
                continue;
            end

            % calc symmetric rate
            %{
            c = floor(size(img4,2)/2+1);
            m = size(img4,1) - 5;
            sym1 = sum(sum(img4(5:m,c-29:c)));
            sym2 = sum(sum(img4(5:m,c+1:c+30)));
            rate = sym1 / sym2;
            %}
            if showImage
                imshow(img4);
            end
            output(j,1) = 1;
            disp(['j=' num2str(j) ' lCount=' num2str(lCount) ' rCount=' num2str(rCount)]);
        end
        csvOutput = [csvOutput, output];
    end

    % apply duration filter
    csvOutput = durationFilter(csvOutput, minDuration);

    % apply gap filter
    csvOutput = gapFilter(csvOutput, gapFrames);

    % output tab sepalated csv
    fname = [outputPath '/corrected_orient.txt'];
    disp(['output tab sepalated csv file : ' fname]);
    dlmwrite(fname,csvOutput,'\t');
end

%%
function trimmedImage = getOneFlyBoxImage_(image, ptX, ptY, angle, boxSize)
    trimSize = boxSize * 1.5;
    rect = [ptX-(trimSize/2) ptY-(trimSize/2) trimSize trimSize];
    if rect(2) < 0
        rect(4) = rect(4) + floor(rect(2)) * 2;
        rect(2) = 0;
    end
    if rect(2)+trimSize > size(image,1)
        rect(4) = rect(4) - floor(rect(2));
        rect(2) = rect(2) * 2;
    end
    trimmedImage = imcrop(image, rect);
    [x,y,col] = size(trimmedImage);
    if rect(4) < trimSize
        boxImg = uint8(zeros(trimSize,trimSize));
        bgY = trimSize/2 - floor(size(trimmedImage,1) / 2);
        if bgY < 1
            bgY = 1;
        end
        edY = bgY + size(trimmedImage,1)-1;
        bgX = trimSize/2 - floor(size(trimmedImage,2) / 2);
        if bgX < 1
            bgX = 1;
        end
        if size(trimmedImage,2) < trimSize
            edTrX = size(trimmedImage,2);
        else
            edTrX = trimSize;
        end
        edX = bgX + edTrX-1;
        boxImg(bgY:edY,bgX:edX) = trimmedImage(:,1:edTrX);
        trimmedImage = boxImg;
    end

    % rotate image
    rotatedImage = imrotate(trimmedImage, 270-angle, 'crop', 'bilinear');

    % trim again
    rect = [(trimSize-boxSize)/2 (trimSize-boxSize)/2 boxSize boxSize];
    trimmedImage = imcrop(rotatedImage, rect);
    [x,y,col] = size(trimmedImage);
    if x > boxSize || y > boxSize
        trimmedImage(:,(boxSize+1):end) = [];
        trimmedImage((boxSize+1):end,:) = [];
    end
end

%%
function be_mat = gapFilter(mat, gap_len)
    frame_num = size(mat, 1);
    fly_num = size(mat, 2);

    % gap completion
    for fn = 1:fly_num
        i = 1;
        while i <= (frame_num - gap_len)
            if((mat(i,fn) ~= 0) && mat(i+1,fn) == 0)
                val  = mat(i,fn);
                active = find(mat((i+1):(i+gap_len),fn) > 0);
                cnt1 = length(active);
                if(cnt1 > 0)
                    mat((i+1):(i+active(1)),fn) = val;
                    i = i+active(1)-1;
                else
                    i = i+gap_len-1;
                end
            end
            i = i + 1;
        end
    end
    be_mat = mat;
end

%%
function be_mat = durationFilter(mat, threshold)
    frame_num = size(mat, 1);
    fly_num = size(mat, 2);
    
    mat(frame_num+1,:) = 0;
    for fn = 1:fly_num
        cnt = 0;
        for i = 1:(frame_num + 1)
            if mat(i,fn) > 0
                cnt = cnt + 1;
            elseif cnt > 0
                if cnt < threshold
                    mat((i-cnt):i,fn) = 0;
                end
                cnt = 0;
            end
        end
    end
    mat(frame_num+1,:) = [];
    be_mat = mat;
end
