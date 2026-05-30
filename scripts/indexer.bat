@echo off
REM Usage:
REM scripts\indexer.bat data\<seed_folder>\optimized index

set "INPUT_DIR=%~1"
set "INDEX_DIR=%~2"
set "EXTRA_ARG=%~3"

if not "%EXTRA_ARG%"=="" (
    echo ERROR: Too many arguments.
    echo Usage: scripts\indexer.bat data^<seed_folder^>\optimized [index_dir]
    exit /b 1
)

if "%INPUT_DIR%"=="" (
    echo ERROR: Missing input directory.
    exit /b 1
)

if "%INDEX_DIR%"=="" (
    set "INDEX_DIR=index"
    echo INDEX_DIR not provided. Using default: index
)

cd /d "%~dp0.."

python Indexer\indexer.py "%INPUT_DIR%" "%INDEX_DIR%"