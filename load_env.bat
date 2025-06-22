@echo off
:: Helper script to load environment variables from .env file
:: This script can be called by other batch files

if exist .env (
    echo Loading environment variables from .env file...
    
    :: Read .env file line by line
    for /f "usebackq eol=# tokens=1,* delims==" %%i in (".env") do (
        if not "%%i"=="" (
            set "%%i=%%j"
            echo Set %%i=%%j
        )
    )
    
    echo Environment variables loaded successfully!
) else (
    echo Warning: .env file not found in current directory
    echo Please create a .env file with your configuration
    echo You can copy from env_variables.txt
    pause
    exit /b 1
) 