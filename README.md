# Tulancingo Connect Platform

> **Digitalizing Tulancingo's economy — one neighborhood at a time.**

Tulancingo Connect Platform is a hyper-local digital ecosystem designed to
empower the businesses, citizens, and institutions of Tulancingo de Bravo,
Hidalgo. The platform knits together local commerce, professional logistics,
civic participation, and enterprise-grade security into a single, cohesive
foundation.

---

## Vision

Tulancingo has a vibrant informal economy, a deeply rooted civic tradition,
and thousands of talented local entrepreneurs who deserve modern digital
tools. This platform delivers those tools without requiring vendors or
citizens to adopt complex third-party services. Everything is purpose-built
for the local context: street names, peso-denominated wallets, Spanish-first
interfaces, and privacy-first design.

**Core principles:**

- **Local first** — every feature is designed around Tulancingo's real
  geography, culture, and commerce patterns.
- **Inclusive access** — intuitive enough for first-time smartphone users,
  powerful enough for established businesses.
- **Trustworthy** — biometric security and transparent civic processes build
  confidence in the digital economy.
- **Open architecture** — modular Python packages that integrate easily with
  existing municipal systems.

---

## Platform Components

### 🚚 `logistics_engine` — Cargo-GO

Route-management backbone for local deliveries.

| Class | Responsibility |
|---|---|
| `Driver` | Represents a registered Cargo-GO delivery driver |
| `Cargo` | A shipment with lifecycle tracking (pending → in_transit → delivered) |
| `Route` | A delivery route linking origin, destination, driver, and cargo |
| `RouteManager` | Orchestrates driver registration, route planning, and dispatch |

```python
from logistics_engine import RouteManager, Driver, Cargo

manager = RouteManager()
driver = Driver(name="Ana López", license_number="HID-001", phone="7711234567")
manager.register_driver(driver)
cargo = Cargo(
    description="Caja de aguacates",
    weight_kg=12.5,
    sender="Rancho La Esperanza",
    recipient="Mercado Morelos",
    origin="Singuilucan",
    destination="Tulancingo Centro",
)
manager.register_cargo(cargo)
route = manager.create_route(
    origin="Singuilucan",
    destination="Tulancingo Centro",
    distance_km=18.0,
    driver_id=driver.driver_id,
    cargo_ids=[cargo.cargo_id],
)
manager.activate_route(route.route_id)
manager.complete_route(route.route_id)
```

---

### 🛍️ `marketplace_api` — Ventul

Database schema and model layer for Tulancingo's local e-commerce marketplace.

**Database schema** (`schema.sql`) includes:

- `vendors` — registered local businesses
- `products` — listings with inventory tracking
- `wallets` — Ventul electronic wallets (consumer and vendor)
- `wallet_transactions` — full audit trail of credits and debits
- `orders` / `order_items` — purchase lifecycle management

**Python models** provide in-process representations of the same concepts,
including `Wallet.deposit()`, `Wallet.pay()`, and order-status transitions.

```python
from marketplace_api import Vendor, Wallet

vendor = Vendor(
    business_name="Tortillería El Sol",
    owner_name="Roberto Sánchez",
    category="Food",
    address="Calle 5 de Mayo, Tulancingo",
    phone="7711112233",
    email="elsol@tortilleria.mx",
)

wallet = Wallet(owner_id=vendor.vendor_id, owner_type="vendor")
wallet.deposit(500.0, "Initial balance")
wallet.withdraw(50.0, "Marketplace fee")
print(wallet.balance)  # 450.0
```

---

### 🏛️ `civic_forum` — Denarytor

Community engagement engine for public reports and structured debates.

| Class | Responsibility |
|---|---|
| `Report` | A citizen-submitted issue (pothole, broken light, etc.) with status tracking |
| `Debate` | A moderated community topic open to citizen votes |
| `Vote` | A single citizen vote (for / against / abstain) on a debate |
| `CivicForum` | Central manager for submitting, reviewing, and resolving reports and debates |

```python
from civic_forum import CivicForum
from civic_forum.models import ReportCategory, VoteChoice

forum = CivicForum()

# Submit a public report
report = forum.submit_report(
    title="Bache en Av. Morelos",
    description="Gran bache frente al Mercado Morelos.",
    category=ReportCategory.INFRASTRUCTURE,
    location="Av. Morelos, Tulancingo",
    submitted_by="citizen-uuid",
)
forum.resolve_report(report.report_id)

# Open a community debate
debate = forum.open_debate(
    title="¿Nueva ciclovía en Blvd. Valle?",
    description="Propuesta para habilitar carril bici en Blvd. del Valle.",
    created_by="authority-001",
)
forum.vote_on_debate(debate.debate_id, "citizen-1", VoteChoice.FOR)
print(debate.tally)  # {'for': 1, 'against': 0, 'abstain': 0}
```

---

### 🔒 `security_gateway` — EyeLock™ Biometric Auth

Integration stubs for enterprise iris-recognition authentication via
[EyeLock™](https://www.eyelock.com/).

> **Note:** All methods in this module are stubs. Replace the stub bodies
> with real EyeLock™ SDK calls when the vendor library is available.
> Raw biometric data is **never** stored — only a one-way hash is kept in
> stub mode.

```python
from security_gateway import BiometricAuthGateway

gateway = BiometricAuthGateway()

# Enroll a user
gateway.enroll("user-uuid", b"<iris_scan_bytes>")

# Authenticate
result = gateway.authenticate("user-uuid", b"<iris_scan_bytes>")
print(result.is_successful)  # True

# Revoke on account closure
gateway.revoke("user-uuid")

# Health check
print(gateway.health_check())
```

---

## Project Structure

```
Tulancingo-Connect-Platform/
├── logistics_engine/          # Cargo-GO route management
│   ├── __init__.py
│   ├── models.py              # Driver, Cargo, Route dataclasses
│   └── route_manager.py      # RouteManager orchestration class
├── marketplace_api/           # Ventul local marketplace
│   ├── __init__.py
│   ├── models.py              # Vendor, Product, Wallet, Transaction models
│   └── schema.sql             # PostgreSQL DDL for all marketplace tables
├── civic_forum/               # Denarytor civic engagement
│   ├── __init__.py
│   ├── models.py              # Report, Debate, Vote dataclasses
│   └── forum.py               # CivicForum manager class
├── security_gateway/          # EyeLock™ biometric auth stubs
│   ├── __init__.py
│   └── eyelock_stub.py        # BiometricAuthGateway stub implementation
└── tests/                     # Pytest test suite
    ├── test_logistics_engine.py
    ├── test_marketplace_api.py
    ├── test_civic_forum.py
    └── test_security_gateway.py
```

---

## Getting Started

### Requirements

- Python 3.10+
- `pytest` for running the test suite

### Installation

```bash
# Clone the repository
git clone https://github.com/jesusortiz42536-ui/Tulancingo-Connect-Platform.git
cd Tulancingo-Connect-Platform

# (Optional) create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

### Running Tests

```bash
pytest tests/ -v
```

---

## Roadmap

- [ ] REST API layer (FastAPI) for all four modules
- [ ] PostgreSQL persistence layer wired to `marketplace_api/schema.sql`
- [ ] EyeLock™ SDK integration replacing stubs in `security_gateway`
- [ ] React / React Native front-end for consumers and vendors
- [ ] SMS/push notification system for civic report status updates
- [ ] Municipal authority dashboard for Denarytor report management

---

## License

This project is licensed under the terms of the [LICENSE](LICENSE) file
included in this repository.

---

*Built with ❤️ for Tulancingo de Bravo, Hidalgo, México.*

