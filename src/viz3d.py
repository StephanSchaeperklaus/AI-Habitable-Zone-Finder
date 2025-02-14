"""
3D visualization module for AIHabitablezone.
Handles creation of 3D visualizations including planet models and orbital systems.
"""
from typing import List, Tuple, Optional, Dict
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from pathlib import Path

from .models import Star, Planet, Galaxy
from .physics import HabitableZoneCalculator, PhysicsConstants
from .error import VisualizationError
from .logger import LOGGER
from .config import CONFIG

class Visualization3D:
    """Base class for 3D visualizations."""
    
    def __init__(self):
        """Initialize visualization settings."""
        self.style = {
            'figure.figsize': (12, 12),
            'font.size': 12,
            'axes.labelsize': 14,
            'axes.titlesize': 16
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
            output_dir = Path(CONFIG.data_dir) / 'plots3d'
            output_dir.mkdir(exist_ok=True)
            fig.savefig(output_dir / filename, dpi=300, bbox_inches='tight')
            LOGGER.info(f"Saved 3D plot to {filename}")
        except Exception as e:
            raise VisualizationError(f"Failed to save 3D plot: {str(e)}")

class PlanetVisualizer3D:
    """Creates 3D visualizations of planets."""
    
    def create_planet_model(self, planet: Planet) -> go.Figure:
        """
        Create an interactive 3D model of a planet.
        
        Args:
            planet: Planet object to visualize
            
        Returns:
            plotly Figure object
        """
        try:
            # Create sphere mesh
            phi = np.linspace(0, 2*np.pi, 100)
            theta = np.linspace(-np.pi/2, np.pi/2, 100)
            phi, theta = np.meshgrid(phi, theta)
            
            # Calculate surface coordinates
            radius = planet.radius * PhysicsConstants.EARTH_RADIUS
            x = radius * np.cos(theta) * np.cos(phi)
            y = radius * np.cos(theta) * np.sin(phi)
            z = radius * np.sin(theta)
            
            # Create base planet surface
            surface_color = self._get_planet_color(planet)
            
            fig = go.Figure(data=[
                go.Surface(
                    x=x, y=y, z=z,
                    colorscale=[[0, surface_color], [1, surface_color]],
                    showscale=False
                )
            ])
            
            # Add atmosphere if present
            if planet.atmosphere:
                atmo_radius = radius * 1.05  # 5% larger than planet
                x_atmo = atmo_radius * np.cos(theta) * np.cos(phi)
                y_atmo = atmo_radius * np.cos(theta) * np.sin(phi)
                z_atmo = atmo_radius * np.sin(theta)
                
                fig.add_trace(
                    go.Surface(
                        x=x_atmo, y=y_atmo, z=z_atmo,
                        colorscale=[[0, 'rgba(100,100,255,0.1)'], 
                                  [1, 'rgba(100,100,255,0.1)']],
                        showscale=False,
                        opacity=0.3
                    )
                )
            
            # Update layout
            fig.update_layout(
                title=f'3D Model of {planet.name}',
                scene=dict(
                    xaxis_title='X (m)',
                    yaxis_title='Y (m)',
                    zaxis_title='Z (m)',
                    aspectmode='data'
                ),
                showlegend=False
            )
            
            return fig
            
        except Exception as e:
            raise VisualizationError(f"Failed to create planet model: {str(e)}")
    
    def _get_planet_color(self, planet: Planet) -> str:
        """Determine planet color based on its properties."""
        # Basic color scheme based on planet type (could be enhanced)
        if planet.mass < 0.1:  # Small rocky planet
            return 'rgb(169,169,169)'  # Gray
        elif planet.mass < 2:  # Earth-like
            return 'rgb(100,149,237)'  # Blue-ish
        elif planet.mass < 10:  # Super-Earth
            return 'rgb(85,107,47)'    # Dark green
        else:  # Gas giant
            return 'rgb(218,165,32)'   # Golden

class OrbitVisualizer3D:
    """Creates 3D visualizations of orbital systems."""
    
    def __init__(self):
        """Initialize orbit visualizer."""
        self.hz_calculator = HabitableZoneCalculator()
    
    def create_orbital_visualization(self, star: Star,
                                  show_habitable_zone: bool = True) -> go.Figure:
        """
        Create an interactive 3D visualization of a star system.
        
        Args:
            star: Star object
            show_habitable_zone: Whether to show the habitable zone
            
        Returns:
            plotly Figure object
        """
        try:
            fig = go.Figure()
            
            # Add star
            fig.add_trace(
                go.Scatter3d(
                    x=[0], y=[0], z=[0],
                    mode='markers',
                    marker=dict(
                        size=20,
                        color='yellow',
                        symbol='circle'
                    ),
                    name=star.name
                )
            )
            
            # Add habitable zone if requested
            if show_habitable_zone:
                self._add_habitable_zone(fig, star)
            
            # Add planets and their orbits
            for planet in star.planets:
                self._add_planet_orbit(fig, planet)
            
            # Update layout
            fig.update_layout(
                title=f'3D Orbital Visualization - {star.name} System',
                scene=dict(
                    xaxis_title='X (AU)',
                    yaxis_title='Y (AU)',
                    zaxis_title='Z (AU)',
                    aspectmode='data'
                ),
                showlegend=True
            )
            
            return fig
            
        except Exception as e:
            raise VisualizationError(
                f"Failed to create orbital visualization: {str(e)}")
    
    def _add_habitable_zone(self, fig: go.Figure, star: Star) -> None:
        """Add habitable zone visualization to the figure."""
        hz_bounds = self.hz_calculator.calculate_habitable_zone(star)
        
        # Get conservative HZ boundaries
        inner = hz_bounds['runaway_greenhouse']
        outer = hz_bounds['maximum_greenhouse']
        
        # Create points for HZ boundaries
        phi = np.linspace(0, 2*np.pi, 100)
        theta = np.linspace(-np.pi/2, np.pi/2, 50)
        phi, theta = np.meshgrid(phi, theta)
        
        # Inner boundary
        x_inner = inner * np.cos(theta) * np.cos(phi)
        y_inner = inner * np.cos(theta) * np.sin(phi)
        z_inner = inner * np.sin(theta)
        
        # Outer boundary
        x_outer = outer * np.cos(theta) * np.cos(phi)
        y_outer = outer * np.cos(theta) * np.sin(phi)
        z_outer = outer * np.sin(theta)
        
        # Add surfaces to figure
        fig.add_trace(
            go.Surface(
                x=x_inner, y=y_inner, z=z_inner,
                colorscale=[[0, 'rgba(0,255,0,0.1)'], 
                           [1, 'rgba(0,255,0,0.1)']],
                showscale=False,
                opacity=0.3,
                name='Inner HZ'
            )
        )
        
        fig.add_trace(
            go.Surface(
                x=x_outer, y=y_outer, z=z_outer,
                colorscale=[[0, 'rgba(0,255,0,0.1)'], 
                           [1, 'rgba(0,255,0,0.1)']],
                showscale=False,
                opacity=0.3,
                name='Outer HZ'
            )
        )
    
    def _add_planet_orbit(self, fig: go.Figure, planet: Planet) -> None:
        """Add planet and its orbit to the figure."""
        # Calculate orbital points
        t = np.linspace(0, 2*np.pi, 200)
        
        # Account for orbital inclination
        inc_rad = np.radians(planet.inclination)
        
        # Calculate orbit
        x = planet.orbital_distance * np.cos(t)
        y = planet.orbital_distance * np.sin(t) * np.cos(inc_rad)
        z = planet.orbital_distance * np.sin(t) * np.sin(inc_rad)
        
        # Add orbit line
        fig.add_trace(
            go.Scatter3d(
                x=x, y=y, z=z,
                mode='lines',
                line=dict(
                    color='gray',
                    width=2
                ),
                name=f'{planet.name} orbit'
            )
        )
        
        # Calculate current position (example at t=0)
        x_pos = planet.orbital_distance * np.cos(0)
        y_pos = planet.orbital_distance * np.sin(0) * np.cos(inc_rad)
        z_pos = planet.orbital_distance * np.sin(0) * np.sin(inc_rad)
        
        # Add planet
        size = 10 * np.sqrt(planet.radius)  # Scale size with radius
        fig.add_trace(
            go.Scatter3d(
                x=[x_pos], y=[y_pos], z=[z_pos],
                mode='markers',
                marker=dict(
                    size=size,
                    color='blue',
                    symbol='circle'
                ),
                name=planet.name
            )
        )

class SystemAnimation3D:
    """Creates animated 3D visualizations of planetary systems."""
    
    def create_system_animation(self, star: Star, 
                              duration: float = 10.0,
                              fps: int = 30) -> go.Figure:
        """
        Create an animated 3D visualization of a star system.
        
        Args:
            star: Star object
            duration: Animation duration in seconds
            fps: Frames per second
            
        Returns:
            plotly Figure object with animation
        """
        try:
            # Calculate number of frames
            n_frames = int(duration * fps)
            
            # Create figure
            fig = go.Figure()
            
            # Add star (static)
            fig.add_trace(
                go.Scatter3d(
                    x=[0], y=[0], z=[0],
                    mode='markers',
                    marker=dict(
                        size=20,
                        color='yellow',
                        symbol='circle'
                    ),
                    name=star.name
                )
            )
            
            # Create frames for animation
            frames = []
            for i in range(n_frames):
                frame_data = []
                # Add star (static)
                frame_data.append(
                    go.Scatter3d(
                        x=[0], y=[0], z=[0],
                        mode='markers',
                        marker=dict(
                            size=20,
                            color='yellow',
                            symbol='circle'
                        ),
                        name=star.name
                    )
                )
                
                # Calculate planet positions for this frame
                time = (i / n_frames) * 2 * np.pi  # 0 to 2π
                for planet in star.planets:
                    pos = planet.calculate_orbital_position(time)
                    frame_data.append(
                        go.Scatter3d(
                            x=[pos[0]], y=[pos[1]], z=[pos[2]],
                            mode='markers',
                            marker=dict(
                                size=10 * np.sqrt(planet.radius),
                                color='blue',
                                symbol='circle'
                            ),
                            name=planet.name
                        )
                    )
                
                frames.append(go.Frame(data=frame_data, name=str(i)))
            
            # Add frames to figure
            fig.frames = frames
            
            # Add animation buttons
            fig.update_layout(
                updatemenus=[{
                    'type': 'buttons',
                    'showactive': False,
                    'buttons': [
                        {'label': 'Play',
                         'method': 'animate',
                         'args': [None, {'frame': {'duration': 1000/fps, 'redraw': True},
                                       'fromcurrent': True,
                                       'mode': 'immediate'}]},
                        {'label': 'Pause',
                         'method': 'animate',
                         'args': [[None], {'frame': {'duration': 0, 'redraw': False},
                                         'mode': 'immediate',
                                         'transition': {'duration': 0}}]}
                    ]
                }]
            )
            
            # Update layout
            fig.update_layout(
                title=f'Animated {star.name} System',
                scene=dict(
                    xaxis_title='X (AU)',
                    yaxis_title='Y (AU)',
                    zaxis_title='Z (AU)',
                    aspectmode='data'
                ),
                showlegend=True
            )
            
            return fig
            
        except Exception as e:
            raise VisualizationError(
                f"Failed to create system animation: {str(e)}")

# Create global visualizer instances
planet_visualizer = PlanetVisualizer3D()
orbit_visualizer = OrbitVisualizer3D()
animation_visualizer = SystemAnimation3D()