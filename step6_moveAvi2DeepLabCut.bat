SET EXPDIR="d:\Fly videos\Experiment"
SET DEEPDIR="D:\DeepLabCut\videos"

for /f "tokens=*" %%G in ('dir /b /a:d %EXPDIR%\*') do (
    if exist %EXPDIR%\%%G\analysis_output\lane_3_topbyroi.txt (
        for %%N in (0 1 2 3) do (
            copy %EXPDIR%\%%G\analysis_output\lane_%%N_topbyroi.avi %DEEPDIR%\%%G_lane_%%N_topbyroi.avi
            copy %EXPDIR%\%%G\analysis_output\lane_%%N_topbyroi.txt %DEEPDIR%\%%G_lane_%%N_topbyroi.txt
        )
    )
)
