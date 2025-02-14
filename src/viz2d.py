"""
2D visualization module for AIHabitablezone.
Handles creation of 2D plots including galaxy maps, habitable zones, and system views.
"""
from typing import List, Tuple, Optional, Dict
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns
from pathlib import Path

from .models import Star, Planet, Galaxy
from .physics import HabitableZoneCalculator, PhysicsConstants
from .error import VisualizationError
from .logger import LOGGER
from .config import CONFIG

class Visualization2D:
    """Base class for 2D visualizations."""
    
    def __init__(self):
        """Initialize visualization settings."""
        self.style = {
            'figure.figsize': (12, 8),
            'font.size': 12,
            'axes.labelsize': 14,
            'axes.titlesize': 16,
            'xtick.labelsize': 12,
            'ytick.labelsize': 12
        }
        plt.style.use('seaborn')
        for key, value in self.style.items():
            plt.rcParams[key] = value
    
    def save_plot(self, fig: Figure, filename: str) -> None:
        """
        Save plot to file.
        
        Args:
            fig: matplotlib Figure object
            filename: Name of the file to save
        """
        try:
            output_dir = Path(CONFIG.data_dir) / 'plots'
            output_dir.mkdir(exist_ok=True)
            fig.savefig(output_dir / filename, dpi=300, bbox_inches='tight')
            LOGGER.info(f"Saved plot to {filename}")
        except Exception as e:
            raise VisualizationError(f"Failed to save plot: {str(e)}")

class GalaxyMapVisualizer(Visualization2D):
    """Creates 2D visualizations of galaxy data."""
    
    def __init__(self):
        """Initialize galaxy map visualizer."""
        super().__init__()
        self.colormap = LinearSegmentedColormap.from_list('star_colors', 
            ['#ff4000', '#ffff00', '#ffffff', '#add8e6', '#0000ff'])
    
    def plot_galaxy_map(self, galaxy: Galaxy, 
                       highlight_habitable: bool = True,
                       show_labels: bool = True) -> Figure:
        """
        Create a 2D map of the galaxy showing star positions.
        
        Args:
            galaxy: Galaxy object containing stars
            highlight_habitable: Whether to highlight potentially habitable systems
            show_labels: Whether to show star labels
            
        Returns:
            matplotlib Figure object
        """
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))
            
            # Top-down view (X-Y plane)
            self._plot_galaxy_projection(ax1, galaxy, 'x', 'y', 
                                      highlight_habitable, show_labels)
            ax1.set_title('Galaxy Map (Top View)')
            
            # Side view (X-Z plane)
            self._plot_galaxy_projection(ax2, galaxy, 'x', 'z',
                                      highlight_habitable, show_labels)
            ax2.set_title('Galaxy Map (Side View)')
            
            fig.suptitle(f'{galaxy.name} Star Map', fontsize=20)
            plt.tight_layout()
            
            return fig
            
        except Exception as e:
            raise VisualizationError(f"Failed to create galaxy map: {str(e)}")
    
    def _plot_galaxy_projection(self, ax: Axes, galaxy: Galaxy,
                              x_coord: str, y_coord: str,
                              highlight_habitable: bool,
                              show_labels: bool) -> None:
        """Plot a 2D projection of the galaxy."""
        # Get coordinate getters
        coord_map = {'x': lambda s: s.x, 'y': lambda s: s.y, 'z': lambda s: s.z}
        get_x = coord_map[x_coord]
        get_y = coord_map[y_coord]
        
        # Plot all stars
        for star in galaxy.stars:
            color = self._get_star_color(star)
            size = 50 * np.sqrt(star.luminosity)  # Size based on luminosity
            
            ax.scatter(get_x(star), get_y(star), 
                      c=color, s=size, alpha=0.6)
            
            if show_labels and star.luminosity > 0.5:  # Label only bright stars
                ax.annotate(star.name, 
                          (get_x(star), get_y(star)),
                          xytext=(5, 5), textcoords='offset points',
                          fontsize=8, alpha=0.7)
        
        # Highlight habitable systems if requested
        if highlight_habitable:
            habitable_stars = galaxy.get_habitable_stars()
            for star in habitable_stars:
                ax.scatter(get_x(star), get_y(star), 
                          facecolors='none', edgecolors='g',
                          s=100, linewidth=2, alpha=0.5)
        
        # Set labels and grid
        ax.set_xlabel(f'{x_coord.upper()} (parsecs)')
        ax.set_ylabel(f'{y_coord.upper()} (parsecs)')
        ax.grid(True, alpha=0.3)
    
    def _get_star_color(self, star: Star) -> str:
        """Determine star color based on temperature."""
        # Simplified color mapping based on temperature
        if star.temperature >= 30000:
            return '#add8e6'  # Blue
        elif star.temperature >= 10000:
            return '#ffffff'  # White
        elif star.temperature >= 7500:
            return '#ffff00'  # Yellow
        elif star.temperature >= 5000:
            return '#ff4000'  # Orange
        else:
            return '#ff0000'  # Red

