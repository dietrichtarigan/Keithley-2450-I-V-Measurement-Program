@echo off
echo Running Keithley 2450 I-V Curve Measurement Program...
echo.

REM Check if Python is available
python --version >nul 2>&1
if %ERRORLEVEL% == 0 (
    REM Python installed, check Python script
    if exist "interface_gui.py" (
        echo Python detected. Setting up environment...
        
        REM Check if virtual environment exists, create if it doesn't
        if not exist "venv\" (
            echo Creating virtual environment...
            python -m venv venv
            if %ERRORLEVEL% NEQ 0 (
                echo Failed to create virtual environment!
                echo Trying to proceed with system Python...
            ) else (
                echo Virtual environment created successfully.
            )
        ) else (
            echo Virtual environment already exists.
        )
        
        REM Activate the virtual environment if it exists
        if exist "venv\" (
            echo Activating virtual environment...
            call venv\Scripts\activate.bat
            
            echo Upgrading pip in virtual environment...
            python -m pip install --upgrade pip
            
            REM Install dependencies from requirements.txt if it exists
            if exist "requirements.txt" (
                echo Installing dependencies from requirements.txt...
                python -m pip install -r requirements.txt
            ) else (
                echo No requirements.txt found. Installing individual packages...
                
                REM Install basic dependencies
                echo Installing NumPy and Matplotlib...
                python -m pip install numpy matplotlib
                
                REM Install PyVISA and related components
                echo Installing PyVISA and instrument communication drivers...
                python -m pip install pyvisa pyvisa-py
                
                REM Install GPIB drivers
                echo Installing GPIB drivers for Windows...
                python -m pip install gpib-ctypes
                
                REM Install additional packages, ensuring PyUSB is properly installed
                echo Installing additional packages to help with GPIB connections...
                python -m pip install pywin32 python-vxi11 pyusb
                
                REM Explicitly install PyUSB for USB device access
                echo Installing PyUSB for USB device communication...
                python -m pip install pyusb
                
                REM Create requirements.txt for future use
                echo Creating requirements.txt file...
                pip freeze > requirements.txt
                echo Requirements file created.
            )
        ) else (
            REM If venv creation failed, fall back to system Python
            echo Installing dependencies to system Python...
            
            REM Install basic dependencies
            echo Installing NumPy and Matplotlib...
            python -m pip install numpy matplotlib
            
            REM Install PyVISA and related components
            echo Installing PyVISA and instrument communication drivers...
            python -m pip install pyvisa pyvisa-py
            
            REM Install GPIB drivers
            echo Installing GPIB drivers for Windows...
            python -m pip install gpib-ctypes
            
            REM Install additional packages, ensuring PyUSB is properly installed
            echo Installing additional packages to help with GPIB connections...
            python -m pip install pywin32 python-vxi11
            
            REM Explicitly install PyUSB for USB device access
            echo Installing PyUSB for USB device communication...
            python -m pip install pyusb
        )
        
        echo.
        REM Run the GUI program directly
        echo Running I-V measurement program...
        
        REM If using venv and it exists
        if exist "venv\Scripts\python.exe" (
            echo Starting application with virtual environment...
            start venv\Scripts\python.exe interface_gui.py
        ) else (
            echo Starting application with system Python...
            start python interface_gui.py
        )
        
        REM Deactivate virtual environment if using it
        if exist "venv\Scripts\activate.bat" (
            call venv\Scripts\deactivate.bat
        )
        
        exit /b 0
    )
)

REM If Python is not available or script not found, try running executable
if exist "dist\iv_measurement_gui.exe" (
    echo Python not found or script missing. Running executable version...
    start "" "dist\iv_measurement_gui.exe"
    exit /b 0
)

REM If we get here, it means we couldn't run the program
echo [ERROR] Unable to run the program!
echo.
echo Possible issues:
echo 1. Python is not installed
echo 2. File interface_gui.py not found
echo 3. Executable file dist\iv_measurement_gui.exe does not exist
echo.
echo Installing Python:
echo   - Download from https://www.python.org/downloads/
echo   - Make sure to check "Add Python to PATH" during installation
echo.
echo After installing Python, run this batch file again.
pause
exit /b 1
