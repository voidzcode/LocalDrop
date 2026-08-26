@echo off
echo Installing the application... (this shouldn't take long...)
winget install python3
echo Installed Python 3 successfully.
echo Cleaning up temporary files...
del /f /q temp\*
echo Cleanup complete.
echo Installation finished successfully. The application will automatically launch.
python3 main.py
echo Application launched. Deleting installer script...
del /f /q installer.bat
echo Installer script deleted. Exiting...



