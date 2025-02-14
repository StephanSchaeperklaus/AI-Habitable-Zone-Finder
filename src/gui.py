#!/usr/bin/env python3
"""
Graphical User Interface module for the AIHabitablezone application.
Provides a basic interface for exploring habitable zones.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from pathlib import Path
import json
from src.visualization import HabitableZoneVisualizer, embed_figure

class DarkTheme:
    """Dark theme color scheme and styles"""
    # Colors
    BG_DARK = "#1e1e1e"
    BG_MEDIUM = "#2d2d2d"
    BG_LIGHT = "#363636"
    FG_GREEN = "#4CAF50"  # Material Design Green
    FG_BRIGHT_GREEN = "#69F0AE"  # Brighter green for highlights
    ACCENT = "#00E676"  # Accent green
    TEXT_BG = "#1e1e1e"  # Dark background for text
    
    @classmethod
    def setup_theme(cls):
        """Configure ttk styles for dark theme"""
        style = ttk.Style()
        
        # Configure main styles
        style.configure(".",
            background=cls.BG_DARK,
            foreground=cls.FG_GREEN,
            fieldbackground=cls.TEXT_BG,
            troughcolor=cls.BG_MEDIUM,
            selectbackground=cls.ACCENT,
            selectforeground=cls.TEXT_BG
        )
        
        # Frame styles
        style.configure("TFrame", background=cls.BG_DARK)
        style.configure("TLabelframe", background=cls.BG_DARK, foreground=cls.FG_GREEN)
        style.configure("TLabelframe.Label", background=cls.BG_DARK, foreground=cls.FG_GREEN)
        
        # Button styles
        style.configure("TButton",
            background=cls.BG_LIGHT,
            foreground=cls.FG_GREEN,
            padding=5
        )
        style.map("TButton",
            background=[("active", cls.ACCENT)],
            foreground=[("active", cls.TEXT_BG)]
        )
        
        # Entry styles
        style.configure("TEntry",
            fieldbackground=cls.TEXT_BG,
            foreground=cls.FG_GREEN,
            padding=5
        )
        
        # Label styles
        style.configure("TLabel",
            background=cls.BG_DARK,
            foreground=cls.FG_GREEN
        )
        
        # Combobox styles
        style.configure("TCombobox",
            fieldbackground=cls.TEXT_BG,
            background=cls.BG_LIGHT,
            foreground=cls.FG_GREEN,
            arrowcolor=cls.FG_GREEN,
            padding=5
        )
        style.map("TCombobox",
            fieldbackground=[("readonly", cls.TEXT_BG)],
            selectbackground=[("readonly", cls.ACCENT)]
        )
        
        # Scrollbar styles
        style.configure("TScrollbar",
            background=cls.BG_LIGHT,
            troughcolor=cls.BG_MEDIUM,
            arrowcolor=cls.FG_GREEN
        )
        
        # Notebook styles
        style.configure("TNotebook",
            background=cls.BG_DARK,
            foreground=cls.FG_GREEN,
            padding=2
        )
        style.configure("TNotebook.Tab",
            background=cls.BG_MEDIUM,
            foreground=cls.FG_GREEN,
            padding=[10, 2]
        )
        style.map("TNotebook.Tab",
            background=[("selected", cls.BG_LIGHT)],
            foreground=[("selected", cls.FG_BRIGHT_GREEN)]
        )

class HabitableZoneExplorer:
    def __init__(self, root):
        self.root = root
        self.root.title("AIHabitablezone Explorer")
        self.root.geometry("800x600")
        self.logger = logging.getLogger("AIHabitablezone")
        
        # Set up dark theme
        self.root.configure(bg=DarkTheme.BG_DARK)
        DarkTheme.setup_theme()
        
        # Initialize visualizer
        self.visualizer = HabitableZoneVisualizer()
        
        # Create main container
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
        
        self._create_controls()
        self._create_display()
        self._create_status_bar()
        
    def _create_controls(self):
        """Create control panel"""
        control_frame = ttk.LabelFrame(self.main_frame, text="Controls", padding="5")
        control_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Star parameters
        ttk.Label(control_frame, text="Star Type:").grid(row=0, column=0, padx=5, pady=5)
        self.star_type = ttk.Combobox(control_frame, values=["G2V (Sun-like)", "M5V (Red Dwarf)", "F0V (Hot)", "K2V (Orange)"])
        self.star_type.grid(row=0, column=1, padx=5, pady=5)
        self.star_type.set("G2V (Sun-like)")
        self.star_type.bind('<<ComboboxSelected>>', self._update_display)
        
        ttk.Label(control_frame, text="Star Temperature (K):").grid(row=0, column=2, padx=5, pady=5)
        self.temp_var = tk.StringVar(value="5778")
        self.temp_entry = ttk.Entry(control_frame, textvariable=self.temp_var)
        self.temp_entry.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(control_frame, text="Star Luminosity (L☉):").grid(row=0, column=4, padx=5, pady=5)
        self.lum_var = tk.StringVar(value="1.0")
        self.lum_entry = ttk.Entry(control_frame, textvariable=self.lum_var)
        self.lum_entry.grid(row=0, column=5, padx=5, pady=5)
        
        # Calculate button
        self.calc_button = ttk.Button(control_frame, text="Calculate Habitable Zone", command=self._calculate)
        self.calc_button.grid(row=0, column=6, padx=5, pady=5)
        
    def _create_display(self):
        """Create main display area with tabs for different views"""
        display_frame = ttk.LabelFrame(self.main_frame, text="Habitable Zone", padding="5")
        display_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(display_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Text results tab
        self.text_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.text_frame, text="Results")
        
        # Results text area with dark theme
        self.results_text = tk.Text(
            self.text_frame, 
            height=10, 
            width=60,
            bg=DarkTheme.TEXT_BG,
            fg=DarkTheme.FG_GREEN,
            insertbackground=DarkTheme.FG_GREEN,
            selectbackground=DarkTheme.ACCENT,
            selectforeground=DarkTheme.TEXT_BG,
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar for results
        scrollbar = ttk.Scrollbar(self.text_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.results_text['yscrollcommand'] = scrollbar.set
        
        # 2D Map tab
        self.map_2d_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.map_2d_frame, text="2D Map")
        
        # 3D Map tab
        self.map_3d_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.map_3d_frame, text="3D Map")
        
        # Configure grid
        display_frame.columnconfigure(0, weight=1)
        display_frame.rowconfigure(0, weight=1)
        self.text_frame.columnconfigure(0, weight=1)
        self.text_frame.rowconfigure(0, weight=1)
        self.map_2d_frame.columnconfigure(0, weight=1)
        self.map_2d_frame.rowconfigure(0, weight=1)
        self.map_3d_frame.columnconfigure(0, weight=1)
        self.map_3d_frame.rowconfigure(0, weight=1)
            
    def _create_status_bar(self):
        """Create status bar"""
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(
            self.main_frame, 
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            padding=(5, 2)
        )
        self.status_bar.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E))
        self.status_var.set("Ready")
        
    def _update_display(self, event=None):
        """Update display when star type changes"""
        star_types = {
            "G2V (Sun-like)": (5778, 1.0),
            "M5V (Red Dwarf)": (3042, 0.0017),
            "F0V (Hot)": (7220, 6.3),
            "K2V (Orange)": (4400, 0.29)
        }
        
        selected = self.star_type.get()
        if selected in star_types:
            temp, lum = star_types[selected]
            self.temp_var.set(str(temp))
            self.lum_var.set(str(lum))
            
    def _calculate(self):
        """Calculate habitable zone and update all displays"""
        try:
            temp = float(self.temp_var.get())
            luminosity = float(self.lum_var.get())
            
            # Calculate habitable zone boundaries
            inner_edge = (luminosity/1.1) ** 0.5
            outer_edge = (luminosity/0.53) ** 0.5
            
            # Update text results
            result = f"""Habitable Zone Calculation Results:
            
