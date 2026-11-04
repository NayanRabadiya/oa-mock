@echo off
cd /d "%~dp0"
rem Stop the mock with Ctrl+C.
where py >nul 2>nul && (py -3 oa_mock_local.py %* & goto :eof)
python oa_mock_local.py %*
