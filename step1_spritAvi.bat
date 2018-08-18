SET EXPDIR="d:\Fly videos\Experiment"

for /f "tokens=*" %%G in ('dir /b /a:d %EXPDIR%\*') do (
    mkdir %EXPDIR%\%%G\analysis_output
    if not exist %EXPDIR%\%%G\analysis_output\position.json (
        python step_1.py %EXPDIR%\%%G\%%G_MMStack_Pos0.ome.tif %EXPDIR%\%%G\laserposition_paper.tif %EXPDIR%\%%G\analysis_output
    )
)
