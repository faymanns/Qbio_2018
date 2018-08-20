SET EXPDIR="d:\Fly videos\Experiment"

for /f "tokens=*" %%G in ('dir /b /a:d %EXPDIR%\*') do (
    if exist %EXPDIR%\%%G\analysis_output\lane_3.avi_x.txt (
        if not exist %EXPDIR%\%%G\analysis_output\corrected_ROIs.txt (
            python ROI_track.py %EXPDIR%\%%G\analysis_output %EXPDIR%\%%G\analysis_output
        )
    )
)
