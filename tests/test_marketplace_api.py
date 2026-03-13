"""
Tests for the marketplace_api (Ventul) module.
"""

import pytest

from marketplace_api.models import (
    OrderStatus,
    Product,
    Transaction,
    Vendor,
    Wallet,
    WalletTxnType,
)


# ---------------------------------------------------------------------------
# Vendor tests
# ---------------------------------------------------------------------------

class TestVendor:
    def test_create_vendor(self):
        v = Vendor(
            business_name="Tacos El Compadre",
            owner_name="Roberto Sánchez",
            category="Food",
            address="Calle 5 de Mayo, Tulancingo",
            phone="7711112233",
            email="tacos@compadre.mx",
        )
        assert v.is_active is True

    def test_invalid_email_raises(self):
        with pytest.raises(ValueError):
            Vendor(
                business_name="Test",
                owner_name="Test",
                category="Food",
                address="Addr",
                phone="0",
                email="not-an-email",
            )

    def test_deactivate_and_activate(self):
        v = Vendor(
            business_name="Farmacia Cruz Verde",
            owner_name="Laura Torres",
            category="Pharmacy",
            address="Blvd. Valle, Tulancingo",
            phone="7712223344",
            email="cruzv@example.mx",
        )
        v.deactivate()
        assert v.is_active is False
        v.activate()
        assert v.is_active is True


# ---------------------------------------------------------------------------
# Product tests
# ---------------------------------------------------------------------------

class TestProduct:
    def _make_product(self, stock=10):
        return Product(vendor_id="v-1", name="Aguacate", price=15.50, stock=stock)

    def test_create_product(self):
        p = self._make_product()
        assert p.price == 15.50
        assert p.stock == 10

    def test_negative_price_raises(self):
        with pytest.raises(ValueError):
            Product(vendor_id="v-1", name="X", price=-1.0)

    def test_reduce_stock(self):
        p = self._make_product(stock=10)
        p.reduce_stock(3)
        assert p.stock == 7

    def test_insufficient_stock_raises(self):
        p = self._make_product(stock=2)
        with pytest.raises(RuntimeError):
            p.reduce_stock(5)

    def test_replenish_stock(self):
        p = self._make_product(stock=5)
        p.replenish_stock(10)
        assert p.stock == 15


# ---------------------------------------------------------------------------
# Wallet tests
# ---------------------------------------------------------------------------

class TestWallet:
    def _make_wallet(self, balance=0.0):
        return Wallet(owner_id="u-1", owner_type="consumer", balance=balance)

    def test_deposit(self):
        w = self._make_wallet()
        txn = w.deposit(200.0, "Initial top-up")
        assert w.balance == 200.0
        assert txn.txn_type == WalletTxnType.DEPOSIT

    def test_withdraw(self):
        w = self._make_wallet(balance=500.0)
        txn = w.withdraw(100.0)
        assert w.balance == 400.0
        assert txn.amount == -100.0

    def test_insufficient_balance_raises(self):
        w = self._make_wallet(balance=50.0)
        with pytest.raises(RuntimeError):
            w.withdraw(100.0)

    def test_pay(self):
        w = self._make_wallet(balance=300.0)
        txn = w.pay(150.0, reference_id="order-abc")
        assert w.balance == 150.0
        assert txn.reference_id == "order-abc"

    def test_transaction_history(self):
        w = self._make_wallet()
        w.deposit(100.0)
        w.deposit(50.0)
        assert len(w.transaction_history) == 2

    def test_invalid_owner_type_raises(self):
        with pytest.raises(ValueError):
            Wallet(owner_id="u-1", owner_type="admin")

    def test_negative_initial_balance_raises(self):
        with pytest.raises(ValueError):
            Wallet(owner_id="u-1", owner_type="consumer", balance=-10.0)


# ---------------------------------------------------------------------------
# Transaction (order) tests
# ---------------------------------------------------------------------------

class TestTransaction:
    def test_order_lifecycle(self):
        t = Transaction(
            order_id="ord-1",
            buyer_wallet_id="w-1",
            vendor_id="v-1",
            total_amount=250.0,
        )
        assert t.status == OrderStatus.PENDING
        t.confirm()
        assert t.status == OrderStatus.CONFIRMED
        t.ship()
        assert t.status == OrderStatus.SHIPPED
        t.deliver()
        assert t.status == OrderStatus.DELIVERED

    def test_cancel_order(self):
        t = Transaction(order_id="ord-2", buyer_wallet_id="w-2", vendor_id="v-2", total_amount=50.0)
        t.cancel()
        assert t.status == OrderStatus.CANCELLED

    def test_cancel_delivered_raises(self):
        t = Transaction(order_id="ord-3", buyer_wallet_id="w-3", vendor_id="v-3", total_amount=100.0)
        t.confirm()
        t.ship()
        t.deliver()
        with pytest.raises(RuntimeError):
            t.cancel()
