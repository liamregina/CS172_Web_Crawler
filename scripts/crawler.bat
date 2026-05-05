@echo off
REM Usage:
REM scripts\crawler.bat Crawler\seed.txt 10000 6 yesOpt data

set "SEED_FILE=%~1"
set "NUM_PAGES=%~2"
set "HOPS=%~3"
set "OPTIMIZE=%~4"
set "OUT_DIR=%~5"
set "EXTRA_ARG=%~6"

if not "%EXTRA_ARG%"=="" (
    echo ERROR: Too many arguments.
    echo Usage: scripts\crawler.bat Crawler\seed.txt [num_pages] [depth] [yesOpt/noOpt] [output_dir]
    exit /b 1
)

if "%SEED_FILE%"=="" (
    echo ERROR: Missing seed file.
    exit /b 1
)

if "%NUM_PAGES%"=="" set "NUM_PAGES=10000"
if "%HOPS%"=="" set "HOPS=6"

if "%OPTIMIZE%"=="" (
    set "OPTIMIZE=noOpt"
    echo OPTIMIZATION not provided. Using default: noOpt
)

if "%OUT_DIR%"=="" (
    set "OUT_DIR=data"
    echo OUTPUT_DIR not provided. Using default: data
)

cd /d "%~dp0.."

python Crawler\crawler.py "%SEED_FILE%" "%NUM_PAGES%" "%HOPS%" "%OPTIMIZE%" "%OUT_DIR%"