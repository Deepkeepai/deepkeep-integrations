:; exec "${0%/*}/deepkeep-hook" "$@"
@echo off
REM DeepKeep hook launcher (Windows entry point).
REM
REM On Windows this batch file starts the PowerShell launcher. POSIX shells
REM execute the first line and hand off to deepkeep-hook instead.
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "%~dp0run.ps1" %*
exit /b %ERRORLEVEL%
