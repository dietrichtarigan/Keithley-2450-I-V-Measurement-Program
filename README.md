# Keithley 2450 SMU I-V Curve Measurement Application

A modular, fully configurable GUI application for I-V curve measurements using the Keithley 2450 Source Measure Unit (SMU) via GPIB interface. This application allows users to perform voltage sweeps, measure currents, calculate resistances, and visualize I-V curves in real-time.

<img width="1002" height="889" alt="python_lBEZjC15Bx" src="https://github.com/user-attachments/assets/c215aa82-3757-4388-bd55-94d2c4f9cee3" />

## Features

- **User-friendly graphical interface** for controlling I-V measurements
- **Real-time plotting** of I-V curves during measurement
- **Automatic resistance calculation** using Ohm's Law
- **CSV data export** for further analysis
- **Multiple GPIB connection methods** for maximum compatibility
- **Remote GPIB address configuration** directly from the application
- **Fully configurable** through a central configuration file
- **Modular architecture** separating UI, logic, and configuration

## Quick Start

### Installation

1. **Automatic Installation (Recommended)**
   
   Simply run the `run.bat` file:
   ```
   run.bat
   ```
   
   This will:
   - Check if Python is installed
   - Create a virtual environment in the `venv` folder
   - Install all required dependencies
   - Launch the application

2. **Manual Installation**

   If you prefer to install manually:
   ```
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   python interface_gui.py
   ```

### Basic Usage

1. Connect your Keithley 2450 SMU via GPIB (default address: 18)
2. Click "Connect" to establish connection
3. Set your measurement parameters:
   - Start voltage
   - Stop voltage
   - Number of steps
   - Current limit
   - Current range
   - Measurement delay
4. Click "Start Measurement" to begin the voltage sweep
5. View the I-V curve in real-time
6. Save your data to CSV when finished

## File Structure

| File               | Description                            |
| ------------------ | -------------------------------------- |
| `interface_gui.py` | Main GUI implementation using Tkinter  |
| `main.py`          | Core SMU control and measurement logic |
| `config.py`        | Centralized configuration settings     |
| `gpib_helper.py`   | Robust GPIB connection handling        |
| `requirements.txt` | Required Python packages               |
| `run.bat`          | Automated setup and launch script      |

## Detailed Component Overview

### `interface_gui.py`

The graphical user interface module built with Tkinter and Matplotlib.

**Key Classes:**
- `IVCurveGUI`: Main GUI class that:
  - Creates all UI elements (input fields, buttons, plots)
  - Handles user interactions
  - Manages the measurement workflow
  - Displays real-time data and plots
  - Provides CSV export functionality

**Key Functions:**
- `create_gui_elements()`: Creates all UI controls
- `create_plot_area()`: Sets up the Matplotlib plotting area
- `connect_to_instrument()`: Establishes connection to the SMU
- `start_measurement()`: Initiates the voltage sweep
- `change_gpib_address()`: Opens dialog to change GPIB address remotely
- `save_data()`: Saves measurement data to CSV

### `main.py`

Core functionality for controlling the Keithley 2450 SMU and performing measurements.

**Key Class:**
- `SMUController`: Handles all instrument control:
  - Connection management
  - Instrument setup and configuration
  - Voltage sweep execution
  - Current measurement and resistance calculation

**Key Methods:**
- `connect_to_instrument(gpib_addr)`: Connects to the SMU at specified GPIB address
- `setup_measurement(...)`: Configures SMU for measurement
- `perform_sweep(...)`: Executes the voltage sweep with specified parameters
- `measure_point(voltage)`: Measures current at a specific voltage
- `set_gpib_address(new_address)`: Changes GPIB address remotely

**Helper Function:**
- `save_data_to_csv(...)`: Exports measurement data to CSV file

### `config.py`

Centralized configuration module containing all user-facing settings.

**Configuration Categories:**
- Application settings (window size, title)
- Default measurement parameters
- Current range options and conversion factors
- File settings (CSV format, headers)
- Plot settings (labels, styles, colors)
- Status and error messages
- SMU-specific settings (thresholds, etc.)

### `gpib_helper.py`

Specialized module for robust GPIB communications, handling various connection methods and error recovery.

**Key Functions:**
- `get_resource_manager(visa_library)`: Obtains VISA resource manager
- `get_instrument_connection(gpib_address)`: Tries multiple methods to connect
- `check_gpib_libraries()`: Checks available GPIB libraries in the system
- `connect_to_instrument_safely(gpib_address)`: Public function with error handling

**Connection Methods:**
1. Standard PyVISA with NI-VISA backend
2. PyVISA-py backend for driver-free operation
3. Multiple GPIB address formats for compatibility

## GPIB Communication Details

The application uses multiple strategies to establish reliable GPIB communication:

1. **Library Detection**
   - Automatically detects available GPIB libraries
   - Supports NI-VISA, PyVISA-py, gpib-ctypes, pyusb, and vxi11

2. **Connection Attempts**
   - Tries multiple connection methods and formats
   - Performs automatic retries with timeouts
   - Handles connection errors gracefully

3. **Remote GPIB Configuration**
   - Sets the GPIB address remotely using SCPI commands
   - Uses the command `:SYSTem:GPIB:ADDRess <address>` 
   - Verifies changes with TSP command `gpib.address`

**Default GPIB Address:**
The default GPIB address is 18, as specified in the Keithley 2450 user manual.

## Modular Architecture

The application follows a modular design pattern:

1. **Separation of Concerns**
   - UI logic (`interface_gui.py`)
   - Business logic (`smu_logic.py`)
   - Configuration (`config.py`)
   - Helper utilities (`gpib_helper.py`)

2. **Integration Points**
   - UI references SMU logic for instrument control
   - Both UI and logic use central configuration
   - GPIB helper provides robust connection services

3. **Benefits**
   - Easy maintenance and updates
   - Clear separation between presentation and logic
   - Simple customization through configuration

## Requirements

- Python 3.6 or higher
- PyVISA and PyVISA-py for instrument communication
- Matplotlib for plotting
- Tkinter for the GUI
- PyUSB for USB device support (optional)
- Python-VXI11 for VXI-11 protocol support (optional)
- PyWin32 for Windows-specific functionality (optional)

See `requirements.txt` for the complete list of dependencies.

## Customization

To customize the application:

1. **Edit `config.py`** to change:
   - Default measurement parameters
   - Plot appearance and labels
   - Application window size and title
   - Status and error messages
   - File export settings

2. All changes in `config.py` are automatically reflected in the UI without requiring code changes.

## Troubleshooting

### Connection Issues

- Ensure the Keithley 2450 is powered on and properly connected via GPIB
- Verify the GPIB address matches (default is 18)
- Check if NI-VISA or an alternative GPIB driver is installed
- Try a different connection method through the application

### Dependency Issues

- Run `run.bat` to automatically install all required dependencies
- Check the Python version (3.6+ required)
- Manually install dependencies from `requirements.txt` if needed

## License

This application is provided under the [MIT License](LICENSE).

## Acknowledgments

- Keithley 2450 SMU instrument documentation
- PyVISA and PyVISA-py projects
- Matplotlib plotting library

---

*Documentation created for Keithley 2450 SMU I-V Curve Measurement Application*
