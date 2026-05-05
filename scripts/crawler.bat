@REM @echo off
@REM REM Usage:
@REM REM scripts\crawler.bat Crawler\seed.txt 10000 6 data\crawl_output

@REM set SEED_FILE=%1
@REM set NUM_PAGES=%2
@REM set HOPS=%3
@REM set OUT_DIR=%4

@REM if "%SEED_FILE%"=="" (
@REM     echo Missing seed file.
@REM     echo Usage: scripts\crawler.bat Crawler\seed.txt 10000 6 data\crawl_output
@REM     exit /b 1
@REM )
@REM if "%NUM_PAGES%"=="" set NUM_PAGES=10000
@REM if "%HOPS%"=="" set HOPS=6
@REM if "%OUT_DIR%"=="" set OUT_DIR=data\crawl_output

@REM cd /d "%~dp0.."

@REM python Crawler\crawler.py "%SEED_FILE%" %NUM_PAGES% %HOPS% "%OUT_DIR%"

@echo off
REM Usage:
REM scripts\crawler.bat Crawler\seed.txt 10000 6 data\crawl_output

set "SEED_FILE=%~1"
set "NUM_PAGES=%~2"
set "HOPS=%~3"
set "OUT_DIR=%~4"
set "EXTRA_ARG=%~5"

if not "%EXTRA_ARG%"=="" (
    echo ERROR: Too many arguments.
    echo Usage: scripts\crawler.bat Crawler\seed.txt [num_pages] [depth] [output_dir]
    exit /b 1
)

if "%SEED_FILE%"=="" (
    echo ERROR: Missing seed file.
    echo Usage: scripts\crawler.bat Crawler\seed.txt [num_pages] [depth] [output_dir]
    exit /b 1
)

if "%NUM_PAGES%"=="" (
    set "NUM_PAGES=10000"
    echo NUM_PAGES not provided. Using default: 10000
)

if "%HOPS%"=="" (
    set "HOPS=6"
    echo DEPTH not provided. Using default: 6
)

if "%OUT_DIR%"=="" (
    set "OUT_DIR=data"
    echo OUTPUT_DIR not provided. Using default: data
)

cd /d "%~dp0.."

python Crawler\crawler.py "%SEED_FILE%" "%NUM_PAGES%" "%HOPS%" "%OUT_DIR%"