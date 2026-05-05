@echo off
REM Usage:
REM scripts\crawler.bat Crawler\seed.txt 10000 6 data\crawl_output

set SEED_FILE=%1
set NUM_PAGES=%2
set HOPS=%3
set OUT_DIR=%4

if "%SEED_FILE%"=="" (
    echo Missing seed file.
    echo Usage: scripts\crawler.bat Crawler\seed.txt 10000 6 data\crawl_output
    exit /b 1
)
if "%NUM_PAGES%"=="" set NUM_PAGES=10000
if "%HOPS%"=="" set HOPS=6
if "%OUT_DIR%"=="" set OUT_DIR=data\crawl_output

cd /d "%~dp0.."

python Crawler\crawler.py "%SEED_FILE%" %NUM_PAGES% %HOPS% "%OUT_DIR%"