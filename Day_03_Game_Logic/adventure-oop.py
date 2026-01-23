class Room:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.exits = {}  # {'north': RoomObject, 'south': RoomObject}
        self.items = []

    def connect(self, direction, room):
        self.exits[direction] = room
        # Auto-connect the reverse direction? Optional, but helpful.
        # reverse_dirs = {'north': 'south', 'south': 'north', 'east': 'west', 'west': 'east'}
        # room.exits[reverse_dirs[direction]] = self 

    def add_item(self, item):
        self.items.append(item)

    def remove_item(self, item_name):
        for item in self.items:
            if item.name.lower() == item_name.lower():
                self.items.remove(item)
                return item
        return None

class Item:
    def __init__(self, name, description, damage=0):
        self.name = name
        self.description = description
        self.damage = damage

class Player:
    def __init__(self, start_room):
        self.current_room = start_room
        self.inventory = []
        self.hp = 100

    def move(self, direction):
        if direction in self.current_room.exits:
            self.current_room = self.current_room.exits[direction]
            print(f"\n📍 You walked to {self.current_room.name}")
            print(self.current_room.description)
        else:
            print("❌ You can't go that way.")

    def look(self):
        print(f"\n👀 {self.current_room.name}: {self.current_room.description}")
        if self.current_room.items:
            visible_items = ", ".join([i.name for i in self.current_room.items])
            print(f"You see: {visible_items}")
        else:
            print("The room is empty.")

    def take(self, item_name):
        item = self.current_room.remove_item(item_name)
        if item:
            self.inventory.append(item)
            print(f"✅ Picked up {item.name}")
        else:
            print("That isn't here.")

# --- Setup the World ---
def create_world():
    # 1. Create Rooms
    hall = Room("Great Hall", "A large, echoing stone hall.")
    kitchen = Room("Kitchen", "It smells of rotten food.")
    garden = Room("Garden", "Overgrown with thorny vines.")

    # 2. Connect Rooms
    hall.connect('south', kitchen)
    kitchen.connect('north', hall)
    hall.connect('east', garden)
    garden.connect('west', hall)

    # 3. Add Items
    sword = Item("Sword", "A rusty blade.", damage=10)
    key = Item("Key", "A heavy iron key.")
    
    garden.add_item(sword)
    kitchen.add_item(key)

    return hall # Return starting room

def main():
    start_room = create_world()
    player = Player(start_room)
    
    print("--- OOP Adventure Engine ---")
    player.look()

    while True:
        cmd = input("\n> ").lower().split()
        if not cmd: continue

        action = cmd[0]

        if action == "quit": break
        elif action == "look": player.look()
        elif action == "go" and len(cmd) > 1: player.move(cmd[1])
        elif action == "take" and len(cmd) > 1: player.take(cmd[1])
        elif action == "inv": 
            print(f"🎒 {[i.name for i in player.inventory]}")
        else: print("Unknown command.")

if __name__ == "__main__":
    main()