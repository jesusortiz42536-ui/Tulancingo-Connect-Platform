"""
Data models for the Cargo-GO logistics engine.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class CargoStatus(str, Enum):
    PENDING = "pending"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class RouteStatus(str, Enum):
    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class Driver:
    """Represents a Cargo-GO delivery driver."""

    name: str
    license_number: str
    phone: str
    driver_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    is_available: bool = True

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Driver name must not be empty.")
        if not self.license_number.strip():
            raise ValueError("License number must not be empty.")

    def assign(self) -> None:
        """Mark the driver as unavailable (assigned to a route)."""
        if not self.is_available:
            raise RuntimeError(f"Driver {self.name} is already assigned.")
        self.is_available = False

    def release(self) -> None:
        """Mark the driver as available after completing a route."""
        self.is_available = True


@dataclass
class Cargo:
    """Represents a shipment handled by Cargo-GO."""

    description: str
    weight_kg: float
    sender: str
    recipient: str
    origin: str
    destination: str
    cargo_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: CargoStatus = CargoStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if self.weight_kg <= 0:
            raise ValueError("Cargo weight must be positive.")

    def mark_in_transit(self) -> None:
        if self.status != CargoStatus.PENDING:
            raise RuntimeError(f"Cannot move cargo {self.cargo_id} to IN_TRANSIT from {self.status}.")
        self.status = CargoStatus.IN_TRANSIT

    def mark_delivered(self) -> None:
        if self.status != CargoStatus.IN_TRANSIT:
            raise RuntimeError(f"Cannot mark cargo {self.cargo_id} as DELIVERED from {self.status}.")
        self.status = CargoStatus.DELIVERED

    def cancel(self) -> None:
        if self.status in (CargoStatus.DELIVERED, CargoStatus.CANCELLED):
            raise RuntimeError(f"Cannot cancel cargo {self.cargo_id} with status {self.status}.")
        self.status = CargoStatus.CANCELLED


@dataclass
class Route:
    """Represents a delivery route in the Tulancingo network."""

    origin: str
    destination: str
    distance_km: float
    driver: Optional[Driver] = None
    cargo_items: list[Cargo] = field(default_factory=list)
    route_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: RouteStatus = RouteStatus.PLANNED
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if self.distance_km <= 0:
            raise ValueError("Route distance must be positive.")

    def add_cargo(self, cargo: Cargo) -> None:
        """Attach a cargo item to this route."""
        if cargo in self.cargo_items:
            raise ValueError(f"Cargo {cargo.cargo_id} is already on this route.")
        self.cargo_items.append(cargo)

    def assign_driver(self, driver: Driver) -> None:
        """Assign a driver to this route."""
        driver.assign()
        self.driver = driver

    def activate(self) -> None:
        """Start the route (move cargo to IN_TRANSIT)."""
        if self.status != RouteStatus.PLANNED:
            raise RuntimeError(f"Route {self.route_id} is not in PLANNED status.")
        if self.driver is None:
            raise RuntimeError("A driver must be assigned before activating a route.")
        for cargo in self.cargo_items:
            cargo.mark_in_transit()
        self.status = RouteStatus.ACTIVE

    def complete(self) -> None:
        """Complete the route and mark all cargo as DELIVERED."""
        if self.status != RouteStatus.ACTIVE:
            raise RuntimeError(f"Route {self.route_id} is not ACTIVE.")
        for cargo in self.cargo_items:
            cargo.mark_delivered()
        if self.driver:
            self.driver.release()
        self.status = RouteStatus.COMPLETED

    @property
    def total_weight_kg(self) -> float:
        """Total weight of all cargo items on this route."""
        return sum(c.weight_kg for c in self.cargo_items)
