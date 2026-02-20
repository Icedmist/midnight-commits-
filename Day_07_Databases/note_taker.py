"""
Simple Note-Taking App with Database
A SQLite-based note management system with categories and search
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional


class NoteTaker:
    """SQLite-based note-taking application"""

    def __init__(self, db_path: str = "notes.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self) -> None:
        """Initialize the database and create notes table"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT,
                    category TEXT DEFAULT 'General',
                    tags TEXT,  -- comma-separated tags
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    color TEXT DEFAULT '#FFFFFF',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            print("✅ Notes database initialized")

    def add_note(self, title: str, content: str = "", category: str = "General",
                tags: List[str] = None) -> bool:
        """Add a new note"""
        try:
            tags_str = ','.join(tags) if tags else ""
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO notes (title, content, category, tags)
                    VALUES (?, ?, ?, ?)
                ''', (title, content, category, tags_str))
                print(f"✅ Note '{title}' added successfully")
                return True
        except Exception as e:
            print(f"❌ Error adding note: {e}")
            return False

    def get_note(self, note_id: int) -> Optional[Dict]:
        """Get note by ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('SELECT * FROM notes WHERE id = ?', (note_id,))
            row = cursor.fetchone()
            if row:
                note = dict(row)
                note['tags'] = note['tags'].split(',') if note['tags'] else []
                return note
            return None

    def search_notes(self, query: str, category: str = None) -> List[Dict]:
        """Search notes by title, content, or tags"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            sql = '''
                SELECT * FROM notes
                WHERE (title LIKE ? OR content LIKE ? OR tags LIKE ?)
            '''
            params = [f'%{query}%', f'%{query}%', f'%{query}%']

            if category:
                sql += ' AND category = ?'
                params.append(category)

            sql += ' ORDER BY updated_at DESC'

            cursor = conn.execute(sql, params)
            notes = []
            for row in cursor.fetchall():
                note = dict(row)
                note['tags'] = note['tags'].split(',') if note['tags'] else []
                notes.append(note)
            return notes

    def update_note(self, note_id: int, **updates) -> bool:
        """Update note information"""
        if not updates:
            return False

        # Handle tags list
        if 'tags' in updates and isinstance(updates['tags'], list):
            updates['tags'] = ','.join(updates['tags'])

        set_clause = ', '.join(f'{key} = ?' for key in updates.keys())
        values = list(updates.values()) + [note_id]

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(f'''
                    UPDATE notes
                    SET {set_clause}, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', values)
                if conn.total_changes > 0:
                    print(f"✅ Note {note_id} updated")
                    return True
                else:
                    print(f"❌ Note {note_id} not found")
                    return False
        except Exception as e:
            print(f"❌ Error updating note: {e}")
            return False

    def delete_note(self, note_id: int) -> bool:
        """Delete a note"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('DELETE FROM notes WHERE id = ?', (note_id,))
                if conn.total_changes > 0:
                    print(f"✅ Note {note_id} deleted")
                    return True
                else:
                    print(f"❌ Note {note_id} not found")
                    return False
        except Exception as e:
            print(f"❌ Error deleting note: {e}")
            return False

    def list_notes(self, category: str = None, limit: int = 20) -> List[Dict]:
        """List notes, optionally filtered by category"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            sql = 'SELECT id, title, category, created_at FROM notes'
            params = []

            if category:
                sql += ' WHERE category = ?'
                params.append(category)

            sql += ' ORDER BY updated_at DESC LIMIT ?'
            params.append(limit)

            cursor = conn.execute(sql, params)
            notes = []
            for row in cursor.fetchall():
                note = dict(row)
                notes.append(note)
            return notes

    def get_categories(self) -> List[str]:
        """Get all unique categories"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('SELECT DISTINCT category FROM notes ORDER BY category')
            return [row[0] for row in cursor.fetchall()]

    def get_note_stats(self) -> Dict:
        """Get note statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('SELECT COUNT(*) FROM notes')
            total_notes = cursor.fetchone()[0]

            cursor = conn.execute('SELECT COUNT(DISTINCT category) FROM notes')
            total_categories = cursor.fetchone()[0]

            cursor = conn.execute('SELECT category, COUNT(*) as count FROM notes GROUP BY category ORDER BY count DESC LIMIT 1')
            most_used = cursor.fetchone()
            most_used_category = most_used[0] if most_used else "None"

            return {
                'total_notes': total_notes,
                'total_categories': total_categories,
                'most_used_category': most_used_category
            }


