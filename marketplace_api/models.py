"""
Python model classes for the Ventul marketplace API.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class WalletTxnType(str, Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    PAYMENT = "payment"
    REFUND = "refund"


@dataclass
class Vendor:
    """A local business registered on the Ventul marketplace."""

    business_name: str
    owner_name: str
    category: str
    address: str
    phone: str
    email: str
    vendor_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.email or "@" not in self.email:
            raise ValueError("A valid email address is required.")
        if not self.business_name.strip():
            raise ValueError("Business name must not be empty.")

    def deactivate(self) -> None:
        self.is_active = False

    def activate(self) -> None:
        self.is_active = True


@dataclass
class Product:
    """A product or service listed by a vendor."""

    vendor_id: str
    name: str
    price: float
    description: str = ""
    stock: int = 0
    is_available: bool = True
    product_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if self.price < 0:
            raise ValueError("Price must be non-negative.")
        if self.stock < 0:
            raise ValueError("Stock must be non-negative.")

    def reduce_stock(self, quantity: int) -> None:
        """Reduce product stock by the given quantity."""
        if quantity <= 0:
            raise ValueError("Quantity must be positive.")
        if self.stock < quantity:
            raise RuntimeError(f"Insufficient stock for product '{self.name}'.")
        self.stock -= quantity

    def replenish_stock(self, quantity: int) -> None:
        """Add stock to the product."""
        if quantity <= 0:
            raise ValueError("Quantity must be positive.")
        self.stock += quantity


@dataclass
class WalletTransaction:
    """Records a single credit or debit on a Ventul wallet."""

    wallet_id: str
    amount: float          # positive = credit, negative = debit
    txn_type: WalletTxnType
    description: str = ""
    reference_id: Optional[str] = None
    txn_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if self.amount == 0:
            raise ValueError("Transaction amount must not be zero.")


@dataclass
class Wallet:
    """Ventul electronic wallet tied to a consumer or vendor."""

    owner_id: str
    owner_type: str         # 'consumer' or 'vendor'
    currency: str = "MXN"
    balance: float = 0.0
    is_active: bool = True
    wallet_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    _transactions: List[WalletTransaction] = field(default_factory=list, repr=False)

    def __post_init__(self) -> None:
        if self.balance < 0:
            raise ValueError("Initial wallet balance must be non-negative.")
        if self.owner_type not in ("consumer", "vendor"):
            raise ValueError("owner_type must be 'consumer' or 'vendor'.")

    def deposit(self, amount: float, description: str = "") -> WalletTransaction:
        """Credit funds to the wallet."""
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")
        self.balance += amount
        txn = WalletTransaction(
            wallet_id=self.wallet_id,
            amount=amount,
            txn_type=WalletTxnType.DEPOSIT,
            description=description,
        )
        self._transactions.append(txn)
        return txn

    def withdraw(self, amount: float, description: str = "") -> WalletTransaction:
        """Debit funds from the wallet."""
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive.")
        if self.balance < amount:
            raise RuntimeError("Insufficient wallet balance.")
        self.balance -= amount
        txn = WalletTransaction(
            wallet_id=self.wallet_id,
            amount=-amount,
            txn_type=WalletTxnType.WITHDRAWAL,
            description=description,
        )
        self._transactions.append(txn)
        return txn

    def pay(self, amount: float, reference_id: Optional[str] = None) -> WalletTransaction:
        """Debit funds as a marketplace payment."""
        if amount <= 0:
            raise ValueError("Payment amount must be positive.")
        if self.balance < amount:
            raise RuntimeError("Insufficient wallet balance for payment.")
        self.balance -= amount
        txn = WalletTransaction(
            wallet_id=self.wallet_id,
            amount=-amount,
            txn_type=WalletTxnType.PAYMENT,
            description="Marketplace payment",
            reference_id=reference_id,
        )
        self._transactions.append(txn)
        return txn

    @property
    def transaction_history(self) -> List[WalletTransaction]:
        return list(self._transactions)


@dataclass
class Transaction:
    """A completed marketplace purchase transaction."""

    order_id: str
    buyer_wallet_id: str
    vendor_id: str
    total_amount: float
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def confirm(self) -> None:
        if self.status != OrderStatus.PENDING:
            raise RuntimeError(f"Cannot confirm order in status {self.status}.")
        self.status = OrderStatus.CONFIRMED

    def ship(self) -> None:
        if self.status != OrderStatus.CONFIRMED:
            raise RuntimeError(f"Cannot ship order in status {self.status}.")
        self.status = OrderStatus.SHIPPED

    def deliver(self) -> None:
        if self.status != OrderStatus.SHIPPED:
            raise RuntimeError(f"Cannot deliver order in status {self.status}.")
        self.status = OrderStatus.DELIVERED

    def cancel(self) -> None:
        if self.status in (OrderStatus.DELIVERED, OrderStatus.CANCELLED):
            raise RuntimeError(f"Cannot cancel order in status {self.status}.")
        self.status = OrderStatus.CANCELLED
