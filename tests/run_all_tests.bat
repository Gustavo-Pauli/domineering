@echo off
echo =============================================
echo         Domineering Game - Board Tests
echo =============================================
echo.
echo Running Unit Tests...
echo.
python .\test_board_unit.py
echo.
echo =============================================
echo.
echo Unit tests completed!
echo.
set /p choice="Do you want to run GUI tests too? (y/n): "
if /i "%choice%"=="y" (
    echo.
    echo Starting GUI tests...
    python .\test_board_view.py
) else (
    echo.
    echo Skipping GUI tests.
)
echo.
echo All tests completed!
pause
