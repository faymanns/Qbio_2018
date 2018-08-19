SET EXPDIR="d:\Fly videos\Experiment"

for /f "tokens=*" %%G in ('dir /b /a:d %EXPDIR%\*') do (
        python check_position.py %EXPDIR%\%%G
)
