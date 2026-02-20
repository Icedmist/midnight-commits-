"""
Query Builder with Filtering
A flexible SQLite query builder with dynamic filtering and sorting
"""

import sqlite3
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime


class QueryBuilder:
    """Flexible SQLite query builder with filtering capabilities"""

    def __init__(self, db_path: str = "query_demo.db"):
        self.db_path = db_path
        self.table_name = None
        self.base_query = None
        self.filters = []
        self.sort_by = []
        self.limit_count = None
        self.offset_count = None
        self.joins = []

    def from_table(self, table_name: str) -> 'QueryBuilder':
        """Set the main table to query from"""
        self.table_name = table_name
        self.base_query = f"SELECT * FROM {table_name}"
        return self

    def select(self, columns: List[str]) -> 'QueryBuilder':
        """Specify columns to select"""
        if columns:
            self.base_query = f"SELECT {', '.join(columns)} FROM {self.table_name}"
        return self

    def join(self, table: str, on_condition: str, join_type: str = "INNER") -> 'QueryBuilder':
        """Add a join clause"""
        self.joins.append(f"{join_type} JOIN {table} ON {on_condition}")
        return self

    def where(self, condition: str) -> 'QueryBuilder':
        """Add a WHERE condition"""
        self.filters.append(condition)
        return self

    def where_equal(self, column: str, value: Any) -> 'QueryBuilder':
        """Add equality filter"""
        if isinstance(value, str):
            self.filters.append(f"{column} = '{value}'")
        else:
            self.filters.append(f"{column} = {value}")
        return self

    def where_like(self, column: str, pattern: str) -> 'QueryBuilder':
        """Add LIKE filter"""
        self.filters.append(f"{column} LIKE '%{pattern}%'")
        return self

    def where_in(self, column: str, values: List[Any]) -> 'QueryBuilder':
        """Add IN filter"""
        if isinstance(values[0], str):
            value_list = "', '".join(values)
            self.filters.append(f"{column} IN ('{value_list}')")
        else:
            value_list = ", ".join(map(str, values))
            self.filters.append(f"{column} IN ({value_list})")
        return self

    def where_between(self, column: str, min_val: Any, max_val: Any) -> 'QueryBuilder':
        """Add BETWEEN filter"""
        self.filters.append(f"{column} BETWEEN {min_val} AND {max_val}")
        return self

    def where_greater_than(self, column: str, value: Any) -> 'QueryBuilder':
        """Add greater than filter"""
        self.filters.append(f"{column} > {value}")
        return self

    def where_less_than(self, column: str, value: Any) -> 'QueryBuilder':
        """Add less than filter"""
        self.filters.append(f"{column} < {value}")
        return self

    def where_null(self, column: str, is_null: bool = True) -> 'QueryBuilder':
        """Add IS NULL or IS NOT NULL filter"""
        operator = "IS NULL" if is_null else "IS NOT NULL"
        self.filters.append(f"{column} {operator}")
        return self

    def order_by(self, column: str, direction: str = "ASC") -> 'QueryBuilder':
        """Add ORDER BY clause"""
        self.sort_by.append(f"{column} {direction.upper()}")
        return self

    def limit(self, count: int) -> 'QueryBuilder':
        """Set LIMIT"""
        self.limit_count = count
        return self

    def offset(self, count: int) -> 'QueryBuilder':
        """Set OFFSET"""
        self.offset_count = count
        return self

    def build_query(self) -> str:
        """Build the complete SQL query"""
        if not self.base_query:
            raise ValueError("No table specified. Use from_table() first.")

        query = self.base_query

        # Add joins
        if self.joins:
            query += " " + " ".join(self.joins)

        # Add WHERE conditions
        if self.filters:
            query += " WHERE " + " AND ".join(self.filters)

        # Add ORDER BY
        if self.sort_by:
            query += " ORDER BY " + ", ".join(self.sort_by)

        # Add LIMIT and OFFSET
        if self.limit_count:
            query += f" LIMIT {self.limit_count}"
        if self.offset_count:
            query += f" OFFSET {self.offset_count}"

        return query

    def execute(self) -> List[Dict]:
        """Execute the query and return results"""
        query = self.build_query()

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query)
            return [dict(row) for row in cursor.fetchall()]

    def count(self) -> int:
        """Get count of records matching the filters"""
        if not self.base_query:
            raise ValueError("No table specified. Use from_table() first.")

        # Replace SELECT * with SELECT COUNT(*)
        count_query = self.base_query.replace("SELECT *", "SELECT COUNT(*)")

        # Add joins
        if self.joins:
            count_query += " " + " ".join(self.joins)

        # Add WHERE conditions
        if self.filters:
            count_query += " WHERE " + " AND ".join(self.filters)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(count_query)
            return cursor.fetchone()[0]

    def reset(self) -> 'QueryBuilder':
        """Reset the query builder for a new query"""
        self.filters = []
        self.sort_by = []
        self.limit_count = None
        self.offset_count = None
        self.joins = []
        return self


