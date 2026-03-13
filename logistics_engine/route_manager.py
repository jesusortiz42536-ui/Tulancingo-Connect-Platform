"""
RouteManager — orchestrates route planning, assignment, and execution for Cargo-GO.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from .models import Cargo, Driver, Route, RouteStatus


class RouteManager:
    """
    Central manager for Cargo-GO logistics operations.

    Responsibilities:
    - Register drivers and cargo
    - Plan and assign routes
    - Track active and completed routes
    """

    def __init__(self) -> None:
        self._drivers: Dict[str, Driver] = {}
        self._cargo: Dict[str, Cargo] = {}
        self._routes: Dict[str, Route] = {}

    # ------------------------------------------------------------------
    # Driver management
    # ------------------------------------------------------------------

    def register_driver(self, driver: Driver) -> None:
        """Register a new driver with the system."""
        if driver.driver_id in self._drivers:
            raise ValueError(f"Driver {driver.driver_id} is already registered.")
        self._drivers[driver.driver_id] = driver

    def get_driver(self, driver_id: str) -> Driver:
        """Retrieve a driver by ID."""
        try:
            return self._drivers[driver_id]
        except KeyError:
            raise KeyError(f"Driver '{driver_id}' not found.") from None

    def list_available_drivers(self) -> List[Driver]:
        """Return all drivers currently available for assignment."""
        return [d for d in self._drivers.values() if d.is_available]

    # ------------------------------------------------------------------
    # Cargo management
    # ------------------------------------------------------------------

    def register_cargo(self, cargo: Cargo) -> None:
        """Register a new cargo item."""
        if cargo.cargo_id in self._cargo:
            raise ValueError(f"Cargo {cargo.cargo_id} is already registered.")
        self._cargo[cargo.cargo_id] = cargo

    def get_cargo(self, cargo_id: str) -> Cargo:
        """Retrieve a cargo item by ID."""
        try:
            return self._cargo[cargo_id]
        except KeyError:
            raise KeyError(f"Cargo '{cargo_id}' not found.") from None

    # ------------------------------------------------------------------
    # Route management
    # ------------------------------------------------------------------

    def create_route(
        self,
        origin: str,
        destination: str,
        distance_km: float,
        driver_id: Optional[str] = None,
        cargo_ids: Optional[List[str]] = None,
    ) -> Route:
        """
        Create a new route, optionally assigning a driver and cargo.

        Args:
            origin: Starting location name.
            destination: Ending location name.
            distance_km: Estimated route distance in kilometres.
            driver_id: Optional driver ID to assign immediately.
            cargo_ids: Optional list of cargo IDs to attach to the route.

        Returns:
            The newly created Route.
        """
        route = Route(origin=origin, destination=destination, distance_km=distance_km)

        if driver_id is not None:
            driver = self.get_driver(driver_id)
            route.assign_driver(driver)

        for cid in cargo_ids or []:
            cargo = self.get_cargo(cid)
            route.add_cargo(cargo)

        self._routes[route.route_id] = route
        return route

    def get_route(self, route_id: str) -> Route:
        """Retrieve a route by ID."""
        try:
            return self._routes[route_id]
        except KeyError:
            raise KeyError(f"Route '{route_id}' not found.") from None

    def activate_route(self, route_id: str) -> Route:
        """Activate a planned route, transitioning cargo to IN_TRANSIT."""
        route = self.get_route(route_id)
        route.activate()
        return route

    def complete_route(self, route_id: str) -> Route:
        """Complete an active route, marking all cargo as DELIVERED."""
        route = self.get_route(route_id)
        route.complete()
        return route

    def list_routes(self, status: Optional[RouteStatus] = None) -> List[Route]:
        """Return all routes, optionally filtered by status."""
        routes = list(self._routes.values())
        if status is not None:
            routes = [r for r in routes if r.status == status]
        return routes
