SET EXPDIR="d:\Fly videos\Experiment"

for /f "tokens=*" %%G in ('dir /b /a:d %EXPDIR%\*') do (
    mkdir %EXPDIR%\%%G\analysis_output
    if exist %EXPDIR%\%%G\analysis_output\corrected_orient.txt (
        if not exist %EXPDIR%\%%G\analysis_output\lane_3_top.avi (
            python extract_avi %EXPDIR%\%%G\analysis_output %EXPDIR%\%%G\analysis_output
        )
    )
)