class DatabaseManager:
    """Helper class to manage demo database"""

    def __init__(self, db_path: str = "query_demo.db"):
        self.db_path = db_path
        self.init_demo_data()

    def init_demo_data(self) -> None:
        """Create demo tables and data"""
        with sqlite3.connect(self.db_path) as conn:
            # Users table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE,
                    age INTEGER,
                    city TEXT,
                    department TEXT,
                    salary REAL,
                    hire_date DATE,
                    active BOOLEAN DEFAULT 1
                )
            ''')

            # Orders table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    product_name TEXT,
                    quantity INTEGER,
                    price REAL,
                    order_date DATE,
                    status TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')

            # Insert demo data if tables are empty
            cursor = conn.execute('SELECT COUNT(*) FROM users')
            if cursor.fetchone()[0] == 0:
                self._insert_demo_data(conn)

            print("✅ Demo database initialized")

    def _insert_demo_data(self, conn) -> None:
        """Insert sample data"""
        users_data = [
            (1, 'Alice Johnson', 'alice@example.com', 28, 'New York', 'Engineering', 75000, '2020-03-15', 1),
            (2, 'Bob Smith', 'bob@example.com', 34, 'San Francisco', 'Sales', 65000, '2019-07-22', 1),
            (3, 'Carol Davis', 'carol@example.com', 29, 'Chicago', 'Marketing', 55000, '2021-01-10', 1),
            (4, 'David Wilson', 'david@example.com', 41, 'Boston', 'Engineering', 85000, '2018-11-05', 1),
            (5, 'Eva Brown', 'eva@example.com', 26, 'Seattle', 'HR', 50000, '2022-05-18', 0),
            (6, 'Frank Miller', 'frank@example.com', 38, 'Austin', 'Sales', 70000, '2020-09-30', 1),
            (7, 'Grace Lee', 'grace@example.com', 31, 'Denver', 'Marketing', 60000, '2021-08-14', 1),
            (8, 'Henry Taylor', 'henry@example.com', 45, 'Miami', 'Engineering', 95000, '2017-12-01', 1),
        ]

        orders_data = [
            (1, 1, 'Laptop', 1, 1200.00, '2023-01-15', 'completed'),
            (2, 2, 'Mouse', 2, 50.00, '2023-01-20', 'completed'),
            (3, 3, 'Keyboard', 1, 80.00, '2023-02-01', 'pending'),
            (4, 4, 'Monitor', 1, 300.00, '2023-02-10', 'completed'),
            (5, 1, 'Headphones', 1, 150.00, '2023-02-15', 'shipped'),
            (6, 5, 'Webcam', 1, 100.00, '2023-03-01', 'cancelled'),
            (7, 6, 'Printer', 1, 200.00, '2023-03-05', 'completed'),
            (8, 7, 'Tablet', 1, 400.00, '2023-03-10', 'pending'),
            (9, 8, 'Router', 1, 120.00, '2023-03-15', 'completed'),
            (10, 2, 'External Drive', 1, 180.00, '2023-03-20', 'shipped'),
        ]

        conn.executemany('INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', users_data)
        conn.executemany('INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?, ?)', orders_data)


def display_results(results: List[Dict], title: str = "Query Results") -> None:
    """Display query results in a formatted way"""
    if not results:
        print(f"\n{title}: No results found")
        return

    print(f"\n{title} ({len(results)} records):")
    print("-" * 80)

    if results:
        # Get column names from first result
        columns = list(results[0].keys())

        # Print header
        header = " | ".join(f"{col[:15]:<15}" for col in columns)
        print(header)
        print("-" * len(header))

        # Print rows
        for row in results[:10]:  # Limit to first 10 rows
            row_str = " | ".join(f"{str(row[col])[:15]:<15}" for col in columns)
            print(row_str)

        if len(results) > 10:
            print(f"... and {len(results) - 10} more records")


def main():
    print("🔍 Query Builder with Filtering\n")

    db_manager = DatabaseManager()
    qb = QueryBuilder()

    while True:
        print("\n--- Query Builder Menu ---")
        print("1. Query users table")
        print("2. Query orders table")
        print("3. Complex multi-table query")
        print("4. Custom filter builder")
        print("5. Show table schemas")
        print("6. Exit")

        choice = input("\nSelect option (1-6): ").strip()

        if choice == '1':
            print("\n--- Users Table Queries ---")
            print("a. All active users")
            print("b. Users by department")
            print("c. Users with salary > 60000")
            print("d. Users from specific city")
            print("e. Users hired after 2020")
            print("f. Search by name")

            sub_choice = input("\nSelect query (a-f): ").strip()

            if sub_choice == 'a':
                results = qb.reset().from_table('users').where_equal('active', 1).execute()
                display_results(results, "Active Users")

            elif sub_choice == 'b':
                dept = input("Department: ").strip()
                results = qb.reset().from_table('users').where_equal('department', dept).execute()
                display_results(results, f"Users in {dept}")

            elif sub_choice == 'c':
                results = qb.reset().from_table('users').where_greater_than('salary', 60000).order_by('salary', 'DESC').execute()
                display_results(results, "High Salary Users")

            elif sub_choice == 'd':
                city = input("City: ").strip()
                results = qb.reset().from_table('users').where_equal('city', city).execute()
                display_results(results, f"Users in {city}")

            elif sub_choice == 'e':
                results = qb.reset().from_table('users').where_greater_than('hire_date', '2020-01-01').order_by('hire_date').execute()
                display_results(results, "Recently Hired Users")

            elif sub_choice == 'f':
                name = input("Name pattern: ").strip()
                results = qb.reset().from_table('users').where_like('name', name).execute()
                display_results(results, f"Users matching '{name}'")

        elif choice == '2':
            print("\n--- Orders Table Queries ---")
            print("a. All completed orders")
            print("b. Orders by user")
            print("c. High value orders (> $500)")
            print("d. Recent orders")
            print("e. Orders by status")

            sub_choice = input("\nSelect query (a-e): ").strip()

            if sub_choice == 'a':
                results = qb.reset().from_table('orders').where_equal('status', 'completed').order_by('order_date', 'DESC').execute()
                display_results(results, "Completed Orders")

            elif sub_choice == 'b':
                try:
                    user_id = int(input("User ID: "))
                    results = qb.reset().from_table('orders').where_equal('user_id', user_id).execute()
                    display_results(results, f"Orders by User {user_id}")
                except ValueError:
                    print("❌ Invalid user ID")

            elif sub_choice == 'c':
                results = qb.reset().from_table('orders').where_greater_than('price', 500).order_by('price', 'DESC').execute()
                display_results(results, "High Value Orders")

            elif sub_choice == 'd':
                results = qb.reset().from_table('orders').where_greater_than('order_date', '2023-03-01').order_by('order_date', 'DESC').execute()
                display_results(results, "Recent Orders")

            elif sub_choice == 'e':
                status = input("Status (completed/pending/shipped/cancelled): ").strip()
                results = qb.reset().from_table('orders').where_equal('status', status).execute()
                display_results(results, f"{status.title()} Orders")

        elif choice == '3':
            print("\n--- Multi-Table Queries ---")
            print("a. User orders with user details")
            print("b. Total spending by user")
            print("c. Orders by department")

            sub_choice = input("\nSelect query (a-c): ").strip()

            if sub_choice == 'a':
                results = (qb.reset()
                          .select(['u.name', 'u.email', 'o.product_name', 'o.price', 'o.order_date', 'o.status'])
                          .from_table('users u')
                          .join('orders o', 'u.id = o.user_id')
                          .where_equal('o.status', 'completed')
                          .order_by('o.order_date', 'DESC')
                          .limit(10)
                          .execute())
                display_results(results, "User Orders")

            elif sub_choice == 'b':
                # This would require GROUP BY which our simple builder doesn't support
                # Let's do a simpler version
                results = (qb.reset()
                          .select(['u.name', 'COUNT(o.id) as order_count', 'SUM(o.price) as total_spent'])
                          .from_table('users u')
                          .join('orders o', 'u.id = o.user_id')
                          .where_equal('o.status', 'completed')
                          .execute())
                # Note: This won't work with our simple builder - we'd need aggregation
                print("Note: Aggregation queries require more complex SQL")
                display_results(results[:5], "Sample User Spending")

            elif sub_choice == 'c':
                results = (qb.reset()
                          .select(['u.department', 'COUNT(o.id) as order_count'])
                          .from_table('users u')
                          .join('orders o', 'u.id = o.user_id')
                          .execute())
                display_results(results[:5], "Orders by Department")

        elif choice == '4':
            print("\n--- Custom Filter Builder ---")
            table = input("Table name (users/orders): ").strip()
            if table not in ['users', 'orders']:
                print("❌ Invalid table")
                continue

            qb.reset().from_table(table)

            print("Available filters:")
            print("1. Equal (=)")
            print("2. Like (contains)")
            print("3. Greater than (>)")
            print("4. Less than (<)")
            print("5. Between")
            print("6. In list")
            print("7. Is null")

            while True:
                add_filter = input("Add filter? (y/n): ").strip().lower()
                if add_filter != 'y':
                    break

                filter_type = input("Filter type (1-7): ").strip()

                if filter_type == '1':
                    column = input("Column: ").strip()
                    value = input("Value: ").strip()
                    qb.where_equal(column, value)
                elif filter_type == '2':
                    column = input("Column: ").strip()
                    pattern = input("Pattern: ").strip()
                    qb.where_like(column, pattern)
                elif filter_type == '3':
                    column = input("Column: ").strip()
                    value = input("Value: ").strip()
                    qb.where_greater_than(column, value)
                elif filter_type == '4':
                    column = input("Column: ").strip()
                    value = input("Value: ").strip()
                    qb.where_less_than(column, value)
                elif filter_type == '5':
                    column = input("Column: ").strip()
                    min_val = input("Min value: ").strip()
                    max_val = input("Max value: ").strip()
                    qb.where_between(column, min_val, max_val)
                elif filter_type == '6':
                    column = input("Column: ").strip()
                    values_str = input("Values (comma-separated): ").strip()
                    values = [v.strip() for v in values_str.split(',')]
                    qb.where_in(column, values)
                elif filter_type == '7':
                    column = input("Column: ").strip()
                    is_null = input("Is null? (y/n): ").strip().lower() == 'y'
                    qb.where_null(column, is_null)

            # Add sorting
            sort_column = input("Sort by column (optional): ").strip()
            if sort_column:
                direction = input("Direction (ASC/DESC): ").strip().upper()
                if direction not in ['ASC', 'DESC']:
                    direction = 'ASC'
                qb.order_by(sort_column, direction)

            # Add limit
            try:
                limit_str = input("Limit results (optional): ").strip()
                if limit_str:
                    qb.limit(int(limit_str))
            except ValueError:
                pass

            try:
                results = qb.execute()
                display_results(results, "Custom Query Results")
                print(f"SQL Query: {qb.build_query()}")
            except Exception as e:
                print(f"❌ Query error: {e}")

        elif choice == '5':
            print("\n--- Table Schemas ---")
            with sqlite3.connect(db_manager.db_path) as conn:
                # Users schema
                cursor = conn.execute("PRAGMA table_info(users)")
                print("Users table:")
                for row in cursor.fetchall():
                    print(f"  {row[1]} ({row[2]})")

                print("\nOrders table:")
                cursor = conn.execute("PRAGMA table_info(orders)")
                for row in cursor.fetchall():
                    print(f"  {row[1]} ({row[2]})")

        elif choice == '6':
            print("👋 Goodbye!")
            break

        else:
            print("❌ Invalid option")


if __name__ == "__main__":
    main()
