import sqlite3
from pathlib import Path

DB_PATH = Path("warung_bot.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS menu_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            category TEXT NOT NULL,
            is_available INTEGER DEFAULT 1,
            emoji TEXT DEFAULT '🍽️'
        );

        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER NOT NULL,
            customer_name TEXT NOT NULL,
            table_number INTEGER,
            status TEXT DEFAULT 'pending',
            total_price REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            menu_item_id INTEGER NOT NULL,
            item_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            subtotal REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id),
            FOREIGN KEY (menu_item_id) REFERENCES menu_items(id)
        );
    """)

    # Seed menu awal kalau masih kosong
    count = conn.execute("SELECT COUNT(*) FROM menu_items").fetchone()[0]
    if count == 0:
        sample_menu = [
            ("Pempek Kapal Selam", "Pempek isi telur, disajikan dengan cuko pedas", 15000, "Makanan", "🐟"),
            ("Pempek Lenjer", "Pempek panjang khas Palembang", 8000, "Makanan", "🍢"),
            ("Tekwan", "Sup ikan dengan jamur dan soun", 18000, "Makanan", "🍲"),
            ("Model", "Tahu isi ikan dengan kuah bening", 17000, "Makanan", "🍜"),
            ("Es Kacang Merah", "Es segar kacang merah khas Palembang", 8000, "Minuman", "🧊"),
            ("Es Teh Manis", "Teh manis dingin segar", 5000, "Minuman", "🍵"),
            ("Air Mineral", "Air putih botol 600ml", 4000, "Minuman", "💧"),
        ]
        conn.executemany(
            "INSERT INTO menu_items (name, description, price, category, emoji) VALUES (?, ?, ?, ?, ?)",
            sample_menu
        )

    conn.commit()
    conn.close()

# ─── Menu ────────────────────────────────────────────────
def get_categories():
    conn = get_conn()
    cats = conn.execute(
        "SELECT DISTINCT category FROM menu_items WHERE is_available = 1"
    ).fetchall()
    conn.close()
    return [row["category"] for row in cats]

def get_menu_by_category(category: str):
    conn = get_conn()
    items = conn.execute(
        "SELECT * FROM menu_items WHERE category = ? AND is_available = 1", (category,)
    ).fetchall()
    conn.close()
    return [dict(i) for i in items]

def get_menu_item(item_id: int):
    conn = get_conn()
    item = conn.execute("SELECT * FROM menu_items WHERE id = ?", (item_id,)).fetchone()
    conn.close()
    return dict(item) if item else None

def get_all_menu():
    conn = get_conn()
    items = conn.execute("SELECT * FROM menu_items WHERE is_available = 1").fetchall()
    conn.close()
    return [dict(i) for i in items]

# ─── Orders ──────────────────────────────────────────────
def create_order(telegram_id, customer_name, table_number, items: list):
    """items: list of (menu_item_id, quantity)"""
    conn = get_conn()
    total = 0
    enriched = []
    for menu_item_id, quantity in items:
        menu = conn.execute("SELECT * FROM menu_items WHERE id = ?", (menu_item_id,)).fetchone()
        if not menu:
            conn.close()
            raise ValueError(f"Menu ID {menu_item_id} tidak ditemukan")
        subtotal = menu["price"] * quantity
        total += subtotal
        enriched.append((menu_item_id, menu["name"], quantity, subtotal))

    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO orders (telegram_id, customer_name, table_number, total_price) VALUES (?, ?, ?, ?)",
        (telegram_id, customer_name, table_number, total)
    )
    order_id = cursor.lastrowid

    for menu_item_id, item_name, quantity, subtotal in enriched:
        cursor.execute(
            "INSERT INTO order_items (order_id, menu_item_id, item_name, quantity, subtotal) VALUES (?, ?, ?, ?, ?)",
            (order_id, menu_item_id, item_name, quantity, subtotal)
        )

    conn.commit()
    conn.close()
    return order_id, total

def get_orders_by_user(telegram_id: int):
    conn = get_conn()
    orders = conn.execute(
        "SELECT * FROM orders WHERE telegram_id = ? ORDER BY created_at DESC LIMIT 5",
        (telegram_id,)
    ).fetchall()
    conn.close()
    return [dict(o) for o in orders]

def get_order_detail(order_id: int):
    conn = get_conn()
    order = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    if not order:
        conn.close()
        return None
    items = conn.execute(
        "SELECT * FROM order_items WHERE order_id = ?", (order_id,)
    ).fetchall()
    conn.close()
    return {**dict(order), "items": [dict(i) for i in items]}

def get_all_orders(status: str = None):
    conn = get_conn()
    if status:
        orders = conn.execute(
            "SELECT * FROM orders WHERE status = ? ORDER BY created_at DESC", (status,)
        ).fetchall()
    else:
        orders = conn.execute(
            "SELECT * FROM orders ORDER BY created_at DESC LIMIT 20"
        ).fetchall()
    conn.close()
    return [dict(o) for o in orders]

def update_order_status(order_id: int, status: str):
    conn = get_conn()
    conn.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
    conn.commit()
    conn.close()
