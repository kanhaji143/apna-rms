@echo off
title APNA Computer Institute - Certificate Trust Installer
echo =====================================================================
echo   APNA Computer Institute - Code Signing Certificate Registration
echo =====================================================================
echo.
echo Installing APNA Computer digital certificate into Windows store...
certutil -addstore -user -f "TrustedPublisher" "%~dp0APNA_Computer_Certificate.cer"
echo.
echo =====================================================================
echo   Certificate registered successfully!
echo   APNA Computer RMS is now recognized as a trusted publisher.
echo =====================================================================
echo.
pause
