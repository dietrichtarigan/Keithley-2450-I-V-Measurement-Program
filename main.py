#!/usr/bin/env python3
"""
Logic Module for I-V Curve Measurement
-----------------------------------------
This module contains the core functionality for controlling a Keithley 2450 SMU
and performing I-V measurements without any GUI dependencies.

It provides functions for:
- Connecting to SMU devices
- Configuring measurement parameters
- Performing voltage sweeps
- Calculating results
"""

import time
import numpy as np
import pyvisa
import config  # Import configuration settings

class SMUController:
    """Class to handle SMU instrument control and measurement logic"""
    
    def __init__(self):
        """Initialize the SMU controller"""
        self.instrument = None
        self.measurement_running = False
    
    def connect_to_instrument(self, gpib_addr):
        """
        Connect to the Keithley 2450 SMU using either gpib_helper module or standard PyVISA
        
        Args:
            gpib_addr (int): GPIB address of the instrument
            
        Returns:
            tuple: (success, message)
        """
        try:
            # Try to connect using gpib_helper if available
            try:
                import gpib_helper
                instrument, error = gpib_helper.connect_to_instrument_safely(gpib_addr)
                if instrument:
                    self.instrument = instrument
                    idn = self.instrument.query('*IDN?').strip()
                    return True, f"Connected to {idn}"
                elif error:
                    raise Exception(error)
            except ImportError:
                # Fall back to standard connection methods if helper not available
                try:
                    # Method 1: Standard PyVISA
                    rm = pyvisa.ResourceManager()
                    self.instrument = rm.open_resource(f'GPIB0::{gpib_addr}::INSTR')
                except Exception as e1:
                    try:
                        # Method 2: PyVISA-py backend
                        rm = pyvisa.ResourceManager('@py')
                        self.instrument = rm.open_resource(f'GPIB0::{gpib_addr}::INSTR')
                    except Exception as e2:
                        return False, f"Failed to connect with all methods:\n1. {str(e1)}\n2. {str(e2)}"
            
            # Reset the instrument and clear errors
            self.instrument.write('*RST')
            self.instrument.write('*CLS')
            
            # Get and verify instrument identification
            idn = self.instrument.query('*IDN?').strip()
            if "MODEL 2450" not in idn.upper():
                return True, f"Warning: Connected to {idn}, which may not be a Keithley 2450 SMU"
            
            return True, f"Connected to {idn.split(',')[1]}"
            
        except Exception as e:
            return False, f"Connection error: {str(e)}"
    
    def setup_measurement(self, start_v, stop_v, current_limit, current_range):
        """
        Configure the SMU for I-V measurement
        
        Args:
            start_v (float): Start voltage for sweep
            stop_v (float): End voltage for sweep
            current_limit (float): Current compliance limit in Amps
            current_range (str): Current measurement range or 'AUTO'
            
        Returns:
            bool: True if setup successful, False otherwise
        """
        try:
            if not self.instrument:
                return False
                
            # Set to use the rear terminals
            self.instrument.write('ROUT:TERM REAR')
            
            # Set source function to voltage
            self.instrument.write('SOUR:FUNC VOLT')
            
            # Set source voltage range based on the highest voltage in the sweep
            max_voltage = max(abs(start_v), abs(stop_v))
            self.instrument.write(f'SOUR:VOLT:RANG {max_voltage}')
            
            # Set current limit
            self.instrument.write(f'SOUR:VOLT:ILIM {current_limit}')
            
            # Set measurement function to current
            self.instrument.write('SENS:FUNC "CURR"')
            
            # Set current measurement range
            if current_range.upper() == 'AUTO':
                self.instrument.write('SENS:CURR:RANG:AUTO ON')
            else:
                try:
                    current_range_val = float(current_range)
                    self.instrument.write(f'SENS:CURR:RANG {current_range_val}')
                except ValueError:
                    self.instrument.write('SENS:CURR:RANG:AUTO ON')
                    return False  # Signal the invalid range
            
            # Use NPLC of 1 for a good balance of speed and noise
            self.instrument.write('SENS:CURR:NPLC 1')
            
            # Set source readback to be ON (measure actual applied voltage)
            self.instrument.write('SOUR:VOLT:READ ON')
            
            return True
            
        except Exception as e:
            if self.instrument:
                self.instrument.write('OUTP OFF')  # Safety: turn off output
            return False
    
    def start_output(self):
        """Turn on the SMU output"""
        if self.instrument:
            self.instrument.write('OUTP ON')
            return True
        return False
    
    def stop_output(self):
        """Turn off the SMU output"""
        if self.instrument:
            self.instrument.write('OUTP OFF')
            return True
        return False
    
    def measure_point(self, voltage):
        """
        Measure current at a specific voltage point
        
        Args:
            voltage (float): Voltage to apply
            
        Returns:
            tuple: (current, resistance) or (None, None) if failed
        """
        try:
            if not self.instrument:
                return None, None
                
            # Set the voltage
            self.instrument.write(f'SOUR:VOLT {voltage}')
            
            # Measure the current
            current = float(self.instrument.query('MEAS:CURR?'))
            
            # Calculate resistance using Ohm's law (V=IR, so R=V/I)
            if abs(current) > config.SMALL_CURRENT_THRESHOLD:  # Avoid division by very small numbers
                resistance = voltage / current
            else:
                resistance = float('inf')  # Infinite resistance for zero current
                
            return current, resistance
            
        except Exception:
            return None, None
    
    def perform_sweep(self, start_v, stop_v, steps, delay_time, callback=None):
        """
        Perform a voltage sweep and measure current at each point
        
        Args:
            start_v (float): Start voltage
            stop_v (float): Stop voltage
            steps (int): Number of steps
            delay_time (float): Delay between measurements in seconds
            callback (function): Optional callback function for progress updates
                                The callback receives (voltage, current, resistance, progress)
                                
        Returns:
            tuple: (voltages, currents, resistances)
        """
        voltages = []
        currents = []
        resistances = []
        
        # Calculate voltage step size
        voltage_step = (stop_v - start_v) / (steps - 1)
        
        # Turn on output
        self.start_output()
        self.measurement_running = True
        
        # Perform sweep
        for i in range(steps):
            if not self.measurement_running:
                break
            
            # Calculate voltage for this step
            voltage = start_v + (i * voltage_step)
            
            # Measure at this point
            current, resistance = self.measure_point(voltage)
            
            if current is None:  # Measurement failed
                continue
                
            # Store results
            voltages.append(voltage)
            currents.append(current)
            resistances.append(resistance)
            
            # Wait for specified delay time
            time.sleep(delay_time)
            
            # Call progress callback if provided
            if callback:
                progress = 100 * (i + 1) / steps
                callback(voltage, current, resistance, progress)
        
        # Turn off output when done
        self.stop_output()
        self.measurement_running = False
        
        return voltages, currents, resistances
    
    def abort_measurement(self):
        """Abort an ongoing measurement"""
        self.measurement_running = False
        self.stop_output()
    
    def close(self):
        """Close the connection to the instrument"""
        if self.instrument:
            try:
                self.stop_output()
                self.instrument.close()
                self.instrument = None
                return True
            except:
                return False
        return True
    
    def set_gpib_address(self, new_address):
        """
        Set the GPIB address of the instrument using remote commands
        
        This function changes the GPIB address of the connected Keithley 2450 SMU
        without requiring physical access to the instrument's front panel.
        It uses the SCPI command :SYSTem:GPIB:ADDRess followed by the TSP command
        gpib.address to verify the change.
        
        Note: This change will take effect after a power cycle or reset of the instrument.
        The current connection will not be affected.
        
        Args:
            new_address (int): New GPIB address to set (0-30)
            
        Returns:
            tuple: (success, message) where success is a boolean indicating if the
                  operation was successful, and message contains information about
                  the operation result or error.
        """
        if not self.instrument:
            return False, "Not connected to any instrument"
        
        try:
            # Validate the address range
            if not (0 <= new_address <= 30):
                return False, "GPIB address must be between 0 and 30"
            
            # Get current address first for confirmation
            try:
                # Try TSP command to get current address
                current_address = self.instrument.query("print(gpib.address)")
                current_address = int(current_address.strip())
            except:
                # If TSP command fails, try SCPI query
                try:
                    current_address = self.instrument.query(":SYSTem:GPIB:ADDRess?")
                    current_address = int(current_address.strip())
                except:
                    current_address = "unknown"
            
            # Send SCPI command to change the address
            self.instrument.write(f":SYSTem:GPIB:ADDRess {new_address}")
            
            # Verify the change using TSP command
            try:
                # Try TSP command first
                verified_address = self.instrument.query("print(gpib.address)")
                verified_address = int(verified_address.strip())
                
                if verified_address == new_address:
                    return True, f"GPIB address successfully changed from {current_address} to {new_address}. The change will take effect after instrument reset or power cycle."
                else:
                    return False, f"GPIB address change verification failed. Current address: {verified_address}"
                    
            except Exception as e:
                # If TSP command fails, return success but warn that verification failed
                return True, f"GPIB address command sent successfully, but verification failed: {str(e)}. Please check the instrument after reset."
        
        except Exception as e:
            return False, f"Error changing GPIB address: {str(e)}"
        

def save_data_to_csv(filename, voltages, currents, resistances, header=None):
    """
    Save measurement data to a CSV file
    
    Args:
        filename (str): Path to save the CSV file
        voltages (list): List of voltage values
        currents (list): List of current values
        resistances (list): List of calculated resistance values
        header (list, optional): Header row for CSV file. Uses config.CSV_HEADER if not provided.
        
    Returns:
        bool: True if saved successfully, False otherwise
    """
    import csv
    
    try:
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header using config if available
            if header is None:
                header = config.CSV_HEADER
            writer.writerow(header)
            
            # Write data
            for v, i, r in zip(voltages, currents, resistances):
                writer.writerow([v, i, r])
        
        return True
    except Exception:
        return False

