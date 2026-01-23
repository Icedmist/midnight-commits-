import sys

# Global list to hold tasks
tasks = []

def show_menu():
    print("\n--- TO-DO LIST ---")
    print("1. View Tasks")
    print("2. Add Task")
    print("3. Remove Task")
    print("4. Exit")

def view_tasks():
    if not tasks:
        print("\nYour list is empty.")
    else:
        print("\nYour Tasks:")
        # enumerate gives us both the index (i) and the item (task)
        for i, task in enumerate(tasks, start=1):
            print(f"{i}. {task}")

def add_task():
    task = input("Enter task description: ")
    tasks.append(task)
    print(f"Added: '{task}'")

def remove_task():
    view_tasks()
    if not tasks:
        return

    try:
        num = int(input("\nEnter number to remove: "))
        # Convert user number (1-based) to list index (0-based)
        if 1 <= num <= len(tasks):
            removed = tasks.pop(num - 1)
            print(f"Removed: '{removed}'")
        else:
            print("Invalid number.")
    except ValueError:
        print("Please enter a valid number.")

def main():
    while True:
        show_menu()
        choice = input("Choose (1-4): ")

        if choice == '1':
            view_tasks()
        elif choice == '2':
            add_task()
        elif choice == '3':
            remove_task()
        elif choice == '4':
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()