@echo off
echo Compiling reader-writer program...
"D:/msys64/ucrt64/bin/gcc.exe" reader_writer.c -o reader_writer.exe -lpthread
if errorlevel 1 (
    echo Compilation failed!
    pause
    exit /b 1
) else (
    echo Compilation successful!
)
echo Running program...
reader_writer.exe
pause