"""
Core data models for astronomical objects in the AIHabitablezone package.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import numpy as np
from .error import DataValidationError

@dataclass
class CelestialObject:
    """Base class for all celestial objects."""
    name: str
    mass: float
    radius: float
    age: float  # billions of years
    
    def __post_init__(self):
        """Validate basic parameters."""
        if self.mass <= 0:
            raise DataValidationError(f"Mass must be positive, got {self.mass}")
        if self.radius <= 0:
            raise DataValidationError(f"Radius must be positive, got {self.radius}")
        if self.age < 0:
            raise DataValidationError(f"Age cannot be negative, got {self.age}")

@dataclass
class Star(CelestialObject):
    """
    Represents a star with enhanced physical properties.
    All units are in solar units unless specified otherwise.
    """
    luminosity: float
    temperature: float  # Kelvin
    metallicity: float = 0.0  # [Fe/H] relative to solar
    activity: float = 0.0  # 0-1 scale
    rotation_velocity: float = 0.0  # km/s
    spectral_type: Optional[str] = None
    planets: List['Planet'] = field(default_factory=list)
    x: float = 0.0  # galactic coordinates in parsecs
    y: float = 0.0
    z: float = 0.0
    
    def __post_init__(self):
        """Validate star-specific parameters."""
        super().__post_init__()
        if self.luminosity <= 0:
            raise DataValidationError(f"Luminosity must be positive, got {self.luminosity}")
        if self.temperature <= 0:
            raise DataValidationError(f"Temperature must be positive, got {self.temperature}")
        if not 0 <= self.activity <= 1:
            raise DataValidationError(f"Activity must be between 0 and 1, got {self.activity}")
    
    def add_planet(self, planet: 'Planet') -> None:
        """Add a planet to the star's system."""
        self.planets.append(planet)
        planet.star = self
    
    def get_position(self) -> Tuple[float, float, float]:
        """Get galactic coordinates."""
        return (self.x, self.y, self.z)
    
    def estimate_habitable_zone(self) -> Tuple[float, float]:
        """
        Estimate basic habitable zone boundaries.
        Returns (inner_bound, outer_bound) in AU.
        """
        # Simple estimation - will be replaced by proper physics calculations
        inner = np.sqrt(self.luminosity / 1.1)
        outer = np.sqrt(self.luminosity / 0.53)
        return (inner, outer)

@dataclass
class Planet(CelestialObject):
    """
    Represents a planet with enhanced physical properties.
    Mass in Earth masses, radius in Earth radii unless specified otherwise.
    """
    orbital_distance: float  # AU
    atmosphere: Dict[str, float]  # composition ratios
    gravity: float  # m/s²
    eccentricity: float  # 0-1
    inclination: float = 0.0  # degrees
    albedo: float = 0.3  # Bond albedo
    rotation_period: float = 24.0  # hours
    orbital_period: float = 365.25  # days
    mean_density: float = 5.51  # g/cm³ (Earth = 5.51)
    surface_temperature: Optional[float] = None  # Kelvin
    magnetic_field: Optional[float] = None  # relative to Earth
    star: Optional[Star] = None
    
    def __post_init__(self):
        """Validate planet-specific parameters."""
        super().__post_init__()
        if self.orbital_distance <= 0:
            raise DataValidationError(f"Orbital distance must be positive, got {self.orbital_distance}")
        if not 0 <= self.eccentricity < 1:
            raise DataValidationError(f"Eccentricity must be between 0 and 1, got {self.eccentricity}")
        if not isinstance(self.atmosphere, dict):
            raise DataValidationError("Atmosphere must be a dictionary of compositions")
    
    def calculate_orbital_position(self, time: float) -> Tuple[float, float, float]:
        """
        Calculate position at a given time.
        Returns (x, y, z) coordinates in AU.
        """
        # Convert inclination to radians
        inc_rad = np.radians(self.inclination)
        
        # Mean angular motion
        n = 2 * np.pi / self.orbital_period
        
        # Mean anomaly
        M = n * time
        
        # Solve Kepler's equation (simplified)
        E = M + self.eccentricity * np.sin(M)  # This is an approximation
        
        # True anomaly
        nu = 2 * np.arctan(np.sqrt((1 + self.eccentricity)/(1 - self.eccentricity)) * np.tan(E/2))
        
        # Distance from star
        r = self.orbital_distance * (1 - self.eccentricity**2)/(1 + self.eccentricity * np.cos(nu))
        
        # Position in orbital plane
        x = r * np.cos(nu)
        y = r * np.sin(nu) * np.cos(inc_rad)
        z = r * np.sin(nu) * np.sin(inc_rad)
        
        return (x, y, z)
    
    def estimate_surface_gravity(self) -> float:
        """Calculate surface gravity in m/s²."""
        G = 6.67430e-11  # gravitational constant
        M = self.mass * 5.972e24  # convert to kg (Earth mass)
        R = self.radius * 6.371e6  # convert to m (Earth radius)
        return G * M / (R * R)

@dataclass
class Galaxy:
    """
    Represents a galaxy containing stars and their planetary systems.
    """
    name: str
    type: str  # Spiral, Elliptical, etc.
    distance: float  # parsecs from Earth
    size: float  # light years
    mass: float  # solar masses
    age: float  # billion years
    stars: List[Star] = field(default_factory=list)
    position: Tuple[float, float, float] = field(default_factory=lambda: (0, 0, 0))
    
    def __post_init__(self):
        """Validate galaxy parameters."""
        if self.distance < 0:
            raise DataValidationError(f"Distance cannot be negative, got {self.distance}")
        if self.size <= 0:
            raise DataValidationError(f"Size must be positive, got {self.size}")
        if self.mass <= 0:
            raise DataValidationError(f"Mass must be positive, got {self.mass}")
        if self.age <= 0:
            raise DataValidationError(f"Age must be positive, got {self.age}")
    
    def add_star(self, star: Star) -> None:
        """Add a star to the galaxy."""
        self.stars.append(star)
    
    def get_habitable_stars(self) -> List[Star]:
        """Return stars that could potentially host habitable planets."""
        return [
            star for star in self.stars
            if 0.8 <= star.mass <= 1.2  # Main sequence stars similar to Sun
            and star.age >= 1.0  # Billion years, allowing time for life
            and -0.5 <= star.metallicity <= 0.5  # Reasonable metallicity range
        ]
    
    def get_stars_in_region(self, center: Tuple[float, float, float], radius: float) -> List[Star]:
        """
        Get all stars within a spherical region.
        
        Args:
            center: (x, y, z) coordinates in parsecs
            radius: Search radius in parsecs
            
        Returns:
            List of stars within the specified region
        """
        return [
            star for star in self.stars
            if np.sqrt(sum((c - p)**2 for c, p in zip(center, (star.x, star.y, star.z)))) <= radius
        ]