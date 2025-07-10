"""
GPIB Helper Module for Keithley 2450 I-V Measurement Program
------------------------------------------------------------
This file adds support for various types of GPIB and VISA connections
to ensure the program can connect to instruments despite driver issues.
"""

import sys
import time
import pyvisa

def get_resource_manager(visa_library=None):
    """
    Try to obtain a VISA Resource Manager using several methods.
    
    Args:
        visa_library: Path to the VISA library to use, optional
        
    Returns:
        ResourceManager object or None if failed
    """
    try:
        # Method 1: Standard PyVISA
        return pyvisa.ResourceManager(visa_library)
    except Exception as e:
        print(f"Error creating ResourceManager: {e}")
        try:
            # Method 2: Use PyVISA-py backend
            return pyvisa.ResourceManager('@py')
        except Exception as e:
            print(f"Error creating ResourceManager with @py backend: {e}")
            return None

def get_instrument_connection(gpib_address, attempts=3):
    """
    Try to connect to an instrument using several different methods.
    
    Args:
        gpib_address: GPIB address of the instrument
        attempts: Number of connection attempts
        
    Returns:
        Instrument object or None if failed
    """
    for attempt in range(attempts):
        print(f"Attempting to connect to instrument (attempt {attempt+1}/{attempts})...")
        
        # Try with standard ResourceManager
        try:
            rm = get_resource_manager()
            if rm:
                # Try with different GPIB formats
                for resource_format in [
                    f"GPIB0::{gpib_address}::INSTR",  # Standard NI-VISA format
                    f"GPIB::{gpib_address}::INSTR",   # Alternative format
                    f"GPIB{gpib_address}",            # Short format
                    f"GPIB::{gpib_address}"           # Alternative short format
                ]:
                    try:
                        print(f"Trying resource string: {resource_format}")
                        instrument = rm.open_resource(resource_format)
                        print(f"Successfully connected with resource string: {resource_format}")
                        return instrument
                    except Exception as e:
                        print(f"  - Failed with format {resource_format}: {e}")
        except Exception as e:
            print(f"Failed to create connection with ResourceManager: {e}")
        
        # Try with PyVISA-py backend
        try:
            rm_py = get_resource_manager('@py')
            if rm_py:
                resources = rm_py.list_resources()
                print(f"Resources detected by PyVISA-py: {resources}")
                
                for resource in resources:
                    if str(gpib_address) in resource:
                        try:
                            instrument = rm_py.open_resource(resource)
                            print(f"Successfully connected with resource: {resource}")
                            return instrument
                        except Exception as e:
                            print(f"  - Failed to connect to {resource}: {e}")
        except Exception as e:
            print(f"Error when trying with PyVISA-py: {e}")
        
        if attempt < attempts - 1:
            print(f"Connection attempt failed. Trying again in 2 seconds...")
            time.sleep(2)
    
    print("All connection attempts failed.")
    return None

def check_gpib_libraries():
    """
    Check the availability of GPIB libraries in the system.
    
    Returns:
        dict: Information about detected libraries
    """
    result = {
        "pyvisa": False,
        "pyvisa-py": False,
        "gpib-ctypes": False,
        "pyusb": False,
        "vxi11": False,
        "ni-visa": False
    }
    
    # Check PyVISA
    try:
        import pyvisa
        result["pyvisa"] = True
        print(f"PyVISA detected, version: {pyvisa.__version__}")
        
        # Check if NI-VISA is installed
        try:
            rm = pyvisa.ResourceManager()
            result["ni-visa"] = True
            print(f"NI-VISA detected, path: {rm.visalib}")
        except Exception:
            print("NI-VISA not detected or cannot be accessed")
            
    except ImportError:
        print("PyVISA not installed")
    
    # Check PyVISA-py
    try:
        import pyvisa_py
        result["pyvisa-py"] = True
        print(f"PyVISA-py detected, version: {pyvisa_py.__version__}")
    except ImportError:
        print("PyVISA-py not installed")
    
    # Check gpib-ctypes
    try:
        import gpib_ctypes
        result["gpib-ctypes"] = True
        print("gpib-ctypes detected")
    except ImportError:
        print("gpib-ctypes not installed")
    
    # Check pyusb
    try:
        import usb.core
        result["pyusb"] = True
        print("pyusb detected")
    except ImportError:
        print("pyusb not installed")
    
    # Check python-vxi11
    try:
        import vxi11
        result["vxi11"] = True
        print("python-vxi11 detected")
    except ImportError:
        print("python-vxi11 not installed")
    
    return result

# Function to use in the main application
def connect_to_instrument_safely(gpib_address):
    """
    Safe function to connect to an instrument, with error handling.
    
    Args:
        gpib_address: GPIB address of the instrument
        
    Returns:
        tuple: (instrument, error_message)
    """
    print("Checking available GPIB libraries...")
    check_gpib_libraries()
    
    print(f"\nAttempting to connect to instrument at GPIB address {gpib_address}...")
    instrument = get_instrument_connection(gpib_address)
    
    if instrument:
        try:
            # Test connection with basic command
            idn = instrument.query('*IDN?').strip()
            print(f"Successfully connected to: {idn}")
            return instrument, None
        except Exception as e:
            error_msg = f"Connection successful but failed to communicate with instrument: {str(e)}"
            print(error_msg)
            return None, error_msg
    else:
        error_msg = "Failed to connect to instrument. See TROUBLESHOOTING.md for more information."
        return None, error_msg
