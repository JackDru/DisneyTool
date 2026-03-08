@echo off
REM Elias weekly run: scraper then scorer (Mondays 4am)
cd /d "%~dp0"

set LOGDIR=%~dp0logs
if not exist "%LOGDIR%" mkdir "%LOGDIR%"
set LOGFILE=%LOGDIR%\weekly_run.log

echo [%date% %time%] Elias weekly run started >> "%LOGFILE%"
echo Running scraper... >> "%LOGFILE%"
python "%~dp0scraper.py" >> "%LOGFILE%" 2>&1
echo [%date% %time%] Scraper finished, exit code %ERRORLEVEL% >> "%LOGFILE%"
echo Running scorer... >> "%LOGFILE%"
python "%~dp0scorer.py" >> "%LOGFILE%" 2>&1
echo [%date% %time%] Scorer finished, exit code %ERRORLEVEL% >> "%LOGFILE%"
echo [%date% %time%] Elias weekly run completed >> "%LOGFILE%"
