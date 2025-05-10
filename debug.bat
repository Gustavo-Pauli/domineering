@echo off
echo Starting first python instance...
start "Python1" cmd /k python main.py

echo Starting second python instance...
start "Python2" cmd /k python main.py

echo Both processes started.
pause