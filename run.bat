@echo off

echo CLEARING LOG FILE
del /Q classification-output\*.txt

del /Q result/*

echo EXEC GHIDRIFF
setlocal
if exist .env (
    for /f "usebackq delims=" %%a in (.env) do set %%a
)
python pipeline.py

endlocal