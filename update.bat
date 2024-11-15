:: Python: `subprocess.run(['update.bat', version])`.
::! If unzip fails, execute `Set-ExecutionPolicy Unrestricted`.
@echo off
setlocal

cd %~dp0

echo Searching for the latest version

:: GitHub repository details (replace with your actual repository details)
set "OWNER=timmy90928"
set "REPO=Home"

:: Get the latest release version from GitHub using PowerShell and GitHub API
for /f "delims=" %%i in ('powershell -Command "(Invoke-WebRequest -Uri https://api.github.com/repos/%OWNER%/%REPO%/releases/latest).Content | ConvertFrom-Json | Select-Object -ExpandProperty tag_name"') do set "version=%%i"

:: Check if version was retrieved
if "%version%"=="" (
    echo Failed to retrieve the latest version from GitHub.
    exit /b 1
)
echo Ready to download %version%

:: Set variables.
set "URL=https://github.com/timmy90928/Home/releases/download/%version%/home.zip"
set "DOWNLOAD_DIR=%TEMP%\home.zip"
set "INSTALL_DIR=%~dp0"
set "EXTRACT_DIR=%TEMP%\home"
set "EXECUTABLE_NAME=server_run.exe"
set "EXCLUDE_DIR=writable"
set "PORT=928"

echo Checking if %EXECUTABLE_NAME% is running...
tasklist /FI "IMAGENAME eq %EXECUTABLE_NAME%" | find /I "%EXECUTABLE_NAME%" >nul

if %ERRORLEVEL% neq 1 (
    echo %EXECUTABLE_NAME% is currently running.

    :: End program.
    echo Closing %EXECUTABLE_NAME%...
    taskkill /F /IM %EXECUTABLE_NAME%
    if %ERRORLEVEL% neq 0 (
        echo Failed to close %EXECUTABLE_NAME%.
        pause
        exit /b 1
    )
)

:: Download update zip file.
echo Downloading update file...
powershell -command "Start-BitsTransfer -Source %URL% -Destination %DOWNLOAD_DIR% -ErrorAction Stop"

:: Check if the download is successful.
if %ERRORLEVEL% neq 0 (
    echo Failed to download the update file.
    exit /b 1
)

:: Unzip the file to the temporary folder.
echo Extracting update files...
mkdir %EXTRACT_DIR%
powershell -command "Expand-Archive -Path '%DOWNLOAD_DIR%' -DestinationPath '%EXTRACT_DIR%'"

:: Check if unzip is successful.
if %ERRORLEVEL% neq 0 (
    echo Failed to extract the update file.
    exit /b 1
)

:: Delete original file.
echo Removing old files, excluding the "write" folder...
for /d %%i in ("%INSTALL_DIR%\*") do (
    :: Exclude specific folders.
    if /I not "%%~nxi"=="%EXCLUDE_DIR%" (
        rmdir /s /q "%%i"
    )
)
for %%i in ("%INSTALL_DIR%\*") do (
    :: Exclude specific files.
    if not "%%~nxi"=="update.bat" (
        del /f /q "%%i"
    )
)

:: Copy the new file to the installation folder.
echo Copying new files to installation directory, excluding the "write" folder...
robocopy "%EXTRACT_DIR%/home" %INSTALL_DIR% /mir /xd %EXCLUDE_DIR% /xf update.bat

:: Clean up temporary files.
echo Cleaning up temporary files...
rmdir /s /q %EXTRACT_DIR%
del /f /q %DOWNLOAD_DIR%

start "" "%INSTALL_DIR%/server_run.exe"
echo Update completed successfully.
pause