class HabitableZoneVisualizer(Visualization2D):
    """Creates 2D visualizations of habitable zones."""
    
    def __init__(self):
        """Initialize habitable zone visualizer."""
        super().__init__()
        self.hz_calculator = HabitableZoneCalculator()
    
    def plot_habitable_zone(self, star: Star, 
                           show_planets: bool = True) -> Figure:
        """
        Create a 2D visualization of a star's habitable zone.
        
        Args:
            star: Star object
            show_planets: Whether to show the star's planets
            
        Returns:
            matplotlib Figure object
        """
        try:
            fig, ax = plt.subplots(figsize=(12, 12))
            
            # Calculate habitable zone boundaries
            hz_bounds = self.hz_calculator.calculate_habitable_zone(star)
            
            # Plot star
            ax.scatter(0, 0, c='yellow', s=300, zorder=10, label='Star')
            
            # Plot habitable zones
            theta = np.linspace(0, 2*np.pi, 100)
            
            # Conservative habitable zone
            inner = hz_bounds['runaway_greenhouse']
            outer = hz_bounds['maximum_greenhouse']
            
            # Fill conservative habitable zone
            x = np.outer(np.cos(theta), np.linspace(inner, outer, 50))
            y = np.outer(np.sin(theta), np.linspace(inner, outer, 50))
            ax.fill(x.flatten(), y.flatten(), 
                   color='green', alpha=0.2, label='Conservative HZ')
            
            # Plot optimistic boundaries
            if 'recent_venus' in hz_bounds and 'early_mars' in hz_bounds:
                opt_inner = hz_bounds['recent_venus']
                opt_outer = hz_bounds['early_mars']
                
                # Plot optimistic zone boundaries
                for r in [opt_inner, opt_outer]:
                    x = r * np.cos(theta)
                    y = r * np.sin(theta)
                    ax.plot(x, y, '--', color='lightgreen', alpha=0.5)
            
            # Plot planets if requested
            if show_planets and star.planets:
                self._add_planets_to_plot(ax, star.planets)
            
            # Customize plot
            ax.set_aspect('equal')
            ax.grid(True, alpha=0.3)
            ax.set_xlabel('Distance (AU)')
            ax.set_ylabel('Distance (AU)')
            ax.set_title(f'Habitable Zone for {star.name}')
            
            # Add legend
            ax.legend(loc='upper right')
            
            return fig
            
        except Exception as e:
            raise VisualizationError(f"Failed to create habitable zone plot: {str(e)}")
    
    def _add_planets_to_plot(self, ax: Axes, planets: List[Planet]) -> None:
        """Add planets to the habitable zone plot."""
        for planet in planets:
            # Calculate planet position (simplified to circular orbit)
            angle = np.random.random() * 2 * np.pi  # Random position in orbit
            x = planet.orbital_distance * np.cos(angle)
            y = planet.orbital_distance * np.sin(angle)
            
            # Plot orbit
            orbit = patches.Circle((0, 0), planet.orbital_distance,
                                 fill=False, linestyle='--',
                                 color='gray', alpha=0.3)
            ax.add_patch(orbit)
            
            # Plot planet
            size = 100 * np.sqrt(planet.radius)  # Size based on radius
            ax.scatter(x, y, s=size, zorder=5,
                      label=planet.name)
            
            # Add label
            ax.annotate(planet.name, (x, y),
                       xytext=(5, 5), textcoords='offset points')

class SystemVisualizer(Visualization2D):
    """Creates 2D visualizations of planetary systems."""
    
    def plot_system_comparison(self, planets: List[Planet],
                             reference_system: Optional[List[Planet]] = None) -> Figure:
        """
        Create a comparative visualization of planetary systems.
        
        Args:
            planets: List of planets to visualize
            reference_system: Optional reference system (e.g., Solar System)
            
        Returns:
            matplotlib Figure object
        """
        try:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))
            
            # Plot planet sizes
            self._plot_size_comparison(ax1, planets, reference_system)
            
            # Plot orbital distances
            self._plot_orbit_comparison(ax2, planets, reference_system)
            
            fig.suptitle('Planetary System Comparison', fontsize=16)
            plt.tight_layout()
            
            return fig
            
        except Exception as e:
            raise VisualizationError(
                f"Failed to create system comparison plot: {str(e)}")
    
    def _plot_size_comparison(self, ax: Axes, planets: List[Planet],
                            reference_system: Optional[List[Planet]]) -> None:
        """Plot planet size comparison."""
        positions = np.arange(len(planets))
        radii = [p.radius for p in planets]
        
        # Create bar plot
        ax.bar(positions, radii, alpha=0.6)
        
        # Add reference system if provided
        if reference_system:
            ref_positions = positions + 0.35
            ref_radii = [p.radius for p in reference_system]
            ax.bar(ref_positions, ref_radii, alpha=0.4, color='gray')
        
        # Customize plot
        ax.set_xticks(positions)
        ax.set_xticklabels([p.name for p in planets], rotation=45)
        ax.set_ylabel('Radius (Earth Radii)')
        ax.set_title('Planet Size Comparison')
        ax.grid(True, alpha=0.3)
    
    def _plot_orbit_comparison(self, ax: Axes, planets: List[Planet],
                             reference_system: Optional[List[Planet]]) -> None:
        """Plot orbital distance comparison."""
        positions = np.arange(len(planets))
        distances = [p.orbital_distance for p in planets]
        
        # Create scatter plot
        ax.scatter(distances, np.zeros_like(distances) + 0.1,
                  s=100, alpha=0.6)
        
        # Add reference system if provided
        if reference_system:
            ref_distances = [p.orbital_distance for p in reference_system]
            ax.scatter(ref_distances, np.zeros_like(ref_distances) - 0.1,
                      s=100, alpha=0.4, color='gray')
        
        # Customize plot
        ax.set_xlabel('Orbital Distance (AU)')
        ax.set_yticks([])
        ax.set_title('Orbital Distance Comparison')
        ax.grid(True, alpha=0.3)
        
        # Add planet labels
        for i, planet in enumerate(planets):
            ax.annotate(planet.name,
                       (planet.orbital_distance, 0.1),
                       xytext=(0, 5), textcoords='offset points',
                       ha='center')

# Create global visualizer instances
galaxy_visualizer = GalaxyMapVisualizer()
hz_visualizer = HabitableZoneVisualizer()
system_visualizer = SystemVisualizer()