@echo off
setlocal

call conda activate home
cd %~dp0

pip install pyinstaller
pyinstaller -y server_run.spec

set SOURCE_DIR=%~dp0
set DEST_DIR=%~dp0\dist\home
xcopy "%SOURCE_DIR%\templates\" "%DEST_DIR%\templates\" /s /e /i /y
xcopy "%SOURCE_DIR%\static\" 	"%DEST_DIR%\static\" 	/s /e /i /y
xcopy "%SOURCE_DIR%\writable\" 	"%DEST_DIR%\writable\" 	/s /e /i /y
xcopy "%SOURCE_DIR%\update.bat" "%DEST_DIR%" /y

set FOLDER_TO_COMPRESS=%DEST_DIR%\*
set OUTPUT_FILE=%DEST_DIR%.zip
powershell -command "Compress-Archive -Path '%FOLDER_TO_COMPRESS%' -Force -DestinationPath '%OUTPUT_FILE%'"

echo completed.

pause
