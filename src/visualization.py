#!/usr/bin/env python3
"""
Visualization module for the AIHabitablezone application.
Provides 2D and 3D plotting capabilities for habitable zones.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.colors as mcolors
from mpl_toolkits.mplot3d import Axes3D

class HabitableZoneVisualizer:
    """Class for creating habitable zone visualizations"""
    
    def __init__(self):
        # Set up color scheme
        self.colors = {
            'background': '#1e1e1e',
            'text': '#4CAF50',
            'star': '#FDB813',
            'habitable': '#4CAF50',
            'too_hot': '#FF5252',
            'too_cold': '#2196F3',
            'grid': '#404040'
        }
        
        # Configure matplotlib style
        plt.style.use('dark_background')
        plt.rcParams.update({
            'text.color': self.colors['text'],
            'axes.labelcolor': self.colors['text'],
            'axes.edgecolor': self.colors['text'],
            'xtick.color': self.colors['text'],
            'ytick.color': self.colors['text'],
            'grid.color': self.colors['grid'],
            'figure.facecolor': self.colors['background'],
            'axes.facecolor': self.colors['background']
        })

    def create_2d_map(self, star_temp, luminosity, inner_edge, outer_edge):
        """Create a 2D visualization of the habitable zone"""
        fig = Figure(figsize=(8, 8), facecolor=self.colors['background'])
        ax = fig.add_subplot(111)
        
        # Create circles for different zones
        theta = np.linspace(0, 2*np.pi, 100)
        
        # Too hot zone
        r_hot = inner_edge
        ax.fill(r_hot * np.cos(theta), r_hot * np.sin(theta), 
                color=self.colors['too_hot'], alpha=0.3, label='Too Hot')
        
        # Habitable zone
        r_hab = np.linspace(inner_edge, outer_edge, 100)
        theta_mesh, r_mesh = np.meshgrid(theta, r_hab)
        ax.fill(outer_edge * np.cos(theta), outer_edge * np.sin(theta),
               color=self.colors['habitable'], alpha=0.3, label='Habitable Zone')
        ax.fill(inner_edge * np.cos(theta), inner_edge * np.sin(theta),
               color=self.colors['background'])
        
        # Too cold zone (show boundary)
        ax.plot(outer_edge * np.cos(theta), outer_edge * np.sin(theta),
                color=self.colors['too_cold'], linestyle='--', label='Too Cold')
        
        # Plot star
        ax.scatter([0], [0], color=self.colors['star'], s=100, label='Star')
        
        # Add AU scale
        ax.set_xlabel('Distance (AU)')
        ax.set_ylabel('Distance (AU)')
        
        # Make plot square and equal scale
        ax.set_aspect('equal')
        
        # Add grid
        ax.grid(True, linestyle='--', alpha=0.3)
        
        # Add legend
        ax.legend(loc='upper right')
        
        # Add title with star information
        title = f'Habitable Zone Map\nStar Temperature: {star_temp}K, Luminosity: {luminosity}L☉'
        ax.set_title(title)
        
        return fig

    def create_3d_map(self, star_temp, luminosity, inner_edge, outer_edge):
        """Create a 3D visualization of the habitable zone"""
        fig = Figure(figsize=(8, 8), facecolor=self.colors['background'])
        ax = fig.add_subplot(111, projection='3d')
        
        # Create sphere points
        phi = np.linspace(0, np.pi, 20)
        theta = np.linspace(0, 2*np.pi, 40)
        phi, theta = np.meshgrid(phi, theta)

        # Inner edge sphere
        x_inner = inner_edge * np.sin(phi) * np.cos(theta)
        y_inner = inner_edge * np.sin(phi) * np.sin(theta)
        z_inner = inner_edge * np.cos(phi)
        
        # Outer edge sphere
        x_outer = outer_edge * np.sin(phi) * np.cos(theta)
        y_outer = outer_edge * np.sin(phi) * np.sin(theta)
        z_outer = outer_edge * np.cos(phi)
        
        # Plot spheres
        ax.plot_surface(x_inner, y_inner, z_inner, color=self.colors['too_hot'],
                       alpha=0.3, label='Inner Edge')
        ax.plot_surface(x_outer, y_outer, z_outer, color=self.colors['too_cold'],
                       alpha=0.3, label='Outer Edge')
        
        # Plot star
        ax.scatter([0], [0], [0], color=self.colors['star'], s=100, label='Star')
        
        # Set labels
        ax.set_xlabel('X (AU)')
        ax.set_ylabel('Y (AU)')
        ax.set_zlabel('Z (AU)')
        
        # Make axes equal
        ax.set_box_aspect([1,1,1])
        
        # Add title
        title = f'3D Habitable Zone\nStar Temperature: {star_temp}K, Luminosity: {luminosity}L☉'
        ax.set_title(title)
        
        return fig

def embed_figure(fig, parent):
    """Embed a matplotlib figure in a tkinter widget"""
    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    return canvas.get_tk_widget()