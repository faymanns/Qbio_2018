SET EXPDIR="d:\Fly videos\Experiment"

for /f "tokens=*" %%G in ('dir /b /a:d %EXPDIR%\*') do (    
    python step_1.py %EXPDIR%\%%G\%%G_MMStack_Pos0.ome.tif %EXPDIR%\%%G\laserposition_paper.tif %EXPDIR%\%%G\analysis_output
)
