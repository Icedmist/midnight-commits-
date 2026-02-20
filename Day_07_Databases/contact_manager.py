"""
SQLite Contact Manager
A simple contact management system using SQLite database
"""

import sqlite3
import os
from typing import List, Dict, Optional


class ContactManager:
    """SQLite-based contact management system"""

    def __init__(self, db_path: str = "contacts.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self) -> None:
        """Initialize the database and create contacts table"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS contacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE,
                    phone TEXT,
                    address TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            print("✅ Database initialized")

    def add_contact(self, name: str, email: str = None, phone: str = None,
                   address: str = None, notes: str = None) -> bool:
        """Add a new contact"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO contacts (name, email, phone, address, notes)
                    VALUES (?, ?, ?, ?, ?)
                ''', (name, email, phone, address, notes))
                print(f"✅ Contact '{name}' added successfully")
                return True
        except sqlite3.IntegrityError:
            print(f"❌ Email '{email}' already exists")
            return False
        except Exception as e:
            print(f"❌ Error adding contact: {e}")
            return False

    def get_contact(self, contact_id: int) -> Optional[Dict]:
        """Get contact by ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('SELECT * FROM contacts WHERE id = ?', (contact_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def search_contacts(self, query: str) -> List[Dict]:
        """Search contacts by name, email, or phone"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT * FROM contacts
                WHERE name LIKE ? OR email LIKE ? OR phone LIKE ?
                ORDER BY name
            ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
            return [dict(row) for row in cursor.fetchall()]

    def update_contact(self, contact_id: int, **updates) -> bool:
        """Update contact information"""
        if not updates:
            return False

        set_clause = ', '.join(f'{key} = ?' for key in updates.keys())
        values = list(updates.values()) + [contact_id]

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(f'''
                    UPDATE contacts
                    SET {set_clause}, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', values)
                if conn.total_changes > 0:
                    print(f"✅ Contact {contact_id} updated")
                    return True
                else:
                    print(f"❌ Contact {contact_id} not found")
                    return False
        except Exception as e:
            print(f"❌ Error updating contact: {e}")
            return False

    def delete_contact(self, contact_id: int) -> bool:
        """Delete a contact"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('DELETE FROM contacts WHERE id = ?', (contact_id,))
                if conn.total_changes > 0:
                    print(f"✅ Contact {contact_id} deleted")
                    return True
                else:
                    print(f"❌ Contact {contact_id} not found")
                    return False
        except Exception as e:
            print(f"❌ Error deleting contact: {e}")
            return False

    def list_contacts(self, limit: int = 50) -> List[Dict]:
        """List all contacts"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT id, name, email, phone
                FROM contacts
                ORDER BY name
                LIMIT ?
            ''', (limit,))
            return [dict(row) for row in cursor.fetchall()]

    def get_stats(self) -> Dict:
        """Get database statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('SELECT COUNT(*) as total FROM contacts')
            total = cursor.fetchone()[0]

            cursor = conn.execute('SELECT COUNT(*) FROM contacts WHERE email IS NOT NULL')
            with_email = cursor.fetchone()[0]

            cursor = conn.execute('SELECT COUNT(*) FROM contacts WHERE phone IS NOT NULL')
            with_phone = cursor.fetchone()[0]

            return {
                'total_contacts': total,
                'with_email': with_email,
                'with_phone': with_phone,
                'db_size_kb': os.path.getsize(self.db_path) / 1024 if os.path.exists(self.db_path) else 0
            }


def display_contact(contact: Dict) -> None:
    """Display contact information"""
    print(f"\n📇 Contact #{contact['id']}")
    print(f"Name: {contact['name']}")
    print(f"Email: {contact.get('email', 'N/A')}")
    print(f"Phone: {contact.get('phone', 'N/A')}")
    print(f"Address: {contact.get('address', 'N/A')}")
    print(f"Notes: {contact.get('notes', 'N/A')}")
    print(f"Created: {contact.get('created_at', 'N/A')}")


def main():
    print("📱 SQLite Contact Manager\n")

    manager = ContactManager()

    while True:
        print("\n--- Contact Manager Menu ---")
        print("1. Add contact")
        print("2. Search contacts")
        print("3. List all contacts")
        print("4. View contact details")
        print("5. Update contact")
        print("6. Delete contact")
        print("7. Show statistics")
        print("8. Exit")

        choice = input("\nSelect option (1-8): ").strip()

        if choice == '1':
            name = input("Name: ").strip()
            if not name:
                print("❌ Name is required")
                continue
            email = input("Email (optional): ").strip() or None
            phone = input("Phone (optional): ").strip() or None
            address = input("Address (optional): ").strip() or None
            notes = input("Notes (optional): ").strip() or None
            manager.add_contact(name, email, phone, address, notes)

        elif choice == '2':
            query = input("Search query: ").strip()
            if query:
                results = manager.search_contacts(query)
                if results:
                    print(f"\n✅ Found {len(results)} contacts:")
                    for contact in results:
                        print(f"  {contact['id']}: {contact['name']} - {contact.get('email', 'No email')}")
                else:
                    print("❌ No contacts found")

        elif choice == '3':
            contacts = manager.list_contacts()
            if contacts:
                print(f"\n📋 All Contacts ({len(contacts)}):")
                for contact in contacts:
                    print(f"  {contact['id']}: {contact['name']}")
            else:
                print("❌ No contacts in database")

        elif choice == '4':
            try:
                contact_id = int(input("Contact ID: "))
                contact = manager.get_contact(contact_id)
                if contact:
                    display_contact(contact)
                else:
                    print("❌ Contact not found")
            except ValueError:
                print("❌ Invalid ID")

        elif choice == '5':
            try:
                contact_id = int(input("Contact ID: "))
                contact = manager.get_contact(contact_id)
                if not contact:
                    print("❌ Contact not found")
                    continue

                print("Leave fields empty to keep current values:")
                name = input(f"Name [{contact['name']}]: ").strip() or contact['name']
                email = input(f"Email [{contact.get('email', '')}]: ").strip() or contact.get('email')
                phone = input(f"Phone [{contact.get('phone', '')}]: ").strip() or contact.get('phone')
                address = input(f"Address [{contact.get('address', '')}]: ").strip() or contact.get('address')
                notes = input(f"Notes [{contact.get('notes', '')}]: ").strip() or contact.get('notes')

                updates = {}
                if name != contact['name']:
                    updates['name'] = name
                if email != contact.get('email'):
                    updates['email'] = email
                if phone != contact.get('phone'):
                    updates['phone'] = phone
                if address != contact.get('address'):
                    updates['address'] = address
                if notes != contact.get('notes'):
                    updates['notes'] = notes

                if updates:
                    manager.update_contact(contact_id, **updates)
                else:
                    print("ℹ️ No changes made")

            except ValueError:
                print("❌ Invalid ID")

        elif choice == '6':
            try:
                contact_id = int(input("Contact ID to delete: "))
                confirm = input(f"Are you sure you want to delete contact {contact_id}? (y/N): ").strip().lower()
                if confirm == 'y':
                    manager.delete_contact(contact_id)
                else:
                    print("❌ Deletion cancelled")
            except ValueError:
                print("❌ Invalid ID")

        elif choice == '7':
            stats = manager.get_stats()
            print("\n📊 Database Statistics:")
            print(f"Total contacts: {stats['total_contacts']}")
            print(f"With email: {stats['with_email']}")
            print(f"With phone: {stats['with_phone']}")
            print(f"Database size: {stats['db_size_kb']:.1f} KB")

        elif choice == '8':
            print("👋 Goodbye!")
            break

        else:
            print("❌ Invalid option")


if __name__ == "__main__":
    main()
