SET EXPDIR="d:\Fly videos\Experiment"

for /f "tokens=*" %%G in ('dir /b /a:d /O:-N %EXPDIR%\*') do (
    if exist %EXPDIR%\%%G\analysis_output\corrected_orient.txt (
        if not exist %EXPDIR%\%%G\analysis_output\lane_3_topbyroi.txt (
            python extract_avi_byROI.py %EXPDIR%\%%G\analysis_output
        )
    )
)
