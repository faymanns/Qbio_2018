SET EXPDIR="d:\Fly videos\Experiment"

for /f "tokens=*" %%G in ('dir /b /a:d /O:-N %EXPDIR%\*') do (
    if exist %EXPDIR%\%%G\analysis_output\position.json (
        if not exist %EXPDIR%\%%G\analysis_output\lane_3.avi_x.txt (
            tprocall.bat %EXPDIR%\%%G\analysis_output
        )
    )
)
