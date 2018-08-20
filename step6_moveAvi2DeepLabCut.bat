SET EXPDIR="d:\Fly videos\Experiment"
SET DEEPDIR="D:\DeepLabCut\videos"

for /f "tokens=*" %%G in ('dir /b /a:d %EXPDIR%\*') do (
    if exist %EXPDIR%\%%G\analysis_output\lane_3_top.avi (
        copy %EXPDIR%\%%G\analysis_output\lane_0_top.avi %DEEPDIR%\%%G_lane_0_top.avi
        copy %EXPDIR%\%%G\analysis_output\lane_1_top.avi %DEEPDIR%\%%G_lane_1_top.avi
        copy %EXPDIR%\%%G\analysis_output\lane_2_top.avi %DEEPDIR%\%%G_lane_2_top.avi
        copy %EXPDIR%\%%G\analysis_output\lane_3_top.avi %DEEPDIR%\%%G_lane_3_top.avi
    )
)
