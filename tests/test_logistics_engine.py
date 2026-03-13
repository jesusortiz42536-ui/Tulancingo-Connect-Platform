"""
Tests for the logistics_engine (Cargo-GO) module.
"""

import pytest

from logistics_engine.models import Cargo, CargoStatus, Driver, Route, RouteStatus
from logistics_engine.route_manager import RouteManager


# ---------------------------------------------------------------------------
# Driver tests
# ---------------------------------------------------------------------------

class TestDriver:
    def test_create_driver(self):
        d = Driver(name="Ana López", license_number="HID-001", phone="7711234567")
        assert d.name == "Ana López"
        assert d.is_available is True

    def test_assign_and_release(self):
        d = Driver(name="Carlos Ruiz", license_number="HID-002", phone="7719876543")
        d.assign()
        assert d.is_available is False
        d.release()
        assert d.is_available is True

    def test_assign_unavailable_driver_raises(self):
        d = Driver(name="María Pérez", license_number="HID-003", phone="7710001111")
        d.assign()
        with pytest.raises(RuntimeError):
            d.assign()

    def test_empty_name_raises(self):
        with pytest.raises(ValueError):
            Driver(name="  ", license_number="HID-004", phone="7710002222")


# ---------------------------------------------------------------------------
# Cargo tests
# ---------------------------------------------------------------------------

class TestCargo:
    def _make_cargo(self):
        return Cargo(
            description="Paquete de tortillas",
            weight_kg=5.0,
            sender="Tortillería El Sol",
            recipient="Mercado Morelos",
            origin="Colonia Centro",
            destination="Mercado Morelos",
        )

    def test_create_cargo(self):
        c = self._make_cargo()
        assert c.status == CargoStatus.PENDING
        assert c.weight_kg == 5.0

    def test_negative_weight_raises(self):
        with pytest.raises(ValueError):
            Cargo(
                description="x", weight_kg=-1, sender="A", recipient="B",
                origin="O", destination="D",
            )

    def test_lifecycle(self):
        c = self._make_cargo()
        c.mark_in_transit()
        assert c.status == CargoStatus.IN_TRANSIT
        c.mark_delivered()
        assert c.status == CargoStatus.DELIVERED

    def test_cancel(self):
        c = self._make_cargo()
        c.cancel()
        assert c.status == CargoStatus.CANCELLED

    def test_cancel_delivered_raises(self):
        c = self._make_cargo()
        c.mark_in_transit()
        c.mark_delivered()
        with pytest.raises(RuntimeError):
            c.cancel()


# ---------------------------------------------------------------------------
# Route tests
# ---------------------------------------------------------------------------

class TestRoute:
    def _make_driver(self):
        return Driver(name="Juan García", license_number="HID-005", phone="7710003333")

    def _make_cargo(self):
        return Cargo(
            description="Frutas", weight_kg=10.0, sender="Mercado",
            recipient="Restaurante", origin="Mercado", destination="Restaurante",
        )

    def test_route_activate_and_complete(self):
        driver = self._make_driver()
        cargo = self._make_cargo()
        route = Route(origin="Mercado", destination="Restaurante", distance_km=3.5)
        route.add_cargo(cargo)
        route.assign_driver(driver)
        route.activate()
        assert route.status == RouteStatus.ACTIVE
        assert cargo.status == CargoStatus.IN_TRANSIT
        route.complete()
        assert route.status == RouteStatus.COMPLETED
        assert cargo.status == CargoStatus.DELIVERED
        assert driver.is_available is True

    def test_activate_without_driver_raises(self):
        route = Route(origin="A", destination="B", distance_km=1.0)
        with pytest.raises(RuntimeError):
            route.activate()

    def test_total_weight(self):
        route = Route(origin="A", destination="B", distance_km=2.0)
        for w in [3.0, 7.0]:
            route.add_cargo(Cargo(
                description="Item", weight_kg=w, sender="S", recipient="R",
                origin="A", destination="B",
            ))
        assert route.total_weight_kg == 10.0


# ---------------------------------------------------------------------------
# RouteManager tests
# ---------------------------------------------------------------------------

class TestRouteManager:
    def test_full_workflow(self):
        manager = RouteManager()
        driver = Driver(name="Pedro Martínez", license_number="HID-006", phone="7710004444")
        cargo = Cargo(
            description="Verduras", weight_kg=8.0, sender="Campo", recipient="Tienda",
            origin="Epazoyucan", destination="Tulancingo",
        )
        manager.register_driver(driver)
        manager.register_cargo(cargo)

        route = manager.create_route(
            origin="Epazoyucan",
            destination="Tulancingo",
            distance_km=25.0,
            driver_id=driver.driver_id,
            cargo_ids=[cargo.cargo_id],
        )
        manager.activate_route(route.route_id)
        manager.complete_route(route.route_id)

        assert route.status == RouteStatus.COMPLETED
        assert cargo.status == CargoStatus.DELIVERED

    def test_list_available_drivers(self):
        manager = RouteManager()
        d1 = Driver(name="D1", license_number="L1", phone="1")
        d2 = Driver(name="D2", license_number="L2", phone="2")
        manager.register_driver(d1)
        manager.register_driver(d2)
        d1.assign()
        available = manager.list_available_drivers()
        assert d2 in available
        assert d1 not in available

    def test_duplicate_driver_raises(self):
        manager = RouteManager()
        driver = Driver(name="D", license_number="L", phone="0")
        manager.register_driver(driver)
        with pytest.raises(ValueError):
            manager.register_driver(driver)
