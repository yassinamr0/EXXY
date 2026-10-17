@echo off
rem Renders the EXXY terrace on this Windows laptop's NVIDIA graphics card.
rem Double-click this file, or run it from a terminal in the project folder.
rem Needs Blender 5.2 installed from blender.org (default install location).

set BLENDER="C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
if not exist %BLENDER% (
  echo Blender 5.2 was not found. Install it from https://www.blender.org/download/
  pause
  exit /b 1
)

cd /d "%~dp0"
echo Downloading the free Poly Haven textures, plants and sky (first time only)...
%BLENDER% --background --python blender\fetch_assets.py
echo Rendering the phone-format still on the graphics card...
%BLENDER% --background --python blender\terrace.py -- --gpu --out renders\still_phone.png
echo Done. The image is in the renders folder.
pause
