@echo off
rem publish launcher (Windows twin of tools/publish).
rem Finds a working Python >=3.10 and execs tools\publish.py with it.
setlocal
set "here=%~dp0"
set "pybin="

call :try py -3
if defined pybin goto :run
call :try python3
if defined pybin goto :run
call :try python
if defined pybin goto :run

echo publish: no working Python 3.10 or newer was found. 1>&2
echo Install one from python.org and run this again. 1>&2
exit /b 1

:try
%1 %2 -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
if errorlevel 1 exit /b 0
if "%2"=="" (set "pybin=%1") else (set "pybin=%1 %2")
exit /b 0

:run
%pybin% "%here%publish.py" %*
exit /b %errorlevel%
