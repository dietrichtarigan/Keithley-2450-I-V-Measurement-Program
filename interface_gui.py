#!/usr/bin/env python3
"""
Interface MOdule for Keithley 2450 I-V Measurement Program
------------------------
This module provides a graphical user interface for the SMU Logic module to
perform I-V curve measurements using a Keithley 2450 SMU.
"""

import os
import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import threading

# Import our SMU logic module
from main import SMUController, save_data_to_csv

# Import configuration settings
import config

class IVCurveGUI:
    """Class implementing the GUI for I-V curve measurements"""
    
    def __init__(self, root):
        """Initialize the GUI window and elements"""
        self.root = root
        self.root.title(config.APP_TITLE)
        self.root.geometry(config.WINDOW_SIZE)
        self.root.minsize(config.WINDOW_MIN_SIZE[0], config.WINDOW_MIN_SIZE[1])
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Initialize the SMU controller
        self.smu_controller = SMUController()
        
        # Data storage
        self.voltages = []
        self.currents = []
        self.resistances = []
        
        # Flag for measurement status
        self.measurement_running = False
        
        # Create the GUI elements
        self.create_gui_elements()
        
        # Create the plot area
        self.create_plot_area()
    
    def create_gui_elements(self):
        """Create all GUI elements: frames, labels, inputs, buttons"""
        # Main frame for controls
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # =============================================================
        # Connection Frame
        # =============================================================
        connection_frame = ttk.LabelFrame(main_frame, text="Connection Settings", padding="10")
        connection_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(connection_frame, text="GPIB Address:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.gpib_address = ttk.Entry(connection_frame, width=10)
        self.gpib_address.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        self.gpib_address.insert(0, config.DEFAULT_GPIB_ADDRESS)  # Default GPIB address
        
        self.connect_button = ttk.Button(connection_frame, text="Connect", command=self.connect_to_instrument)
        self.connect_button.grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Add button to change GPIB address remotely
        self.change_addr_button = ttk.Button(connection_frame, text="Change GPIB", command=self.change_gpib_address, state=tk.DISABLED)
        self.change_addr_button.grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        
        self.connection_status = ttk.Label(connection_frame, text=config.MSG_NOT_CONNECTED, foreground="red")
        self.connection_status.grid(row=0, column=4, sticky=tk.W, padx=5, pady=5)
        
        # =============================================================
        # Measurement Parameters Frame
        # =============================================================
        params_frame = ttk.LabelFrame(main_frame, text="Measurement Parameters", padding="10")
        params_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # First row - Voltage parameters
        ttk.Label(params_frame, text="Start Voltage (V):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.start_voltage = ttk.Entry(params_frame, width=10)
        self.start_voltage.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        self.start_voltage.insert(0, config.DEFAULT_START_VOLTAGE)
        
        ttk.Label(params_frame, text="Stop Voltage (V):").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.stop_voltage = ttk.Entry(params_frame, width=10)
        self.stop_voltage.grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        self.stop_voltage.insert(0, config.DEFAULT_STOP_VOLTAGE)
        
        ttk.Label(params_frame, text="Number of Steps:").grid(row=0, column=4, sticky=tk.W, padx=5, pady=5)
        self.num_steps = ttk.Entry(params_frame, width=10)
        self.num_steps.grid(row=0, column=5, sticky=tk.W, padx=5, pady=5)
        self.num_steps.insert(0, config.DEFAULT_NUM_STEPS)
        
        # Second row - Current parameters
        ttk.Label(params_frame, text="Current Limit (A):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.current_limit = ttk.Entry(params_frame, width=10)
        self.current_limit.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        self.current_limit.insert(0, config.DEFAULT_CURRENT_LIMIT)
        
        ttk.Label(params_frame, text="Current Range:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        self.current_range = ttk.Combobox(params_frame, width=10, values=config.CURRENT_RANGE_OPTIONS)
        self.current_range.grid(row=1, column=3, sticky=tk.W, padx=5, pady=5)
        self.current_range.set(config.DEFAULT_CURRENT_RANGE)  # Set default range
        
        ttk.Label(params_frame, text="Delay (s):").grid(row=1, column=4, sticky=tk.W, padx=5, pady=5)
        self.delay_time = ttk.Entry(params_frame, width=10)
        self.delay_time.grid(row=1, column=5, sticky=tk.W, padx=5, pady=5)
        self.delay_time.insert(0, config.DEFAULT_DELAY)
        
        # =============================================================
        # Control Buttons Frame
        # =============================================================
        control_frame = ttk.Frame(main_frame, padding="10")
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.start_button = ttk.Button(control_frame, text="Start Measurement", command=self.start_measurement)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.abort_button = ttk.Button(control_frame, text="Abort", command=self.abort_measurement, state=tk.DISABLED)
        self.abort_button.pack(side=tk.LEFT, padx=5)
        
        self.save_button = ttk.Button(control_frame, text="Save Data", command=self.save_data, state=tk.DISABLED)
        self.save_button.pack(side=tk.LEFT, padx=5)
        
        # =============================================================
        # Progress Frame
        # =============================================================
        progress_frame = ttk.Frame(main_frame, padding="10")
        progress_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(progress_frame, text="Progress:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100, length=400)
        self.progress_bar.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # Measurement info
        self.measurement_info = ttk.Label(progress_frame, text=config.MSG_READY)
        self.measurement_info.grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
    
    def create_plot_area(self):
        """Create the matplotlib plot area"""
        plot_frame = ttk.Frame(self.root, padding="10")
        plot_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create matplotlib figure
        self.figure = Figure(figsize=config.FIGURE_SIZE, dpi=config.FIGURE_DPI)
        self.plot = self.figure.add_subplot(111)
        self.plot.set_title(config.PLOT_TITLE)
        self.plot.set_xlabel(config.PLOT_X_LABEL)
        self.plot.set_ylabel(config.PLOT_Y_LABEL)
        self.plot.grid(config.PLOT_GRID)
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.figure, master=plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def connect_to_instrument(self):
        """Connect to the SMU instrument"""
        try:
            gpib_addr = int(self.gpib_address.get())
            
            # Disable connect button during connection attempt
            self.connect_button.config(state=tk.DISABLED)
            self.connection_status.config(text=config.MSG_CONNECTING, foreground="blue")
            self.root.update()
            
            # Try to connect
            success, message = self.smu_controller.connect_to_instrument(gpib_addr)
            
            if success:
                self.connection_status.config(text=message, foreground="green")
                # Enable measurement controls
                self.start_button.config(state=tk.NORMAL)
                self.change_addr_button.config(state=tk.NORMAL)  # Enable GPIB change button
            else:
                messagebox.showerror("Connection Error", message)
                self.connection_status.config(text=config.MSG_CONNECTION_FAILED, foreground="red")
            
        except ValueError:
            messagebox.showerror("Input Error", config.ERR_GPIB_ADDRESS)
        finally:
            self.connect_button.config(state=tk.NORMAL)
    
    def change_gpib_address(self):
        """Open dialog to change GPIB address remotely using SCPI and TSP commands"""
        if not self.smu_controller.instrument:
            messagebox.showerror("Error", "Not connected to any instrument")
            return
        
        # Ask for the new GPIB address
        from tkinter.simpledialog import askinteger
        new_address = askinteger("Change GPIB Address", 
                                "Enter new GPIB address (0-30):",
                                minvalue=0, maxvalue=30)
        
        if new_address is None:  # User cancelled
            return
            
        # Try to change the address
        success, message = self.smu_controller.set_gpib_address(new_address)
        
        if success:
            messagebox.showinfo("GPIB Address Change", message)
        else:
            messagebox.showerror("GPIB Address Change Failed", message)
    
    def update_progress(self, voltage, current, resistance, progress):
        """Update progress bar and display current measurement values"""
        if not self.measurement_running:
            return
            
        # Update progress bar
        self.progress_var.set(progress)
        
        # Update measurement info text
        self.measurement_info.config(text=f"V: {voltage:.4f} V, I: {current*1000:.6f} mA, R: {resistance:.2f} Ω")
        
        # Update the plot
        self.update_plot()
        
        # Force GUI update
        self.root.update_idletasks()
    
    def start_measurement(self):
        """Start the measurement process"""
        if not self.smu_controller.instrument:
            messagebox.showerror("Error", "Not connected to instrument")
            return
            
        try:
            # Get parameters
            start_v = float(self.start_voltage.get())
            stop_v = float(self.stop_voltage.get())
            steps = int(self.num_steps.get())
            current_limit = float(self.current_limit.get())
            
            # Parse current range
            curr_range_str = self.current_range.get()
            if curr_range_str == "Auto":
                current_range = "AUTO"
            else:
                # Convert from display units to Amps
                range_val = curr_range_str.split()[0]
                unit = curr_range_str.split()[1]
                
                if unit == "nA":
                    current_range = str(float(range_val) * 1e-9)
                elif unit == "µA":
                    current_range = str(float(range_val) * 1e-6)
                elif unit == "mA":
                    current_range = str(float(range_val) * 1e-3)
                else:
                    current_range = range_val
            
            delay = float(self.delay_time.get())
            
            # Validate inputs
            if steps < 2:
                messagebox.showerror("Input Error", "Number of steps must be at least 2")
                return
                
            if delay < 0:
                messagebox.showerror("Input Error", "Delay cannot be negative")
                return
                
            if current_limit <= 0:
                messagebox.showerror("Input Error", "Current limit must be greater than 0")
                return
            
            # Setup instrument
            setup_success = self.smu_controller.setup_measurement(start_v, stop_v, current_limit, current_range)
            if not setup_success:
                messagebox.showerror("Setup Error", "Failed to setup instrument")
                return
            
            # Clear old data
            self.voltages = []
            self.currents = []
            self.resistances = []
            
            # Update UI state
            self.measurement_running = True
            self.start_button.config(state=tk.DISABLED)
            self.abort_button.config(state=tk.NORMAL)
            self.save_button.config(state=tk.DISABLED)
            self.progress_var.set(0)
            self.measurement_info.config(text=config.MSG_MEASUREMENT_STARTED)
            
            # Start measurement in a new thread
            self.measurement_thread = threading.Thread(
                target=self.run_measurement_thread,
                args=(start_v, stop_v, steps, delay)
            )
            self.measurement_thread.daemon = True
            self.measurement_thread.start()
            
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input: {str(e)}")
    
    def run_measurement_thread(self, start_v, stop_v, steps, delay):
        """Run the measurement in a separate thread"""
        try:
            # Perform the sweep
            self.voltages, self.currents, self.resistances = self.smu_controller.perform_sweep(
                start_v, stop_v, steps, delay, self.update_progress
            )
            
            # Update the GUI from the main thread
            self.root.after(0, self.measurement_completed)
        except Exception as e:
            # Handle errors and update the GUI
            self.root.after(0, lambda: self.show_error(f"Measurement error: {str(e)}"))
    
    def measurement_completed(self):
        """Called when measurement is completed"""
        self.measurement_running = False
        self.start_button.config(state=tk.NORMAL)
        self.abort_button.config(state=tk.DISABLED)
        self.save_button.config(state=tk.NORMAL)
        self.measurement_info.config(text=config.MSG_MEASUREMENT_COMPLETED)
        self.progress_var.set(100)
        
        # Final plot update
        self.update_plot()
    
    def abort_measurement(self):
        """Abort an ongoing measurement"""
        if self.measurement_running:
            self.smu_controller.abort_measurement()
            self.measurement_running = False
            self.start_button.config(state=tk.NORMAL)
            self.abort_button.config(state=tk.DISABLED)
            if len(self.voltages) > 0:
                self.save_button.config(state=tk.NORMAL)
            self.measurement_info.config(text=config.MSG_MEASUREMENT_ABORTED)
    
    def update_plot(self):
        """Update the I-V curve plot"""
        if len(self.voltages) == 0:
            return
            
        self.plot.clear()
        self.plot.set_title(config.PLOT_TITLE)
        self.plot.set_xlabel(config.PLOT_X_LABEL)
        self.plot.set_ylabel(config.PLOT_Y_LABEL)
        self.plot.grid(config.PLOT_GRID)
        
        # Plot the I-V curve
        self.plot.plot(self.voltages, self.currents, config.PLOT_STYLE)
        
        # Draw the canvas
        self.canvas.draw()
    
    def save_data(self):
        """Save measurement data to a CSV file"""
        if len(self.voltages) == 0:
            messagebox.showinfo("Info", config.ERR_NO_DATA)
            return
            
        # Ask for file location
        file_path = filedialog.asksaveasfilename(
            defaultextension=config.CSV_EXTENSION,
            filetypes=config.CSV_FILETYPES,
            title=config.CSV_DIALOG_TITLE
        )
        
        if not file_path:  # User cancelled
            return
            
        # Save data
        if save_data_to_csv(file_path, self.voltages, self.currents, self.resistances, config.CSV_HEADER):
            messagebox.showinfo("Success", f"Data saved to {file_path}")
        else:
            messagebox.showerror("Error", f"{config.ERR_SAVE_FAILED}{file_path}")
    
    def show_error(self, message):
        """Show an error message"""
        messagebox.showerror("Error", message)
        self.measurement_running = False
        self.start_button.config(state=tk.NORMAL)
        self.abort_button.config(state=tk.DISABLED)
        if len(self.voltages) > 0:
            self.save_button.config(state=tk.NORMAL)
    
    def on_closing(self):
        """Handle window closing"""
        if self.measurement_running:
            if messagebox.askokcancel("Quit", config.CONFIRM_QUIT_MEASUREMENT):
                self.abort_measurement()
            else:
                return
                
        # Close connection to instrument
        if self.smu_controller:
            self.smu_controller.close()
            
        # Close the window
        self.root.destroy()


def main():
    """Main function to start the application"""
    root = tk.Tk()
    app = IVCurveGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()