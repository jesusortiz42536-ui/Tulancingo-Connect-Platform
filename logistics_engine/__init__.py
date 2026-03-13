"""
logistics_engine — Cargo-GO route management module.

Provides core classes for managing cargo routes, drivers, and shipments
within the Tulancingo local delivery network.
"""

from .models import Cargo, Driver, Route
from .route_manager import RouteManager

__all__ = ["Cargo", "Driver", "Route", "RouteManager"]
