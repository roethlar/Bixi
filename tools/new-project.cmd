@echo off
rem new-project launcher (Windows twin of tools/new-project).
rem Finds a working Python >=3.10 and execs tools\new-project.py with it, so
rem the owner never thinks about interpreters. Probe order per the repo's
rem Windows contract (procedures/bootstrap.md): py -3 first, then python3,
rem then python; the Microsoft Store App Execution Alias stub fails the
rem version probe and so counts as absent.
setlocal
set "here=%~dp0"
set "pybin="

call :try py -3
if defined pybin goto :run
call :try python3
if defined pybin goto :run
call :try python
if defined pybin goto :run

echo new-project: no working Python 3.10 or newer was found. 1>&2
echo Install one from python.org and run this again. 1>&2
exit /b 1

:try
rem Probe "cmd [arg]": succeeds only if the interpreter exists AND is >=3.10.
%1 %2 -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
if errorlevel 1 exit /b 0
if "%2"=="" (set "pybin=%1") else (set "pybin=%1 %2")
exit /b 0

:run
%pybin% "%here%new-project.py" %*
exit /b %errorlevel%
