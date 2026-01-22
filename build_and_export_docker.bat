@echo off
REM Build and export Docker image for ibookr_v2

REM Get version from settings.py from app_version: str = "0.9.9"
for /f "tokens=3 delims== " %%a in ('findstr /r /c:"app_version: str = \"[0-9]*\.[0-9]*\.[0-9]*\"" .\ibookr\settings.py') do (
    set VERSION=%%~a
)

REM Set image name
set IMAGE=ibookr

REM Build Docker image with 'latest' and version tag

docker build -t %IMAGE%:%VERSION% .
if %errorlevel% neq 0 (
    echo Docker build failed.
    exit /b %errorlevel%
)

docker tag %IMAGE%:%VERSION% %IMAGE%:latest
if %errorlevel% neq 0 (
    echo Docker tag failed.
    exit /b %errorlevel%
)

REM Export versioned image to tar

echo Exporting Docker image %IMAGE%:%VERSION% to %IMAGE%_%VERSION%.tar

docker save -o %IMAGE%_%VERSION%.tar %IMAGE%:%VERSION%

if %errorlevel% neq 0 (
    echo Docker save failed.
    exit /b %errorlevel%
)
echo Docker image built and exported: %IMAGE%:%VERSION%  %IMAGE%_%VERSION%.tar

