SET EXPDIR="d:\Fly videos\Experiment"
SET DEST="D:\analysis_outputs"
mkdir %DEST%

for /f "tokens=*" %%G in ('dir /b /a:d %EXPDIR%\*') do (
    if exist %EXPDIR%\%%G\analysis_output (
	mkdir %DEST%\%%G
        xcopy /e %EXPDIR%\%%G\analysis_output %DEST%\%%G
    )
)
