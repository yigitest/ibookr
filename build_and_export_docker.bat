@echo off
REM Build and export Docker image for ibookr_v2

REM Read version from VERSION file
setlocal enabledelayedexpansion
set VERSION=
for /f "delims=" %%v in (VERSION) do set VERSION=%%v

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