Star Parameters:
- Type: {self.star_type.get()}
- Temperature: {temp:.0f} K
- Luminosity: {luminosity:.4f} L☉

Habitable Zone Boundaries:
- Inner Edge: {inner_edge:.2f} AU
- Outer Edge: {outer_edge:.2f} AU

Notes:
- The habitable zone is the region around a star where liquid water could exist on a planet's surface
- These are conservative estimates based on simple models
- Actual habitability depends on many other factors including:
  * Planetary atmosphere
  * Surface pressure
  * Planetary mass
  * Orbital eccentricity
"""
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, result)
            
            # Clear previous plots
            for widget in self.map_2d_frame.winfo_children():
                widget.destroy()
            for widget in self.map_3d_frame.winfo_children():
                widget.destroy()
            
            # Create and embed new plots
            fig_2d = self.visualizer.create_2d_map(temp, luminosity, inner_edge, outer_edge)
            fig_3d = self.visualizer.create_3d_map(temp, luminosity, inner_edge, outer_edge)
            
            map_2d_widget = embed_figure(fig_2d, self.map_2d_frame)
            map_3d_widget = embed_figure(fig_3d, self.map_3d_frame)
            
            map_2d_widget.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            map_3d_widget.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            
            self.status_var.set("Calculation complete")
            self.logger.info("Habitable zone calculation completed successfully")
            
        except ValueError as e:
            messagebox.showerror("Error", "Please enter valid numbers for temperature and luminosity")
            self.logger.error(f"Calculation error: {str(e)}")
            self.status_var.set("Error in calculation")
            
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
            self.logger.error(f"Unexpected error in calculation: {str(e)}")
            self.status_var.set("Error in calculation")

def launch_gui() -> None:
    """Launch the main application GUI."""
    try:
        root = tk.Tk()
        app = HabitableZoneExplorer(root)
        root.mainloop()
    except Exception as e:
        logging.getLogger("AIHabitablezone").error(f"Error launching GUI: {e}")
        raise