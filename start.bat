@echo off
cd /d "%~dp0"
rem Stop the mock with Ctrl+C.
where py >nul 2>nul && (py -3 run.py %* & goto :eof)
python run.py %*
