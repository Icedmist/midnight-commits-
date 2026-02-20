"""
Inventory Management System
A SQLite-based inventory tracking system with stock management
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Tuple


class InventoryManager:
    """SQLite-based inventory management system"""

    def __init__(self, db_path: str = "inventory.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self) -> None:
        """Initialize the database and create inventory tables"""
        with sqlite3.connect(self.db_path) as conn:
            # Products table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    category TEXT,
                    sku TEXT UNIQUE,
                    unit_price REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Inventory table (stock levels)
            conn.execute('''
                CREATE TABLE IF NOT EXISTS inventory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER,
                    quantity INTEGER DEFAULT 0,
                    min_stock_level INTEGER DEFAULT 0,
                    location TEXT,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products (id)
                )
            ''')

            # Stock movements table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS stock_movements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER,
                    movement_type TEXT NOT NULL,  -- 'IN', 'OUT', 'ADJUSTMENT'
                    quantity INTEGER NOT NULL,
                    reason TEXT,
                    reference TEXT,  -- PO number, invoice, etc.
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products (id)
                )
            ''')

            print("✅ Inventory database initialized")

    def add_product(self, name: str, description: str = "", category: str = "",
                   sku: str = None, unit_price: float = 0.0) -> int:
        """Add a new product and return its ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    INSERT INTO products (name, description, category, sku, unit_price)
                    VALUES (?, ?, ?, ?, ?)
                ''', (name, description, category, sku, unit_price))
                product_id = cursor.lastrowid

                # Initialize inventory record
                conn.execute('''
                    INSERT INTO inventory (product_id, quantity, min_stock_level)
                    VALUES (?, 0, 0)
                ''', (product_id,))

                print(f"✅ Product '{name}' added with ID {product_id}")
                return product_id
        except sqlite3.IntegrityError:
            print(f"❌ SKU '{sku}' already exists")
            return -1
        except Exception as e:
            print(f"❌ Error adding product: {e}")
            return -1

    def update_stock(self, product_id: int, quantity_change: int,
                    movement_type: str, reason: str = "", reference: str = "") -> bool:
        """Update stock level and record movement"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Check if product exists
                cursor = conn.execute('SELECT id FROM products WHERE id = ?', (product_id,))
                if not cursor.fetchone():
                    print(f"❌ Product {product_id} not found")
                    return False

                # Update inventory
                conn.execute('''
                    UPDATE inventory
                    SET quantity = quantity + ?, last_updated = CURRENT_TIMESTAMP
                    WHERE product_id = ?
                ''', (quantity_change, product_id))

                # Record movement
                conn.execute('''
                    INSERT INTO stock_movements (product_id, movement_type, quantity, reason, reference)
                    VALUES (?, ?, ?, ?, ?)
                ''', (product_id, movement_type, quantity_change, reason, reference))

                print(f"✅ Stock updated: {quantity_change:+d} units")
                return True
        except Exception as e:
            print(f"❌ Error updating stock: {e}")
            return False

    def get_product(self, product_id: int) -> Optional[Dict]:
        """Get product with current stock information"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT p.*, i.quantity, i.min_stock_level, i.location, i.last_updated
                FROM products p
                LEFT JOIN inventory i ON p.id = i.product_id
                WHERE p.id = ?
            ''', (product_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def search_products(self, query: str) -> List[Dict]:
        """Search products by name, SKU, or category"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT p.id, p.name, p.sku, p.category, i.quantity, i.min_stock_level
                FROM products p
                LEFT JOIN inventory i ON p.id = i.product_id
                WHERE p.name LIKE ? OR p.sku LIKE ? OR p.category LIKE ?
                ORDER BY p.name
            ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
            return [dict(row) for row in cursor.fetchall()]

    def get_low_stock_items(self) -> List[Dict]:
        """Get products that are below minimum stock level"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT p.id, p.name, p.sku, i.quantity, i.min_stock_level
                FROM products p
                JOIN inventory i ON p.id = i.product_id
                WHERE i.quantity <= i.min_stock_level AND i.min_stock_level > 0
                ORDER BY i.quantity ASC
            ''')
            return [dict(row) for row in cursor.fetchall()]

    def get_stock_movements(self, product_id: int = None, limit: int = 20) -> List[Dict]:
        """Get stock movement history"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            sql = '''
                SELECT sm.*, p.name as product_name
                FROM stock_movements sm
                JOIN products p ON sm.product_id = p.id
            '''
            params = []

            if product_id:
                sql += ' WHERE sm.product_id = ?'
                params.append(product_id)

            sql += ' ORDER BY sm.created_at DESC LIMIT ?'
            params.append(limit)

            cursor = conn.execute(sql, params)
            return [dict(row) for row in cursor.fetchall()]

    def update_product(self, product_id: int, **updates) -> bool:
        """Update product information"""
        if not updates:
            return False

        set_clause = ', '.join(f'{key} = ?' for key in updates.keys())
        values = list(updates.values()) + [product_id]

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(f'''
                    UPDATE products
                    SET {set_clause}, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', values)
                if conn.total_changes > 0:
                    print(f"✅ Product {product_id} updated")
                    return True
                else:
                    print(f"❌ Product {product_id} not found")
                    return False
        except Exception as e:
            print(f"❌ Error updating product: {e}")
            return False

    def set_min_stock_level(self, product_id: int, min_level: int) -> bool:
        """Set minimum stock level for a product"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    UPDATE inventory
                    SET min_stock_level = ?, last_updated = CURRENT_TIMESTAMP
                    WHERE product_id = ?
                ''', (min_level, product_id))
                if conn.total_changes > 0:
                    print(f"✅ Minimum stock level set to {min_level}")
                    return True
                else:
                    print(f"❌ Product {product_id} not found")
                    return False
        except Exception as e:
            print(f"❌ Error setting min stock level: {e}")
            return False

    def get_inventory_stats(self) -> Dict:
        """Get inventory statistics"""
        with sqlite3.connect(self.db_path) as conn:
            # Total products
            cursor = conn.execute('SELECT COUNT(*) FROM products')
            total_products = cursor.fetchone()[0]

            # Total value
            cursor = conn.execute('''
                SELECT SUM(p.unit_price * i.quantity) as total_value
                FROM products p
                JOIN inventory i ON p.id = i.product_id
            ''')
            total_value = cursor.fetchone()[0] or 0

            # Low stock items
            cursor = conn.execute('''
                SELECT COUNT(*) FROM inventory
                WHERE quantity <= min_stock_level AND min_stock_level > 0
            ''')
            low_stock_count = cursor.fetchone()[0]

            # Out of stock
            cursor = conn.execute('SELECT COUNT(*) FROM inventory WHERE quantity = 0')
            out_of_stock = cursor.fetchone()[0]

            return {
                'total_products': total_products,
                'total_value': total_value,
                'low_stock_items': low_stock_count,
                'out_of_stock': out_of_stock
            }


def display_product(product: Dict) -> None:
    """Display product information"""
    print(f"\n📦 Product #{product['id']}: {product['name']}")
    print(f"SKU: {product.get('sku', 'N/A')}")
    print(f"Category: {product.get('category', 'N/A')}")
    print(f"Description: {product.get('description', 'N/A')}")
    print(f"Unit Price: ${product.get('unit_price', 0):.2f}")
    print(f"Current Stock: {product.get('quantity', 0)}")
    print(f"Min Stock Level: {product.get('min_stock_level', 0)}")
    print(f"Location: {product.get('location', 'N/A')}")
    print(f"Last Updated: {product.get('last_updated', 'N/A')}")


def main():
    print("📦 Inventory Management System\n")

    manager = InventoryManager()

    while True:
        print("\n--- Inventory Manager Menu ---")
        print("1. Add product")
        print("2. Update stock")
        print("3. Search products")
        print("4. View product details")
        print("5. Update product info")
        print("6. Set minimum stock level")
        print("7. Show low stock items")
        print("8. View stock movements")
        print("9. Show statistics")
        print("10. Exit")

        choice = input("\nSelect option (1-10): ").strip()

        if choice == '1':
            name = input("Product name: ").strip()
            if not name:
                print("❌ Name is required")
                continue

            description = input("Description (optional): ").strip()
            category = input("Category (optional): ").strip()
            sku = input("SKU (optional): ").strip() or None
            try:
                unit_price = float(input("Unit price (default: 0.00): ").strip() or "0")
            except ValueError:
                unit_price = 0.0

            manager.add_product(name, description, category, sku, unit_price)

        elif choice == '2':
            try:
                product_id = int(input("Product ID: "))
                quantity = int(input("Quantity change (positive for IN, negative for OUT): "))
                movement_type = "IN" if quantity > 0 else "OUT"
                reason = input("Reason: ").strip()
                reference = input("Reference (PO/invoice number): ").strip()

                manager.update_stock(product_id, quantity, movement_type, reason, reference)
            except ValueError:
                print("❌ Invalid input")

        elif choice == '3':
            query = input("Search query: ").strip()
            if query:
                results = manager.search_products(query)
                if results:
                    print(f"\n✅ Found {len(results)} products:")
                    for product in results:
                        stock_status = "⚠️ LOW" if product['quantity'] <= product['min_stock_level'] and product['min_stock_level'] > 0 else "✅ OK"
                        print(f"  {product['id']}: {product['name']} (Stock: {product['quantity']}) {stock_status}")
                else:
                    print("❌ No products found")

        elif choice == '4':
            try:
                product_id = int(input("Product ID: "))
                product = manager.get_product(product_id)
                if product:
                    display_product(product)
                else:
                    print("❌ Product not found")
            except ValueError:
                print("❌ Invalid ID")

        elif choice == '5':
            try:
                product_id = int(input("Product ID: "))
                product = manager.get_product(product_id)
                if not product:
                    print("❌ Product not found")
                    continue

                print("Leave fields empty to keep current values:")
                name = input(f"Name [{product['name']}]: ").strip() or product['name']
                description = input(f"Description [{product.get('description', '')}]: ").strip() or product.get('description', '')
                category = input(f"Category [{product.get('category', '')}]: ").strip() or product.get('category', '')
                sku = input(f"SKU [{product.get('sku', '')}]: ").strip() or product.get('sku', '')

                try:
                    unit_price_str = input(f"Unit price [{product.get('unit_price', 0)}]: ").strip()
                    unit_price = float(unit_price_str) if unit_price_str else product.get('unit_price', 0)
                except ValueError:
                    unit_price = product.get('unit_price', 0)

                updates = {}
                if name != product['name']:
                    updates['name'] = name
                if description != product.get('description', ''):
                    updates['description'] = description
                if category != product.get('category', ''):
                    updates['category'] = category
                if sku != product.get('sku', ''):
                    updates['sku'] = sku
                if unit_price != product.get('unit_price', 0):
                    updates['unit_price'] = unit_price

                if updates:
                    manager.update_product(product_id, **updates)
                else:
                    print("ℹ️ No changes made")

            except ValueError:
                print("❌ Invalid ID")

        elif choice == '6':
            try:
                product_id = int(input("Product ID: "))
                min_level = int(input("Minimum stock level: "))
                manager.set_min_stock_level(product_id, min_level)
            except ValueError:
                print("❌ Invalid input")

        elif choice == '7':
            low_stock = manager.get_low_stock_items()
            if low_stock:
                print(f"\n⚠️ Low Stock Items ({len(low_stock)}):")
                for item in low_stock:
                    print(f"  {item['id']}: {item['name']} - Current: {item['quantity']}, Min: {item['min_stock_level']}")
            else:
                print("✅ All items are above minimum stock levels")

        elif choice == '8':
            product_id_input = input("Product ID (optional): ").strip()
            try:
                product_id = int(product_id_input) if product_id_input else None
                movements = manager.get_stock_movements(product_id)
                if movements:
                    print(f"\n📊 Stock Movements ({len(movements)}):")
                    for movement in movements:
                        print(f"  {movement['created_at'][:19]} | {movement['product_name']} | {movement['movement_type']} {movement['quantity']:+d} | {movement['reason']}")
                else:
                    print("❌ No movements found")
            except ValueError:
                print("❌ Invalid product ID")

        elif choice == '9':
            stats = manager.get_inventory_stats()
            print("\n📊 Inventory Statistics:")
            print(f"Total products: {stats['total_products']}")
            print(f"Total inventory value: ${stats['total_value']:.2f}")
            print(f"Low stock items: {stats['low_stock_items']}")
            print(f"Out of stock items: {stats['out_of_stock']}")

        elif choice == '10':
            print("👋 Goodbye!")
            break

        else:
            print("❌ Invalid option")


if __name__ == "__main__":
    main()
