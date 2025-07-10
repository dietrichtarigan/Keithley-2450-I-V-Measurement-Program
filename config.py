"""
Configuration settings for the I-V Curve Measurement application
---------------------------------------------------------------
This module contains all configurable parameters for the application.
"""

# Application settings
APP_TITLE = "I-V Curve Measurement"
WINDOW_SIZE = "900x700"
WINDOW_MIN_SIZE = (1000, 600)

# Default measurement parameters
DEFAULT_GPIB_ADDRESS = "18"
DEFAULT_START_VOLTAGE = "-1"
DEFAULT_STOP_VOLTAGE = "1"
DEFAULT_NUM_STEPS = "101"
DEFAULT_CURRENT_LIMIT = "0.1"
DEFAULT_DELAY = "0.1"
DEFAULT_CURRENT_RANGE = "Auto"

# Current range options
CURRENT_RANGE_OPTIONS = ["Auto", "10 nA", "100 nA", "1 µA", "10 µA", "100 µA", "1 mA", "10 mA", "100 mA"]

# Current range conversion factors
CURRENT_RANGE_FACTORS = {
    "nA": 1e-9,   # Nano-amps to amps
    "µA": 1e-6,   # Micro-amps to amps
    "mA": 1e-3    # Milli-amps to amps
}

# File settings
CSV_EXTENSION = ".csv"
CSV_FILETYPES = [("CSV files", "*.csv"), ("All files", "*.*")]
CSV_HEADER = ['Voltage (V)', 'Current (A)', 'Resistance (Ω)']
CSV_DIALOG_TITLE = "Save measurement data"

# Plot settings
PLOT_TITLE = "I-V Curve"
PLOT_X_LABEL = "Voltage (V)"
PLOT_Y_LABEL = "Current (A)"
PLOT_STYLE = 'b.-'  # Blue line with dots
PLOT_GRID = True
FIGURE_SIZE = (6, 4)
FIGURE_DPI = 100

# Status messages
MSG_NOT_CONNECTED = "Not Connected"
MSG_CONNECTING = "Connecting..."
MSG_CONNECTION_FAILED = "Connection Failed"
MSG_MEASUREMENT_STARTED = "Measurement started..."
MSG_MEASUREMENT_COMPLETED = "Measurement completed"
MSG_MEASUREMENT_ABORTED = "Measurement aborted"
MSG_READY = "Ready"

# Error messages
ERR_NOT_CONNECTED = "Not connected to instrument"
ERR_GPIB_ADDRESS = "GPIB address must be an integer"
ERR_STEPS_TOO_FEW = "Number of steps must be at least 2"
ERR_NEGATIVE_DELAY = "Delay cannot be negative"
ERR_CURRENT_LIMIT = "Current limit must be greater than 0"
ERR_SETUP_FAILED = "Failed to setup instrument"
ERR_NO_DATA = "No data to save"
ERR_SAVE_FAILED = "Failed to save data to "

# Confirmation dialogs
CONFIRM_QUIT_MEASUREMENT = "A measurement is in progress. Do you really want to quit?"

# SMU Settings
SMALL_CURRENT_THRESHOLD = 1e-12  # Threshold for avoiding division by very small currents