def display_note(note: Dict) -> None:
    """Display note information"""
    print(f"\n📝 Note #{note['id']}: {note['title']}")
    print(f"Category: {note['category']}")
    print(f"Tags: {', '.join(note['tags']) if note['tags'] else 'None'}")
    print(f"Created: {note['created_at']}")
    print(f"Updated: {note['updated_at']}")
    print(f"\nContent:\n{note['content']}")
    print("-" * 50)


def main():
    print("📝 Simple Note-Taking App\n")

    noter = NoteTaker()

    while True:
        print("\n--- Note Taker Menu ---")
        print("1. Add note")
        print("2. Search notes")
        print("3. List notes")
        print("4. View note details")
        print("5. Update note")
        print("6. Delete note")
        print("7. Show statistics")
        print("8. Exit")

        choice = input("\nSelect option (1-8): ").strip()

        if choice == '1':
            title = input("Title: ").strip()
            if not title:
                print("❌ Title is required")
                continue

            content = input("Content: ").strip()
            category = input("Category (default: General): ").strip() or "General"

            tags_input = input("Tags (comma-separated, optional): ").strip()
            tags = [tag.strip() for tag in tags_input.split(',')] if tags_input else None

            noter.add_note(title, content, category, tags)

        elif choice == '2':
            query = input("Search query: ").strip()
            if query:
                category = input("Filter by category (optional): ").strip() or None
                results = noter.search_notes(query, category)
                if results:
                    print(f"\n✅ Found {len(results)} notes:")
                    for note in results:
                        print(f"  {note['id']}: {note['title']} ({note['category']})")
                else:
                    print("❌ No notes found")

        elif choice == '3':
            categories = noter.get_categories()
            print(f"\n📂 Categories: {', '.join(categories) if categories else 'None'}")

            category = input("Filter by category (optional): ").strip() or None
            notes = noter.list_notes(category)
            if notes:
                print(f"\n📋 Notes ({len(notes)}):")
                for note in notes:
                    print(f"  {note['id']}: {note['title']} [{note['category']}]")
            else:
                print("❌ No notes found")

        elif choice == '4':
            try:
                note_id = int(input("Note ID: "))
                note = noter.get_note(note_id)
                if note:
                    display_note(note)
                else:
                    print("❌ Note not found")
            except ValueError:
                print("❌ Invalid ID")

        elif choice == '5':
            try:
                note_id = int(input("Note ID: "))
                note = noter.get_note(note_id)
                if not note:
                    print("❌ Note not found")
                    continue

                print("Leave fields empty to keep current values:")
                title = input(f"Title [{note['title']}]: ").strip() or note['title']
                content = input(f"Content [{note['content'][:50]}...]: ").strip() or note['content']
                category = input(f"Category [{note['category']}]: ").strip() or note['category']

                current_tags = ', '.join(note['tags']) if note['tags'] else ''
                tags_input = input(f"Tags [{current_tags}]: ").strip()
                if tags_input:
                    tags = [tag.strip() for tag in tags_input.split(',')]
                else:
                    tags = note['tags']

                updates = {}
                if title != note['title']:
                    updates['title'] = title
                if content != note['content']:
                    updates['content'] = content
                if category != note['category']:
                    updates['category'] = category
                if tags != note['tags']:
                    updates['tags'] = tags

                if updates:
                    noter.update_note(note_id, **updates)
                else:
                    print("ℹ️ No changes made")

            except ValueError:
                print("❌ Invalid ID")

        elif choice == '6':
            try:
                note_id = int(input("Note ID to delete: "))
                confirm = input(f"Are you sure you want to delete note {note_id}? (y/N): ").strip().lower()
                if confirm == 'y':
                    noter.delete_note(note_id)
                else:
                    print("❌ Deletion cancelled")
            except ValueError:
                print("❌ Invalid ID")

        elif choice == '7':
            stats = noter.get_note_stats()
            print("\n📊 Note Statistics:")
            print(f"Total notes: {stats['total_notes']}")
            print(f"Categories: {stats['total_categories']}")
            print(f"Most used category: {stats['most_used_category']}")

        elif choice == '8':
            print("👋 Goodbye!")
            break

        else:
            print("❌ Invalid option")


if __name__ == "__main__":
    main()
