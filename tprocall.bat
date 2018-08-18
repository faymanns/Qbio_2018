SET AVIDIR=%1

for /r %AVIDIR% %%G in (*.avi) do (
    c:\tpro_2015a\TPro.exe -g --showcount 0 --tempindex 5 -d -t -f --export %AVIDIR% "%%G"
)
