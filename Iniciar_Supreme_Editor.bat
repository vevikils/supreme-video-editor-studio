@echo off
title Iniciar Supreme Video Editor Studio
python "%~dp0supreme_video_editor.py"
if %errorlevel% neq 0 (
    echo.
    echo Ha ocurrido un error al ejecutar la aplicacion.
    pause
)
