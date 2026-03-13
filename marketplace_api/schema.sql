-- ============================================================
-- Ventul Marketplace — Database Schema
-- Platform: Tulancingo Connect Platform
-- ============================================================

-- ============================================================
-- Vendors
-- ============================================================
CREATE TABLE IF NOT EXISTS vendors (
    vendor_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_name   VARCHAR(255)  NOT NULL,
    owner_name      VARCHAR(255)  NOT NULL,
    category        VARCHAR(100)  NOT NULL,
    address         TEXT          NOT NULL,
    phone           VARCHAR(30)   NOT NULL,
    email           VARCHAR(255)  UNIQUE NOT NULL,
    is_active       BOOLEAN       NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

-- ============================================================
-- Products / Services
-- ============================================================
CREATE TABLE IF NOT EXISTS products (
    product_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vendor_id       UUID          NOT NULL REFERENCES vendors(vendor_id) ON DELETE CASCADE,
    name            VARCHAR(255)  NOT NULL,
    description     TEXT,
    price           NUMERIC(12,2) NOT NULL CHECK (price >= 0),
    stock           INTEGER       NOT NULL DEFAULT 0 CHECK (stock >= 0),
    is_available    BOOLEAN       NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

-- ============================================================
-- Ventul Electronic Wallets
-- ============================================================
CREATE TABLE IF NOT EXISTS wallets (
    wallet_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id        UUID          NOT NULL,          -- references users table (external)
    owner_type      VARCHAR(50)   NOT NULL,          -- 'consumer' | 'vendor'
    balance         NUMERIC(14,2) NOT NULL DEFAULT 0.00 CHECK (balance >= 0),
    currency        CHAR(3)       NOT NULL DEFAULT 'MXN',
    is_active       BOOLEAN       NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

-- ============================================================
-- Wallet Transactions (credits and debits)
-- ============================================================
CREATE TABLE IF NOT EXISTS wallet_transactions (
    txn_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    wallet_id       UUID          NOT NULL REFERENCES wallets(wallet_id) ON DELETE RESTRICT,
    amount          NUMERIC(14,2) NOT NULL,          -- positive = credit, negative = debit
    txn_type        VARCHAR(50)   NOT NULL,          -- 'deposit' | 'withdrawal' | 'payment' | 'refund'
    description     TEXT,
    reference_id    UUID,                            -- optional order/invoice reference
    created_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

-- ============================================================
-- Marketplace Orders
-- ============================================================
CREATE TABLE IF NOT EXISTS orders (
    order_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    buyer_wallet_id UUID          NOT NULL REFERENCES wallets(wallet_id) ON DELETE RESTRICT,
    vendor_id       UUID          NOT NULL REFERENCES vendors(vendor_id) ON DELETE RESTRICT,
    total_amount    NUMERIC(14,2) NOT NULL CHECK (total_amount >= 0),
    status          VARCHAR(50)   NOT NULL DEFAULT 'pending',  -- pending | confirmed | shipped | delivered | cancelled
    created_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

-- ============================================================
-- Order Line Items
-- ============================================================
CREATE TABLE IF NOT EXISTS order_items (
    item_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id        UUID          NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    product_id      UUID          NOT NULL REFERENCES products(product_id) ON DELETE RESTRICT,
    quantity        INTEGER       NOT NULL CHECK (quantity > 0),
    unit_price      NUMERIC(12,2) NOT NULL CHECK (unit_price >= 0)
);

-- ============================================================
-- Indexes for common query patterns
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_products_vendor  ON products (vendor_id);
CREATE INDEX IF NOT EXISTS idx_orders_vendor    ON orders   (vendor_id);
CREATE INDEX IF NOT EXISTS idx_orders_wallet    ON orders   (buyer_wallet_id);
CREATE INDEX IF NOT EXISTS idx_wallet_txn_wid   ON wallet_transactions (wallet_id);
