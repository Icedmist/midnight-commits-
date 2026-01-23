# a simple adventure game to kill monsters, from the wheelers house, stranger things S5
def main():
    # The Map: A dictionary of dictionaries
    rooms = {
        'Hall': {
            'south': 'Kitchen',
            'east': 'Dining Room',
            'item': 'Key'
        },
        'Kitchen': {
            'north': 'Hall',
            'item': 'Monster'
        },
        'Dining Room': {
            'west': 'Hall',
            'south': 'Garden',
            'item': 'Potion'
        },
        'Garden': {
            'north': 'Dining Room',
            'item': 'Sword' # needed to kill monster
        }
    }

    current_room = 'Hall'
    inventory = []

    print("--- Dungeon Explorer ---")
    print("Move: go [direction] | Get: get [item] | Quit: quit")

    while True:
        print(f"\n📍 You are in the {current_room}")
        print(f"🎒 Inventory: {inventory}")
        
        # Check for item in the room
        room_item = rooms[current_room].get('item')
        if room_item:
            print(f"👁️ You see a {room_item} here.")
            
        # Monster Event Logic
        if 'Monster' in str(room_item) and 'Sword' not in inventory:
            print("\n👹 A Monster attacks you! You have no Sword...")
            print("💀 YOU DIED.")
            break
        elif 'Monster' in str(room_item) and 'Sword' in inventory:
            print("\n⚔️ You use the Sword to defeat the Monster!")
            del rooms[current_room]['item'] # Remove monster
            print("You found the treasure! YOU WIN! 🏆")
            break

        # Get User Input
        move = input("> ").lower().split()

        if not move:
            continue

        action = move[0] # 'go' or 'get'

        if action == 'quit':
            print("Thanks for playing!")
            break

        if action == 'go':
            if len(move) < 2:
                print("Go where?")
                continue
            
            direction = move[1]
            if direction in rooms[current_room]:
                current_room = rooms[current_room][direction]
            else:
                print("❌ You can't go that way.")

        elif action == 'get':
            if room_item and len(move) > 1 and move[1] == room_item.lower():
                print(f"✅ Picked up {room_item}")
                inventory.append(room_item)
                del rooms[current_room]['item'] # Remove item from room
            else:
                print("Can't get that.")
        
        else:
            print("I don't understand that command.")

if __name__ == "__main__":
    main()