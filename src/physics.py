"""
Physics calculations module for the AIHabitablezone package.
Implements advanced astronomical and physical calculations.
"""
from typing import Dict, Tuple, Optional
import numpy as np
from .models import Star, Planet
from .error import PhysicsError
from .logger import LOGGER

class PhysicsConstants:
    """Physical constants in SI units."""
    
    # Astronomical constants
    AU_TO_METERS = 1.496e11  # 1 AU in meters
    SOLAR_MASS = 1.989e30    # kg
    SOLAR_RADIUS = 6.957e8   # meters
    SOLAR_LUMINOSITY = 3.828e26  # watts
    EARTH_MASS = 5.972e24    # kg
    EARTH_RADIUS = 6.371e6   # meters
    
    # Physical constants
    G = 6.67430e-11         # gravitational constant (m³/kg/s²)
    STEFAN_BOLTZMANN = 5.670374419e-8  # W/(m²·K⁴)
    PLANCK = 6.62607015e-34  # J·s
    SPEED_OF_LIGHT = 299792458  # m/s
    
    # Conversion factors
    KELVIN_TO_CELSIUS = 273.15
    PARSEC_TO_METERS = 3.0857e16

class HabitableZoneCalculator:
    """
    Advanced habitable zone calculations based on various models.
    Implements multiple methods for calculating habitable zones.
    """
    
    def __init__(self):
        """Initialize calculator with Kopparapu et al. (2013) coefficients."""
        # Coefficients from Kopparapu et al. (2013)
        self.coefficients = {
            'recent_venus': {
                'a': 1.776e-4, 'b': 2.136e-4, 'c': 2.533e-8,
                'd': -1.332e-11, 'e': -3.097e-15, 's_eff': 1.776
            },
            'runaway_greenhouse': {
                'a': 1.107e-4, 'b': 1.332e-4, 'c': 1.580e-8,
                'd': -8.308e-12, 'e': -1.931e-15, 's_eff': 1.107
            },
            'moist_greenhouse': {
                'a': 1.380e-4, 'b': 1.685e-4, 'c': 3.731e-9,
                'd': -2.787e-12, 'e': -1.673e-15, 's_eff': 1.380
            },
            'maximum_greenhouse': {
                'a': 6.171e-5, 'b': 1.698e-5, 'c': 3.198e-9,
                'd': -5.575e-12, 'e': -3.008e-15, 's_eff': 0.356
            },
            'early_mars': {
                'a': 5.547e-5, 'b': 1.526e-5, 'c': 2.874e-9,
                'd': -5.011e-12, 'e': -2.695e-15, 's_eff': 0.320
            }
        }
    
    def calculate_stellar_flux(self, star_temp: float, coeffs: Dict) -> float:
        """
        Calculate stellar flux for different HZ boundaries.
        
        Args:
            star_temp: Stellar effective temperature in Kelvin
            coeffs: Coefficient dictionary for the specific boundary
            
        Returns:
            float: Calculated stellar flux
        """
        t_star = star_temp - 5780  # Difference from Solar temperature
        
        s_eff = (coeffs['s_eff'] + coeffs['a'] * t_star +
                coeffs['b'] * t_star**2 + coeffs['c'] * t_star**3 +
                coeffs['d'] * t_star**4 + coeffs['e'] * t_star**5)
        
        return s_eff
    
    def calculate_habitable_zone(self, star: Star) -> Dict[str, Tuple[float, float]]:
        """
        Calculate habitable zone boundaries using multiple methods.
        
        Args:
            star: Star object with required properties
            
        Returns:
            Dictionary containing different HZ boundary calculations
        """
        try:
            results = {}
            
            # 1. Kopparapu et al. (2013) model
            for boundary, coeffs in self.coefficients.items():
                flux = self.calculate_stellar_flux(star.temperature, coeffs)
                distance = np.sqrt(star.luminosity / flux)
                results[boundary] = distance
            
            # 2. Classic model (as a backup)
            classic_inner = np.sqrt(star.luminosity/1.1)
            classic_outer = np.sqrt(star.luminosity/0.53)
            results['classic'] = (classic_inner, classic_outer)
            
            # 3. Apply corrections for stellar age and activity
            age_factor = 1 + (star.age - 4.6) * 0.1
            activity_factor = 1 - star.activity * 0.2
            
            # Apply corrections to all boundaries
            for key in results:
                if isinstance(results[key], tuple):
                    inner, outer = results[key]
                    results[key] = (
                        inner * age_factor * activity_factor,
                        outer * age_factor * activity_factor
                    )
                else:
                    results[key] *= age_factor * activity_factor
            
            return results
            
        except Exception as e:
            raise PhysicsError(f"Error calculating habitable zone: {str(e)}") from e
    
    def calculate_planet_temperature(self, planet: Planet, star: Star) -> float:
        """
        Calculate planet's effective temperature using enhanced model.
        
        Args:
            planet: Planet object
            star: Host star object
            
        Returns:
            float: Calculated temperature in Kelvin
        """
        try:
            # Convert AU to meters
            distance_m = planet.orbital_distance * PhysicsConstants.AU_TO_METERS
            
            # Calculate stellar flux at planet's distance
            stellar_flux = (star.luminosity * PhysicsConstants.SOLAR_LUMINOSITY) / \
                         (4 * np.pi * distance_m**2)
            
            # Account for eccentricity
            avg_flux = stellar_flux * np.sqrt(1 / (1 - planet.eccentricity**2))
            
            # Calculate effective temperature
            temp = ((avg_flux * (1 - planet.albedo)) / 
                   (4 * PhysicsConstants.STEFAN_BOLTZMANN)) ** 0.25
            
            # Apply atmospheric greenhouse effect
            if planet.atmosphere:
                greenhouse_factor = self._calculate_greenhouse_effect(planet.atmosphere)
                temp *= greenhouse_factor
            
            return temp
            
        except Exception as e:
            raise PhysicsError(f"Error calculating planet temperature: {str(e)}") from e
    
    def _calculate_greenhouse_effect(self, atmosphere: Dict[str, float]) -> float:
        """
        Calculate greenhouse effect factor based on atmospheric composition.
        
        Args:
            atmosphere: Dictionary of atmospheric composition
            
        Returns:
            float: Greenhouse effect factor
        """
        # Simplified greenhouse effect model
        # Could be enhanced with proper radiative transfer calculations
        base_factor = 1.0
        
        # Contribution factors for different gases
        gas_factors = {
            'CO2': 0.3,
            'CH4': 0.4,
            'H2O': 0.2,
            'N2': 0.05,
            'O2': 0.05
        }
        
        for gas, concentration in atmosphere.items():
            if gas in gas_factors:
                base_factor += gas_factors[gas] * concentration
        
        return base_factor
    
    def calculate_orbital_stability(self, planet: Planet) -> bool:
        """
        Calculate if a planet's orbit is stable.
        
        Args:
            planet: Planet object
            
        Returns:
            bool: True if orbit is stable
        """
        if planet.star is None:
            raise PhysicsError("Planet must be associated with a star")
        
        # Check if planet is within Hill sphere
        hill_radius = planet.orbital_distance * (planet.mass / (3 * planet.star.mass))**(1/3)
        
        # Check if planet is within roche limit
        roche_limit = 2.44 * planet.star.radius * (planet.star.mass / planet.mass)**(1/3)
        
        return hill_radius > roche_limit

class PlanetaryDynamics:
    """Calculations for planetary dynamics and evolution."""
    
    @staticmethod
    def calculate_escape_velocity(planet: Planet) -> float:
        """
        Calculate escape velocity for a planet.
        
        Args:
            planet: Planet object
            
        Returns:
            float: Escape velocity in m/s
        """
        mass_kg = planet.mass * PhysicsConstants.EARTH_MASS
        radius_m = planet.radius * PhysicsConstants.EARTH_RADIUS
        
        return np.sqrt(2 * PhysicsConstants.G * mass_kg / radius_m)
    
    @staticmethod
    def calculate_orbital_period(planet: Planet) -> float:
        """
        Calculate orbital period using Kepler's Third Law.
        
        Args:
            planet: Planet object
            
        Returns:
            float: Orbital period in days
        """
        if planet.star is None:
            raise PhysicsError("Planet must be associated with a star")
        
        a = planet.orbital_distance * PhysicsConstants.AU_TO_METERS
        period_seconds = 2 * np.pi * np.sqrt(
            a**3 / (PhysicsConstants.G * planet.star.mass * PhysicsConstants.SOLAR_MASS)
        )
        
        return period_seconds / (24 * 3600)  # Convert to days